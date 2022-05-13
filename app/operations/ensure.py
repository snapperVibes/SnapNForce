from app.schemas import orm
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session
from app.operations import select, insert


def _select_or_insert(db: Session, select_func, insert_func, **kwargs):
    try:
        return select_func(db, **kwargs)
    except NoResultFound:
        return insert_func(db, **kwargs)


def city_state_zip(db, *, city, state, zip_) -> orm.MailingCityStateZip:
    return _select_or_insert(
        db, select._city_state_zip, insert.city_state_zip, city=city, state=state, zip_=zip_
    )


def street(db, *, city_state_zip_id, street_name, is_pobox) -> orm.MailingStreet:
    return _select_or_insert(
        db,
        select._street,
        insert.street,
        city_state_zip_id=city_state_zip_id,
        street_name=street_name,
        is_pobox=is_pobox,
    )


def address(db, *, street_id, number, attn, secondary) -> orm.MailingAddress:
    return _select_or_insert(
        db,
        select._address,
        insert.address,
        street_id=street_id,
        number=number,
        attn=attn,
        secondary=secondary,
    )


def human(db, *, name, is_multi_entity) -> orm.Human:
    return _select_or_insert(db, select._human, insert.human, name=name, is_multi_entity=is_multi_entity)
