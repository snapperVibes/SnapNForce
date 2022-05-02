# """ Common functions made from the primitives found in lib"""
# fmt: off
import re
from functools import partial
from typing import Optional

from bs4 import NavigableString, Tag
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session

from app import schemas
from app.operations import insert, deactivate, ensure
from app.operations import select
from app.operations._common import GENERAL_LINKED_OBJECT_ROLE, MORTGAGE_LINKED_OBJECT_ROLE
from app.schemas import CogGeneralAndMortgage
from lib import scrape, parse


async def sync_parcel_data(db: Session, parcel_id: str) -> schemas.GeneralAndMortgage:
    _county_data = await get_parcel_data_from_county(parcel_id)
    _cog_tables = get_cog_tables(db, parcel_id)

    out = {GENERAL_LINKED_OBJECT_ROLE: None, MORTGAGE_LINKED_OBJECT_ROLE: None}
    # Todo: we need to ensure the parcel exists before the next stage
    for county, cog, role in zip(
        (_county_data.general,       _county_data.mortgage),
        (_cog_tables.general,        _cog_tables.mortgage),
        (GENERAL_LINKED_OBJECT_ROLE, MORTGAGE_LINKED_OBJECT_ROLE)
    ):
        out[role] = _sync_owner_and_mailing(db, county, cog)

    return schemas.GeneralAndMortgage(
        general=out[GENERAL_LINKED_OBJECT_ROLE],
        mortgage=out[MORTGAGE_LINKED_OBJECT_ROLE]
    )


def _sync_owner_and_mailing(db, county: schemas.OwnerAndMailing, cog: Optional[schemas.CogTables]) -> schemas.OwnerAndMailing:
    # Todo: This is one of the messiest functions in the code. Refactor
    # SYNC MAILING

    # SEE IF THE ADDRESS IS THE SAME
    #  WHILE YOU CHECK, IF THE COG DOES NOT EXIST, WRITE IT
    #  IF THEY ARE THE SAME, YOU DO NOT NEED TO DISABLE THE OLD ADDRESS
    #
    #  IF THEY ARE THE SAME, CONTINUE
    m = county.mailing
    city_state_zip = None
    street=None
    address = None
    if m is not None:
        city_state_zip = ensure.city_state_zip(db, city=m.last.city, state=m.last.state, zip_=m.last.zip)
        street = ensure.street(db, city_state_zip_id=city_state_zip.id, street_name=m.delivery.street, is_pobox=m.delivery.is_pobox)
        address = ensure.address(db, street_id=street.streetid, number=m.delivery.number, attn=m.delivery.attn, secondary=m.delivery.secondary)

    # Todo: The insert doesn't work yet because we need the muni. I'll figure it out later

    address_is_same: bool
    if cog is not None:
        cog_line_1 = schemas.DeliveryAddressLine(is_pobox=cog.street.pobox, attn=cog.address.attention, number=cog.address.bldgno, street=cog.street.name)
        cog_line_2 = schemas.LastLine(city=cog.city_state_zip.city, state=cog.city_state_zip.state_abbr, zip=cog.city_state_zip.zip_code)
        address_is_same = all(
            (x == y)
            for x, y in zip([m.delivery, m.last], [cog_line_1, cog_line_2])
        )
    else:
        address_is_same = True

    if not address_is_same:
        if address is not None:
            deactivate.parcel_mailing_address(db, parcel_key=cog.parcel.parcelkey, address_id=address.addressid)
            insert.parcel_mailing(
                db, parcel_key=cog.parcel.parcelkey, address_id=address.addressid, role=GENERAL_LINKED_OBJECT_ROLE
            )

    # SYNC OWNER
    ############################
    o = county.owner
    # human-ify the cog owner
    # Todo: make this more readable
    if (not (cog is None)) and (not (cog.human is None)) and (not all(
            (x == y)
            for x, y in zip([o.name, o.is_multi_entity], [cog.human.name, cog.human.multihuman])
    )):
        deactivate.human_mailing_address(
            db, human_id=cog.human_address.humanmailing_humanid, mailing_id=cog.human_address.humanmailing_addressid
        )
    # TODO: THIS WILL FAIL IN DISASTROUS WAYS IF TWO PEOPLE HAVE THE SAME NAME.
    #  TALK TO ERIC AND FIGURE IT OUT
    human = select._human(db, name=o.name, is_multi_entity=o.is_multi_entity)
    if not human:
        human = insert.human(db, name=o.name, is_multi_entity=o.is_multi_entity)
        if address is not None:
            insert.human_mailing(db, human_id=human.humanid, mailing_id=address.addressid)

    mailing = None
    if city_state_zip is not None:
        mailing = schemas.Mailing(
            delivery=schemas.DeliveryAddressLine(is_pobox=street.pobox, attn=address.attention, number=address.bldgno, street=street.name),
            last=schemas.LastLine(city=city_state_zip.city, state=city_state_zip.state_abbr, zip=city_state_zip.zip_code)
        )

    owner = None
    try:
        owner = schemas.Owner(name=human.name, is_multi_entity=human.multihuman)
    except AttributeError:
        breakpoint()
    return schemas.OwnerAndMailing(owner=owner, mailing=mailing)


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
        #  but I haven't thought to prove it yet
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


def get_cog_tables(db, parcel_id) -> CogGeneralAndMortgage:
    all_addresses = []
    parcel = select.parcel(db, parcel_id)
    parcel_addresses = select.parcel_mailing_addresses(db, parcel.parcelkey)
    for (parcel_address,) in parcel_addresses:
        address = select.address(db, parcel_address.mailingaddress_addressid)
        street = select.street(db, address.street_streetid)
        city_state_zip = select.city_state_zip(db, street.citystatezip_cszipid)
        try:
            human_address = select.human_mailing_address(db, address.addressid)
            human = select.human(db, human_address.humanmailing_humanid)
        except NoResultFound:
            human_address = human = None
        tables = schemas.CogTables(
            parcel=parcel,
            address=address,
            parcel_address=parcel_address,
            street=street,
            city_state_zip=city_state_zip,
            human=human,
            human_address=human_address,
        )
        all_addresses.append(tables)
    return schemas.CogGeneralAndMortgage(
        general=_match_general(all_addresses),
        mortgage=_match_mortgage(all_addresses),
    )


def _match_number(num_to_match: int, owners_and_mailings: list[schemas.CogTables]):
    for x in owners_and_mailings:
        if x.parcel_address.linkedobjectrole_lorid == num_to_match:
            return x
    return None


_match_general = partial(_match_number, GENERAL_LINKED_OBJECT_ROLE)
_match_mortgage = partial(_match_number, MORTGAGE_LINKED_OBJECT_ROLE)
