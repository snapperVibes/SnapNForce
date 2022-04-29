from app import schemas
from sqlmodel import Session

from app.operations import select_or_insert


def sync_county_data_with_cog(
    db: Session, *, parcel_id: str, county_mailing: schemas.Mailing
) -> schemas.GeneralAndMortgage:
    a, city_state_zip = select_or_insert.city_state_zip(
        db,
        city=county_mailing.line2.city,
        state=county_mailing.line2.state,
        zip_=county_mailing.line3.zip,
    )
    b, street = select_or_insert.street(
        db,
        city_state_zip_id=city_state_zip.id,
        street_name=county_mailing.line1.street,
        is_pobox=county_mailing.line1.is_pobox,
    )
    c, address = select_or_insert.address(
        db, street_id=street.streetid, number=county_mailing.line1.number
    )
    ## Todo: we're net set up to handle the insertion of new parcels yet
    # parcel = select_or_insert.parcel(
    #     db, county_parcel_id=parcel_id,
    # )
    return address, street, city_state_zip


# from typing import Optional
#
# from sqlmodel import Session
#
# from app import schemas, orm
# from app.operations import select, insert, deactivate, select_or_insert
# from app.operations._common import GENERAL_LINKED_OBJECT_ROLE, MORTGAGE_LINKED_OBJECT_ROLE
# from sqlalchemy.exc import NoResultFound, MultipleResultsFound
#
# from lib.parse._types import Line1, Line2, Line3
#
#
# def _sync_mailing(
#     db: Session,
#     parcel_id: str,
#     county_mailing: Optional[schemas.Mailing],
# ) -> tuple[orm.MailingAddress, orm.MailingStreet, orm.MailingCityStateZip]:
#     city_state_zip = select_or_insert.city_state_zip(
#         db,
#         city=county_mailing.line2.city,
#         state=county_mailing.line2.state,
#         zip_=county_mailing.line3.zip,
#     )
#     street = select_or_insert.street(
#         db,
#         city_state_zip_id=city_state_zip.id,
#         street_name=county_mailing.line1.street,
#         is_pobox=county_mailing.line1.is_pobox,
#     )
#     address = select_or_insert.address(
#         db, street_id=street.streetid, number=county_mailing.line1.number
#     )
#     parcel = select_or_insert.parcel(
#         db,
#     )
#     return address, street, city_state_zip
#
#
# def _sync_owner(db, county_owner, cog_owner) -> schemas.Owner:
#     pass
#
#
# def _sync(
#     role_id: int,
#     db: Session,
#     parcel_id: str,
#     county: schemas.OwnerAndMailing,
#     cog_tables,
# ) -> schemas.OwnerAndMailing:
#     cog = _cog_tables_to_optional_owner_and_mailing(cog_tables)
#     _parcel_key = cog_tables.parcel.parcelkey
#     _address_id = cog_tables.mailing_address.addressid
#
#     if county.mailing != cog.mailing:
#         if county.mailing is None:
#             # Todo: Logic has yet to be decided for when the cog has more info than the county
#             raise NotImplementedError
#         if cog.mailing:
#             deactivate.parcel_mailing_address(
#                 db,
#                 parcel_key=cog_tables.parcel_mailing_address.parcel_parcelkey,
#                 address_id=cog_tables.parcel_mailing_address.mailingaddress_addressid,
#             )
#         mailing = _sync_mailing(
#             db,
#             parcel_id=parcel_id,
#             county_mailing=county.mailing,
#         )
#     owner = _sync_owner(db, county_owner=county.owner, cog_owner=cog.owner)
#     return schemas.OwnerAndMailing(owner=owner, mailing=mailing)
#
#
# def general(db: Session, parcel_id: str, county: schemas.OwnerAndMailing, cog):
#     return _sync(GENERAL_LINKED_OBJECT_ROLE, db, parcel_id, county, cog)
#
#
# def mortgage(db: Session, parcel_id: str, county: schemas.OwnerAndMailing, cog):
#     return _sync(MORTGAGE_LINKED_OBJECT_ROLE, db, parcel_id, county, cog)
#
#
# def _cog_tables_to_optional_owner_and_mailing(
#     cog,
# ) -> tuple[Optional[schemas.Owner], schemas.Mailing]:
#     if cog is None:
#         return None
#
#     owner = None
#     if cog.human is not None:
#         owner = schemas.Owner(name=cog.human.name, is_multi_entity=cog.human.multihuman)
#
#     return schemas.OwnerAndMailing(
#         owner=owner,
#         mailing=schemas.Mailing(
#             line1=schemas.Line1(
#                 is_pobox=cog.mailing_street.pobox,
#                 attn=cog.mailing_address.attention,
#                 number=cog.mailing_address.bldgno,
#                 street=cog.mailing_street.name,
#             ),
#             line2=schemas.Line2(city=cog.city_state_zip.city, state=cog.city_state_zip.state_abbr),
#             line3=schemas.Line3(zip=cog.city_state_zip.zip_code),
#         ),
#     )
