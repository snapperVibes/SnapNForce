from sqlmodel import Session
from sqlalchemy.exc import NoResultFound

from app import orm
from app.operations import select, insert, deactivate


def _ensure_current(db: Session, select_func, insert_func, deactivate_func, model):
    try:
        select_func(db, **kwargs)
    except NoResultFound:
        return insert_func(db, **kwargs)


def parcel(db: Session, model: orm.Parcel) -> orm.Parcel:
    _ensure_current(db, select.parcel, insert.parcel, deactivate.parcel, model)
