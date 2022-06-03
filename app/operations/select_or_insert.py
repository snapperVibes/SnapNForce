import typing

import sqlmodel
from sqlmodel import Session

from app.operations import select, insert
from app.operations.events import UnimplementedEvent
from app.orm import MailingAddress, Human, ParcelMailingAddress, MailingCityStateZip

ModelType = typing.TypeVar("ModelType", bound=sqlmodel.SQLModel)
SelectFuncType = typing.Callable[[Session, ModelType], typing.Optional[ModelType]]
InsertFuncType = typing.Callable[[Session, ModelType], ModelType]


def _select_or_insert(db: Session, model: typing.Optional[ModelType], select_func: SelectFuncType, insert_event=UnimplementedEvent) -> typing.Optional[ModelType]:
    if model is None:
        return None
    _model = select_func(db, model)
    if _model is None:
        db.add(model)
        _model = model
    return _model


## Todo: this doesn't work yet because I haven't figured out how to pass municode to the appropriate functions
# def parcel(db, model):
#     return _select_or_insert(db, select.parcel, insert.parcel, model)


def city_state_zip(db, model) -> MailingCityStateZip:
    return _select_or_insert(db, model, select.city_state_zip)


def street(db, model):
    return _select_or_insert(db, model, select.street)


def address(db, model: MailingAddress) -> MailingAddress:
    return _select_or_insert(db, model, select.address)


def human(db, model: Human) -> Human:
    return _select_or_insert(db, model, select.human)


def linked_parcel_and_address(db, model: ParcelMailingAddress) -> ParcelMailingAddress:
    return _select_or_insert(db, model, select.linked_parcel_and_address)


def linked_human_and_address(db, model):
    return _select_or_insert(db, model, select.linked_human_and_address)


def linked_human_and_parcel(db, model):
    return _select_or_insert(db, model, select.linked_human_and_parcel)