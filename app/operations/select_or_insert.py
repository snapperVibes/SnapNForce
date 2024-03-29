import typing

import sqlmodel
from sqlmodel import Session

from app.operations import select, insert
from app.operations.events import UnimplementedEvent
from app.orm import MailingAddress, Human, ParcelMailingAddress, MailingCityStateZip

from sqlalchemy import func

from app.constants import USER_ID, SOURCE_ID

ModelType = typing.TypeVar("ModelType", bound=sqlmodel.SQLModel)
SelectFuncType = typing.Callable[[Session, ModelType], typing.Optional[ModelType]]
InsertFuncType = typing.Callable[[Session, ModelType], ModelType]

_common = {
    "createdts": func.now(),
    "createdby_userid": USER_ID,
    "lastupdatedts": func.now(),
    "lastupdatedby_userid": USER_ID,
}


def _select_or_insert(
    db: Session,
    model: typing.Optional[ModelType],
    select_func: SelectFuncType,
    insert_event=UnimplementedEvent) -> typing.Optional[ModelType]:
    if model is None:
        return None
    returned_model = select_func(db, model)
    if returned_model is None:
        returned_model = model
        for k, v in _common.items():
            setattr(returned_model, k, v)
        db.add(returned_model)
        db.commit()  # Todo: this should probably be elsewhere?
    return returned_model


def parcel(db, model):
    # Todo: this doesn't work yet because I haven't figured out how to pass municode to the appropriate functions
    return _select_or_insert(db, select.parcel, insert.parcel, model)


def city_state_zip(db, model) -> MailingCityStateZip:
    return _select_or_insert(db, model, select.city_state_zip)


def street(db, model):
    return _select_or_insert(db, model, select.street)


def address(db, model: MailingAddress) -> MailingAddress:
    return _select_or_insert(db, model, select.address)


def human(db, model: Human) -> Human:
    h = select.human(db, model)
    if h is None:
        db.add(model)
        db.commit()
        db.refresh(model)
    return h


def linked_parcel_and_address(db, model: ParcelMailingAddress) -> ParcelMailingAddress:
    return _select_or_insert(db, model, select.linked_parcel_and_address)


def linked_human_and_address(db, model):
    return _select_or_insert(db, model, select.linked_human_and_address)


def linked_human_and_parcel(db, model):
    return _select_or_insert(db, model, select.linked_human_and_parcel)
