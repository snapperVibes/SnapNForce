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


def city_state_zip(session, *, city: str, state: str, zip_: str) -> orm.MailingCityStateZip:
    statement = (
        insert(orm.MailingCityStateZip)
        .values(
            city=city,
            state_abbr=state,
            zip_code=zip_,
            **_common
        )
        .returning(orm.MailingCityStateZip)
    )
    return session.execute(statement).scalar_one()


def parcel_mailing(session, *, parcel_key: int, address_id: int, role: int) -> None:
    statement = insert(orm.ParcelMailingAddress).values(
        parcel_parcelkey=parcel_key,
        mailingaddress_addressid=address_id,
        linkedobjectrole_lorid=role,
        **_common
    )
    session.execute(statement)


def street(session, *, street_name, city_state_zip_id, is_pobox) -> orm.MailingStreet:
    statement = (
        insert(orm.MailingStreet)
        .values(
            name=street_name,
            citystatezip_cszipid=city_state_zip_id,
            pobox=is_pobox,
            **_common
        )
        .returning(orm.MailingStreet)
    )
    return session.execute(statement).one()


def mailing_address(session, *, street_id: int, number: str) -> orm.MailingAddress:
    statement = (
        insert(orm.MailingAddress)
        .values(
            bldgno=number,
            street_streetid=street_id,
            **_common
        )
        .returning(orm.MailingAddress)
    )
    return session.execute(statement).one()


def human(session, *, name: str, is_multi_entity: bool) -> orm.Human:
    statement = insert(orm.Human).values(
        name=name, multihuman=is_multi_entity, **_common
    ).returning(orm.Human)
    return session.execute(statement).one()


def human_mailing(session, *, human_id: int, mailing_id: int) -> orm.HumanMailingAddress:
    statement = insert(orm.HumanMailingAddress).values(
        human_id=human_id, mailing_id=mailing_id, **_common
    )
    return session.execute(statement).one()