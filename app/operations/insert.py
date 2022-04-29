import logging
from time import sleep
from functools import wraps
from typing import Optional

from sqlmodel import insert
from sqlalchemy.sql import func
from app import orm
from app.operations._common import USER_ID


_common = {
    "createdts": func.now(),
    "createdby_userid": USER_ID,
    "lastupdatedts": func.now(),
    "lastupdatedby_userid": USER_ID,
}


def _insert_event(name: str, requires_code_officer_approval: bool):
    def inner_func(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if requires_code_officer_approval:
                logging.warning(f"NEEDS OFFICER APPROVAL: {name}\t{kwargs}")
                # print(f"Seeking approval to insert {name}. {kwargs}")
                # sleep(2)
            return func(*args, **kwargs)

        return wrapper

    return inner_func


@_insert_event("city/state/zip", requires_code_officer_approval=True)
def city_state_zip(session, *, city: str, state: str, zip_: str) -> orm.MailingCityStateZip:
    statement = (
        insert(orm.MailingCityStateZip)
        .values(city=city, state_abbr=state, zip_code=zip_, **_common)
        .returning(orm.MailingCityStateZip)
    )
    return session.execute(statement).one()


@_insert_event("parcel mailing", requires_code_officer_approval=False)
def parcel_mailing(session, *, parcel_key: int, address_id: int, role: int) -> None:
    statement = (
        insert(orm.ParcelMailingAddress)
        .values(
            parcel_parcelkey=parcel_key,
            mailingaddress_addressid=address_id,
            linkedobjectrole_lorid=role,
            **_common,
        )
        .returning(orm.ParcelMailingAddress)
    )
    session.execute(statement)


@_insert_event("street", requires_code_officer_approval=True)
def street(session, *, street_name, city_state_zip_id, is_pobox) -> orm.MailingStreet:
    statement = (
        insert(orm.MailingStreet)
        .values(
            name=street_name, citystatezip_cszipid=city_state_zip_id, pobox=is_pobox, **_common
        )
        .returning(orm.MailingStreet)
    )
    return session.execute(statement).one()


@_insert_event("mailing address", requires_code_officer_approval=False)
def mailing_address(
    session, *, street_id: int, number: str, attn: Optional[str]
) -> orm.MailingAddress:
    statement = (
        insert(orm.MailingAddress)
        .values(bldgno=number, street_streetid=street_id, attention=attn, **_common)
        .returning(orm.MailingAddress)
    )
    return session.execute(statement).one()


@_insert_event("human", requires_code_officer_approval=False)
def human(session, *, name: str, is_multi_entity: bool) -> orm.Human:
    statement = (
        insert(orm.Human)
        .values(name=name, multihuman=is_multi_entity, **_common)
        .returning(orm.Human)
    )
    return session.execute(statement).one()


@_insert_event("human mailing", requires_code_officer_approval=False)
def human_mailing(session, *, human_id: int, mailing_id: int) -> orm.HumanMailingAddress:
    statement = (
        insert(orm.HumanMailingAddress)
        .values(humanmailing_humanid=human_id, humanmailing_addressid=mailing_id, **_common)
        .returning(orm.HumanMailingAddress)
    )
    return session.execute(statement).one()
