# """ Common functions made from the primitives found in lib"""
# fmt: off
import re
from typing import Optional

import sqlmodel
from bs4 import NavigableString, Tag
from sqlmodel import Session

from app import schemas, orm
from app.constants import LinkedObjectRole, _AddressAndHumanRoles
from app.logging import logger
from app.operations import select, deactivate, insert, select_or_insert
from lib import scrape, parse


async def sync_parcel_data(db: Session, parcel_id: str) -> schemas.GeneralAndMortgage:
    _county_data = await get_parcel_data_from_county(parcel_id)

    general_owner_and_mailing = None
    mortgage_owner_and_mailing = None

    # todo: somehow get muni_municode filled in with _county_data, otherwise the insert doesn't work
    model_parcel = orm.Parcel(parcelidcnty=parcel_id)
    parcel = select.parcel(db, model_parcel)
    parcel = parcel if parcel is not None else insert.parcel(db, model_parcel)

    data: schemas.OwnerAndMailing
    linked_object_roles: _AddressAndHumanRoles  # just a typehint because my editor couldn't figure out the correct type
    for data, linked_object_roles in zip(
        (_county_data.general, _county_data.mortgage),
        (LinkedObjectRole.general_roles, LinkedObjectRole.mortgage_roles)
    ):
        if data.mailing:
            model_city_state_zip = orm.MailingCityStateZip(
                zip_code=data.mailing.last.zip,
                state_abbr=data.mailing.last.state,
                city=data.mailing.last.city
            )
            city_state_zip = select_or_insert.city_state_zip(db, model_city_state_zip)

            model_street = orm.MailingStreet(
                name=data.mailing.delivery.street,
                pobox=data.mailing.delivery.is_pobox,
                # relationships
                citystatezip=city_state_zip
            )
            street = select_or_insert.street(db, model_street)

            model_address = orm.MailingAddress(
                bldgno=data.mailing.delivery.number,
                attention=data.mailing.delivery.attn,
                secondary=data.mailing.delivery.secondary,
                # relationships
                street=street
            )
            address = select_or_insert.address(db, model_address)
        else:
            city_state_zip = street = address = None

        if data.owner:
            model_human = orm.Human(
                name=data.owner.name,
                multihuman=data.owner.is_multi_entity,
                # businessentity=None,
            )
            human = select_or_insert.human(db, model_human)
        else:
            human = None

        # Todo: Let's write some wet code and fix it latter
        # todo: remove unnecessary database calls

        if address:
            _select_existing_addresses_linked_to_parcel = sqlmodel.select(
                orm.ParcelMailingAddress
            ).where(
                orm.ParcelMailingAddress.parcel_parcelkey == parcel.parcelkey,
                orm.ParcelMailingAddress.linkedobjectrole_lorid == linked_object_roles.address,
                orm.ParcelMailingAddress.mailingaddress_addressid != address.addressid,
                orm.ParcelMailingAddress.deactivatedts == None
            )
            non_current_linked_parcels_and_addresses = db.exec(_select_existing_addresses_linked_to_parcel).all()
            for _model_linked_parcel_and_address in non_current_linked_parcels_and_addresses:
                deactivate.linking_model(db, _model_linked_parcel_and_address)
            model_linked_parcel_and_address = orm.ParcelMailingAddress(
                parcel=parcel, mailingaddress=address, linkedobjectrole_lorid=linked_object_roles.address
            )
            linked_parcel_and_address = select_or_insert.linked_parcel_and_address(db, model_linked_parcel_and_address)

        if human:
            _select_existing_linked_humans_and_addresses = sqlmodel.select(orm.HumanMailingAddress).where(
                orm.HumanMailingAddress.humanmailing_humanid == human.humanid,
                orm.HumanMailingAddress.linkedobjectrole_lorid == linked_object_roles.human,
                orm.HumanMailingAddress.deactivatedts == None
            )
            existing_linked_humans_and_addresses = db.exec(_select_existing_linked_humans_and_addresses).all()
            for _model_human in existing_linked_humans_and_addresses:
                if _model_human.humanmailing_humanid != human.humanid:
                    deactivate.linking_model(db, _model_human)
            model_linked_human_and_address = orm.HumanMailingAddress(
                human=human, mailingaddress=address, linkedobjectrole_lorid=linked_object_roles.human
            )
            linked_human_and_mailing_address = select_or_insert.linked_human_and_address(db, model_linked_human_and_address)

        if human:
            _select_existing_linked_humans_and_parcels = sqlmodel.select(orm.HumanParcel).where(
                orm.HumanParcel.parcel_parcelkey == parcel.parcelkey,
                orm.HumanParcel.linkedobjectrole_lorid == LinkedObjectRole.CURRENT_OWNER,
                orm.HumanParcel.human_humanid != human.humanid,
                orm.HumanParcel.deactivatedts == None,
            )
            existing_linked_humans_and_parcels = db.exec(_select_existing_linked_humans_and_parcels).all()
            for _model_linked_human_and_parcel in existing_linked_humans_and_parcels:
                if _model_linked_human_and_parcel.human_humanid != human.humanid:
                    deactivate.linking_model(db, _model_linked_human_and_parcel)
                    _model_linked_human_and_parcel_as_former_owner = orm.HumanParcel(
                        human=human, parcel=parcel, linkedobjectrole_lorid=LinkedObjectRole.FORMER_OWNER
                    )
                    db.add(_model_linked_human_and_parcel_as_former_owner)
            model_linked_human_and_parcel = orm.HumanParcel(
                human=human, parcel=parcel, linkedobjectrole_lorid=LinkedObjectRole.CURRENT_OWNER
            )
            linked_human_and_parcel = select_or_insert.linked_human_and_parcel(db, model_linked_human_and_parcel)


        # Ok, now time to re-serialize everything
        owner = schemas.Owner(
            name=human.name,
            is_multientity=human.multihuman
        ) if not (human is None) else None
        mailing = schemas.Mailing(
            delivery=schemas.DeliveryAddressLine(
                is_pobox=street.pobox if not street is None else None,
                attn=address.attention if not address is None else None,
                number=address.bldgno if not address is None else None,
                street=street.name if not street is None else None,
                secondary=address.secondary if not address is None else None,
            ),
            last=schemas.LastLine(
                city=city_state_zip.city,
                state=city_state_zip.state_abbr,
                zip=city_state_zip.zip_code
            )
        ) if not city_state_zip is None else None
        owners_and_mailing = schemas.OwnerAndMailing(
            owner=owner,
            mailing=mailing
        )
        if linked_object_roles.human == LinkedObjectRole.general_roles.human:
            general_owner_and_mailing = owners_and_mailing
        elif linked_object_roles.human == LinkedObjectRole.mortgage_roles.human:
            mortgage_owner_and_mailing = owners_and_mailing
        else:
            raise RuntimeError("failed sanity check")

    out = schemas.GeneralAndMortgage(
        general=general_owner_and_mailing,
        mortgage=mortgage_owner_and_mailing,
    )
    logger.debug("Synced parcel", parcel_id=parcel_id, result=out)
    return out













# async def sync_parcel_data(db: Session, parcel_id: str) -> schemas.GeneralAndMortgage:
#     _county_data = await get_parcel_data_from_county(parcel_id)
#     _cog_tables = get_cog_tables(db, parcel_id)
#
#     out = {"general": None, "tax": None}
#     for county, cog, address_and_human_roles in zip(
#         (_county_data.general, _county_data.mortgage),
#         (_cog_tables.general, _cog_tables.mortgage),
#         (LinkedObjectRole.general_roles, LinkedObjectRole.mortgage_roles),
#     ):
#         out[address_and_human_roles] = _sync_owner_and_mailing(db, county, cog, address_and_human_roles)
#     return schemas.GeneralAndMortgage(
#         general=out[LinkedObjectRole.general_roles],
#         mortgage=out[LinkedObjectRole.mortgage_roles]
#     )
#
#
# def _sync_owner_and_mailing(
#         db,
#         county_data: schemas.OwnerAndMailing,
#         cog_tables: Optional[schemas.CogTables],
#         address_and_human_roles: tuple[int, int]
# ) -> schemas.OwnerAndMailing:
#     address_id = cog_tables and cog_tables.address and cog_tables.address.addressid



# def _sync_owner_and_mailing(
#         db,
#         county_data: schemas.OwnerAndMailing,
#         cog_tables: Optional[schemas.CogTables],
#         address_and_human_roles: tuple[int, int]
# ) -> schemas.OwnerAndMailing:
#     address_role, addressee_role = address_and_human_roles
#     cog_data = _cog_tables_to_owner_and_mailing(cog_tables)
#
#     # Todo: ensure parcel here
#     #  Note: make sure to change references to cog_tables.parcel.parcelkey
#     #  to the yet-to-be-created parcel_table.parcelkey
#
#     # Todo: I don't like how this can be reassigned by the following if clause.
#     #  Make it pretty and clean.
#     address_id = cog_tables and cog_tables.address and cog_tables.address.addressid
#     returned_address = county_data.mailing
#     same_address = county_data.mailing == cog_data.mailing
#     if not same_address:
#         if not cog_tables is None:
#             # Deactivate address and linked tables
#             # TODO: Automatic database cascade
#             if cog_tables.parcel_address:
#                 deactivate.parcel_to_address(db, id=cog_tables.parcel_address.linkid)
#             if cog_tables.human_address:
#                 deactivate.human_to_address(db, id=cog_tables.human_address.linkid)
#             if cog_tables.address:
#                 deactivate.address(db, id=cog_tables.address.addressid)
#
#         # Insert new data
#         city_state_zip_table = ensure.city_state_zip(db, city=county_data.mailing.last.city, state=county_data.mailing.last.state, zip_=county_data.mailing.last.zip)
#         street_table = ensure.street(db, city_state_zip_id=city_state_zip_table.id, street_name=county_data.mailing.delivery.street, is_pobox=county_data.mailing.delivery.is_pobox)
#         address_table = ensure.address(db, street_id=street_table.streetid, number=county_data.mailing.delivery.number,  attn=county_data.mailing.delivery.attn, secondary=county_data.mailing.delivery.secondary)
#         # Hmm, should linking go here? Or is it a separate step?
#         link.parcel_to_address(db, parcelkey=cog_tables.parcel.parcelkey, address_id=address_table.addressid, role=address_role)
#         address_id = address_table.addressid
#         returned_address = schemas.Mailing(
#             delivery=schemas.DeliveryAddressLine(
#                 is_pobox=street_table.pobox,
#                 attn=address_table.attention,
#                 number=address_table.bldgno,
#                 street=street_table.name,
#                 secondary=address_table.secondary,
#             ),
#             last=schemas.LastLine(
#                 city=city_state_zip_table.city,
#                 state=city_state_zip_table.state_abbr,
#                 zip=city_state_zip_table.zip_code
#             )
#         )
#
#     human_id = cog_tables and cog_tables.human and cog_tables.human.humanid
#     human_parcel_linked_object_role = cog_tables and cog_tables.human_parcel and cog_tables.human_parcel.linkedobjectrole_lorid
#     if human_parcel_linked_object_role and (human_parcel_linked_object_role != LinkedObjectRole.CURRENT_OWNER):
#         deactivate.human_to_parcel(db, cog_tables.human_parcel.linkid)
#         insert.human_to_parcel(db, )
#
#         orm.HumanParcel
#
#     returned_human = county_data.owner
#     same_human = county_data.owner == cog_data.owner
#     if not same_human:
#         if not cog_tables is None:
#             if cog_tables.human_parcel:
#                 raise RuntimeError("Code is a work in progress. Fix")
#                 # statement = sqlmodel.update(orm.HumanParcel).where(
#                 #     orm.HumanParcel.linkid == cog_tables.human_parcel.linkid,
#                 #     orm.HumanParcel.deactivatedts == None
#                 # ).values(linkedobjectrole_lorid=USER_ID)
#             # if cog_tables.human_parcel:
#             #     deactivate.human_to_parcel(db, id=cog_tables.human_parcel)
#             # # Todo: If we already deactivated human parcel, we may hit the database an unnecessary time here
#             # #  At the time of writing, clean code matters more to me than efficiency.
#             # #  I still would like to remove the unnecessary call
#             # if cog_tables.human_address:
#             #     deactivate.human_to_address(db, id=cog_tables.human_address.linkid)
#             # if cog_tables.human:
#             #     deactivate.human(db, id=cog_tables.human.humanid)
#         human_table = ensure.human(db, name=county_data.owner.name, is_multi_entity=county_data.owner.is_multi_entity)
#         link.human_to_parcel(db, parcelkey=cog_tables.parcel.parcelkey, humanid=human_table.humanid, role=addressee_role)
#         human_id = human_table.humanid
#         returned_human = schemas.Owner(
#             name=human_table.name,
#             is_multi_entity=human_table.multihuman
#         )
#
#     if (not same_human) or (not same_address):
#         link.human_to_address(db, human_id=human_id, address_id=address_id, role=addressee_role)
#
#     return schemas.OwnerAndMailing(
#         owner=returned_human,
#         mailing=returned_address
#     )


#
# def _cog_tables_to_owner_and_mailing(t: schemas.CogTables) -> schemas.OwnerAndMailing:
#     # Todo: long-winded ternary statements are not very Pythonic.
#     #  Break into actual if / else clauses
#     owner = None if (t is None or t.human is None) else schemas.Owner(
#             name=t.human.name,
#             is_multi_entity=t.human.multihuman
#         )
#     mailing = None if (t is None or not t.has_address_tables) else schemas.Mailing(
#         delivery_line=schemas.DeliveryAddressLine(
#             is_pobox=t.street.pobox,
#             attn=t.address.attention,
#             number=t.address.bldgno,
#             street=t.street.name,
#             secondary=t.address.secondary,
#         ),
#         last_line=schemas.LastLine(
#             city=t.city_state_zip.city,
#             state=t.city_state_zip.state_abbr,
#             zip=t.city_state_zip.zip_code
#         )
#     )
#     return schemas.OwnerAndMailing(
#         owner=owner,
#         mailing=mailing
#     )






async def get_parcel_data_from_county(parcel_id: str) -> schemas.GeneralAndMortgage:
    general_data = await get_general_data_from_county(parcel_id)
    tax_data = await get_tax_data_from_county(parcel_id)
    return schemas.GeneralAndMortgage(general=general_data, mortgage=tax_data)


async def get_general_data_from_county(parcel_id: str):
    response = await scrape.general_info(parcel_id)
    response.raise_for_status()
    _owner, _mailing = parse.general_html_content(response.content)
    owner = owner_from_raw(_owner)
    mailing = mailing_from_raw_general(_mailing)
    return schemas.OwnerAndMailing(owner=owner, mailing=mailing)


async def get_tax_data_from_county(parcel_id: str):
    response = await scrape.tax_info(parcel_id)
    response.raise_for_status()
    _owner, _mailing = parse.mortgage_html_content(response.content)
    owner = owner_from_raw(_owner)
    mailing = mailing_from_raw_tax(_mailing)
    return schemas.OwnerAndMailing(owner=owner, mailing=mailing)


def owner_from_raw(data: list[Tag | NavigableString]) -> schemas.Owner:
    owner_list = _clean_tags(data)
    is_multi_entity = False
    if len(owner_list) > 1:
        is_multi_entity = True
    # Owner names often have trailing whitespace
    #  If it isn't stripped away, the dirty_owner != clean_owner check
    #  will always return True.
    dirty_owner = " & ".join(o.strip() for o in owner_list)
    clean_owner = _clean_whitespace(dirty_owner)
    if dirty_owner != clean_owner:  # Todo:
        # Todo: this is most likely duplicate logic,
        #  but I haven't taken time to prove it yet
        is_multi_entity = True
    return schemas.Owner(name=clean_owner, is_multi_entity=is_multi_entity)


def mailing_from_raw_tax(data: list[Tag | NavigableString]) -> Optional[schemas.Mailing]:
    # Todo: these two functions almost certainly belong in lib.parse
    address_list = _clean_tags(data)
    if len(address_list) == 3:
        delivery_line = parse.mortgage_delivery_address_line(address_list[0])
        last_line = parse.mortgage_last_line(city_state=address_list[1], zip=address_list[2])
    elif not address_list:
        return None
    else:
        raise NotImplementedError("I haven't dealt with this yet")
    return schemas.Mailing(delivery=delivery_line, last=last_line)


def mailing_from_raw_general(data: list[Tag | NavigableString]) -> Optional[schemas.Mailing]:
    address_list = _clean_tags(data)
    if len(address_list) == 2:
        delivery_line = parse.general_delivery_address_line(address_list[0])
        last_line = parse.general_city_state_zip(address_list[1])
    elif len(address_list) == 3:
        delivery_line = parse.general_delivery_address_line(address_list[1])
        # "ATTN ", "ATTN: ", "ATTENTION ", "ATTENTION: "
        delivery_line.attn = re.sub(r"ATT(N|ENTION):?\s+", address_list[0], "")
        last_line = parse.general_city_state_zip(address_list[2])
    elif len(address_list) == 0:
        return None
    else:
        raise RuntimeError
    return schemas.Mailing(delivery=delivery_line, last=last_line)


def _clean_tags(content: list[Tag | NavigableString]) -> list[str]:
    return [str(tag) for tag in content if isinstance(tag, NavigableString)]


def _clean_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text)


# def get_cog_tables(db, parcel_id):
#     all_addresses = []
#     parcel = select.parcel(db, parcel_id)
#     if parcel is None:
#         raise RuntimeError
#         # return schemas.CogGeneralAndMortgage(general=None, mortgage=None)
#     parcel_addresses = select.parcel_mailing_addresses(db, parcel.parcelkey)
#     for (parcel_address,) in parcel_addresses:
#         address = select.address(db, parcel_address.mailingaddress_addressid)
#         street = select.street(db, address.street_streetid)
#         city_state_zip = select.city_state_zip(db, street.citystatezip_cszipid)
#         try:
#             human_address = select.human_mailing_address(db, address.addressid)
#             human = select.human(db, human_address.humanmailing_humanid)
#         except NoResultFound:
#             human_address = human = None
#         tables = schemas.CogTables(
#             address=address,
#             parcel_address=parcel_address,
#             street=street,
#             city_state_zip=city_state_zip,
#             human=human,
#             human_address=human_address,
#         )
#         all_addresses.append(tables)
#     # todo: this only works because we are currently lax and accept optional tables
#     #  it would be nice to roll this logic into the above code
#     general = _match_general(all_addresses) or schemas.CogTables()
#     mortgage = _match_mortgage(all_addresses) or schemas.CogTables()
#     general.parcel = mortgage.parcel = parcel
#     return schemas.CogGeneralAndMortgage(general=general, mortgage=mortgage)
#
#
# def _match_number(num_to_match: int, owners_and_mailings: list[schemas.CogTables]):
#     for x in owners_and_mailings:
#         if x.parcel_address.linkedobjectrole_lorid == num_to_match:
#             return x
#     return None
#
#
# _match_general = partial(_match_number, LinkedObjectRole.GENERAL_HUMAN_MAILING_ADDRESS)
# _match_mortgage = partial(_match_number, LinkedObjectRole.MORTGAGE_HUMAN_MAILING_ADDRESS)


# def select_all_parcels_in_municode(db: Session, *, municode: int):
#     return select.parcels_by_municode(db, municode=municode)
def select_all_parcels_in_municode(db, municode):
    statement = sqlmodel.select(orm.Parcel).where(orm.Parcel.muni_municode==municode)
    return db.exec(statement)
