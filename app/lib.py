# """ Common functions made from the primitives found in lib"""
# import re
# from functools import partial
# from typing import Optional
#
# from bs4 import Tag, NavigableString
# from sqlalchemy.exc import NoResultFound
# from sqlmodel import Session
#
# from app import schemas, sync
# from app.operations import select, insert, deactivate
# from app.operations._common import GENERAL_LINKED_OBJECT_ROLE, MORTGAGE_LINKED_OBJECT_ROLE
# from lib import parse, scrape
#
#
from app.schemas


def get_parcel_data_from_county(parcel_id: str) -> schemas.GeneralAndMortgage:
    general_data = get_general_data_from_county(parcel_id)
    tax_data = get_tax_data(parcel_id)
    return schemas.GeneralAndMortgage(general=general_data, mortgage=tax_data)


def get_general_data_from_county
#
#
# def sync_parcel_data(db: Session, *, parcel_id: str):
#     # Get data
#     county = get_parcel_data_from_county(parcel_id)
#     cog = get_parcel_data_from_cog(db, parcel_id)
#
#     sync.general(
#         db,
#         county,
#     )
#
#
#
#     # TODO: IT BREAKS HERE BECUASE I TOOK OUT COG DATAS
#     #  WE NEED TO REEVALUATE HOW THAT DATASTRUCTURE WORKS.
#     cog = get_cog_data(parcel_id)
#     raise RuntimeError
#     # cog = get_cog_general_and_mortgage(db, parcel_id)
#
#     # # Sync data
#     # general = sync.general(
#     #     db,
#     #     parcel_id=parcel_id,
#     #     county=county.general,
#     #     cog=cog.general,
#     # )
#     # mortgage = sync.mortgage(
#     #     db,
#     #     parcel_id=parcel_id,
#     #     county=county.mortgage,
#     #     cog=cog.mortgage,
#     # )
#     # return schemas.CountyGeneralAndMortgage(general=general, mortgage=mortgage)
#
#
# def get_parcel_data_from_cog(db: Session, parcel_id: str):
#     pass
#
#
# # Todo: comment outdated. Left for educational purposes
# # This is HOW you should structure your get_data calls
# #  In practice, debugging was easier without the functional approach exampled here
# # def get_tax_data(parcel_id: str):
# #     return _get_data(
# #         scraper=scrape.tax_info,
# #         parser=parse.general_content,
# #         owner_serilzer=OwnerData.from_raw,
# #         mailing_serilizer=MailingData.from_raw_tax,
# #         parcel_id=parcel_id
# #     )
# # def _get_data(
# #     scraper: Callable[[str], httpx.Response],
# #     parser: Callable[
# #         [AnyStr], tuple[list[Tag | NavigableString], list[Tag | NavigableString]]
# #     ],
# #     owner_serilizer,
# #     mailing_serilizer,
# #     parcel_id: str,
# # ) -> "MailingAddress":
# #     response = scraper(parcel_id)
# #     response.raise_for_status()
# #     _owner, _mailing = parser(response.content)
# #     owner_data = owner_serilizer(_owner)
# #     mailing_data = mailing_serilizer(_mailing)
# #     return MailingAddress(owner_data, mailing_data)
#
#
# def get_general_data(parcel_id: str):
#     response = scrape.general_info(parcel_id)
#     response.raise_for_status()
#     _owner, _mailing = parse.general_content(response.content)
#     owner = owner_from_raw(_owner)
#     mailing = mailing_from_raw_general(_mailing)
#     return schemas.OwnerAndMailing(owner=owner, mailing=mailing)
#
#
# def get_tax_data(parcel_id: str):
#     response = scrape.tax_info(parcel_id)
#     response.raise_for_status()
#     _owner, _mailing = parse.tax_content(response.content)
#     owner = owner_from_raw(_owner)
#     mailing = mailing_from_raw_tax(_mailing)
#     return schemas.OwnerAndMailing(owner=owner, mailing=mailing)
#
#
# def owner_from_raw(data: list[Tag | NavigableString]) -> schemas.Owner:
#     owner_list = _clean_tags(data)
#     is_multi_entity = False
#     if len(owner_list) > 1:
#         is_multi_entity = True
#     # Owner names often have trailing whitespace
#     #  If it isn't stripped away, the dirty_owner != clean_owner check
#     #  will always return True.
#     dirty_owner = " & ".join(o.strip() for o in owner_list)
#     clean_owner = _clean_whitespace(dirty_owner)
#     if dirty_owner != clean_owner:  # Todo:
#         # Todo: this is most likely duplicate logic,
#         #  but I haven't thought to prove it yet
#         is_multi_entity = True
#     return schemas.Owner(name=clean_owner, is_multi_entity=is_multi_entity)
#
#
# def mailing_from_raw_tax(data: list[Tag | NavigableString]) -> schemas.Mailing:
#     # Todo: these two functions almost certainly belong in lib.parse
#     address_list = _clean_tags(data)
#     if len(address_list) == 3:
#         line1 = parse.line1(address_list[0])
#         line2 = parse.line2(address_list[1])
#         line3 = parse.line3(address_list[2])
#     elif not address_list:
#         line1 = line2 = line3 = None
#     else:
#         raise NotImplementedError("I haven't dealt with this yet")
#     return schemas.Mailing(line1=line1, line2=line2, line3=line3)
#
#
# def mailing_from_raw_general(data: list[Tag | NavigableString]) -> schemas.Mailing:
#     address_list = _clean_tags(data)
#     if len(address_list) == 2:
#         line1 = parse.general_street_line(address_list[0])
#         line2, line3 = parse.city_state_zip(address_list[1])
#     elif len(address_list) == 3:
#         attn = (
#             address_list[0]
#             .lstrip("ATTN ")
#             .lstrip("ATTN: ")
#             .lstrip("ATTENTION ")
#             .lstrip("ATTENTION: ")
#         )
#         line1 = parse.general_street_line(address_list[1])
#         line1.attn = attn
#         line2, line3 = parse.city_state_zip(address_list[1])
#     elif len(address_list) == 0:
#         line1 = line2 = line3 = None
#     else:
#         raise RuntimeError
#     return schemas.Mailing(line1=line1, line2=line2, line3=line3)
#
#
# def _clean_tags(content: list[Tag | NavigableString]) -> list[str]:
#     return [str(tag) for tag in content if isinstance(tag, NavigableString)]
#
#
# def _clean_whitespace(text: str) -> str:
#     return re.sub(r"\s+", " ", text)
#
#
# # def get_cog_general_and_mortgage(db: Session, parcel_id: str) -> schemas.CogGeneralAndMortgage:
# # This function was not designed to handle the insertion of new parcels.
# #  Please do not attempt to catch NoResultFound and use it to insert new parcels
# #  without first reevaluating this program's architecture
# # fmt: off
#     # all_addresses: list[schemas.CogTables] = []
#     # parcel = select.parcel(db, parcel_id)
#     # parcel_mailing_addresses = select.parcel_mailing_addresses(db, parcel.parcelkey)
#     # for (parcel_mailing_address,) in parcel_mailing_addresses:
#     #     mailing_address = select.address(db, parcel_mailing_address.mailingaddress_addressid)
#     #     mailing_street = select.street(db, mailing_address.street_streetid)
#     #     city_state_zip = select.city_state_zip(db, mailing_street.citystatezip_cszipid)
#     #     try:
#     #         human_mailing_address = select.human_mailing_address(db, mailing_address.addressid)
#     #         human = select.human(db, human_mailing_address.humanmailing_humanid)
#     #     except NoResultFound:
#     #         human = None
#     #     tables = schemas.CogTables(
#     #         parcel=parcel,
#     #         parcel_mailing_address=parcel_mailing_address,
#     #         mailing_address=mailing_address,
#     #         mailing_street=mailing_street,
#     #         city_state_zip=city_state_zip,
#     #         human=human,
#     #     )
#     #     all_addresses.append(tables)
#     # # fmt: on
#     # return schemas.CogGeneralAndMortgage(
#     #     general=_match_general(all_addresses),
#     #     mortgage=_match_mortgage(all_addresses),
#     # )
#
#
# def _match_number(
#     num_to_match: int, owners_and_mailings
# ):
#     for x in owners_and_mailings:
#         if x.parcel_mailing_address.linkedobjectrole_lorid == num_to_match:
#             return x
#     return None
#
#
# _match_general = partial(_match_number, GENERAL_LINKED_OBJECT_ROLE)
# _match_mortgage = partial(_match_number, MORTGAGE_LINKED_OBJECT_ROLE)
#
#
# # def _sync(
# #     db: Session,
# #     parcel_id: str,
# #     role: int,
# #     county_info: schemas.OwnerAndMailing,
# #     cog_tables: Optional[schemas.CogTables],
# # ):
# #     # Todo: Find a schema where "parcel_id" doesn't have to be an argument"
# #     cog_info = _cog_tables_to_owner_and_mailing(cog_tables)
# #
# #     if county_info.mailing != cog_info.mailing:
# #         if county_info is None:
# #             raise NotImplementedError("Todo: get to cases where the cog has more info than the county")
# #         # Todo: writing this code pains me because of how unorganized it is. REFACTOR
# #         #  Additionally, I have a nagging suspicion this code is broken
# #         parcel_key: int
# #         if not (cog_tables is None):
# #             deactivate.parcel_mailing_address(
# #                 db,
# #                 parcel_key=cog_tables.parcel_mailing_address.parcel_parcelkey,
# #                 address_id=cog_tables.parcel_mailing_address.mailingaddress_addressid,
# #             )
# #             parcel_key = cog_tables.parcel.parcelkey
# #         else:
# #             _parcel = select.parcel(db, parcel_id=parcel_id)
# #             parcel_key = _parcel.parcelkey
# #
# #         mailing_address_id = write_parcel_info(db, county_info.mailing, parcel_key, role=role)
# #     # todo: I don't like how it's hard to tell what sets mailing_address_id.
# #     else:
# #         mailing_address_id = cog_tables.mailing_address.addressid
# #
# #
# #
# #     if county_info.owner != cog_info.owner:
# #         if county_info is None:
# #             raise NotImplementedError("Todo: get to cases where the cog has more info than the county")
# #         if not (cog_tables.human is None):
# #             deactivate.human_mailing_address(
# #                 db,
# #                 human_id=cog_tables.human.humanid,
# #                 # This mailing address id is not to be changed
# #                 mailing_id=cog_tables.mailing_address.addressid
# #             )
# #         write_owner_info(db, county_info.owner, mailing_address_id)
#
#
# # def write_owner_info(db: Session, o: schemas.Owner, mailing_address_id: int):
# #     pass
# #
# #
# # def write_parcel_info(session: Session, m: schemas.Mailing, parcel_key: int, role: int) -> int:
# #     # fmt: off
# #     try:
# #         city_state_zip_id = select.city_state_zip_id(
# #             session, city=m.line2.city, state=m.line2.state, zip_=m.line3.zip
# #         )
# #     except NoResultFound as err:
# #         raise NotImplementedError
# #         city_state_zip_id = insert.city_state_zip(
# #             session, city=m.line2.city, state=m.line2.state, zip_=m.line3.zip
# #         )
# #
# #     try:
# #         street_id = select.mailing_street_id(
# #             session, street_name=m.line1.street, city_state_zip_id=city_state_zip_id
# #         )
# #     except NoResultFound as err:
# #         street_id = insert.mailing_street(
# #             session,
# #             street_name=m.line1.street,
# #             city_state_zip_id=city_state_zip_id,
# #             is_pobox=m.line1.is_pobox
# #         )
# #
# #     try:
# #         address_id = select.address_by_info(
# #             session, street_id=street_id, number=m.line1.number
# #         )
# #     except NoResultFound:
# #         address_id = insert.mailing_address(
# #             session, street_id=street_id, number=m.line1.number
# #         )
# #     insert.parcel_mailing(session, address_id=address_id, parcel_key=parcel_key, role=role)
# #     return address_id
