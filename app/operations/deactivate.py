# fmt: off
from app import orm
from app.constants import USER_ID
from sqlmodel import update, Session
from sqlalchemy.sql import func

_common = {
    "deactivatedts": func.now(),
    "deactivatedby_userid": USER_ID
}

# def linked_parcel_and_address(session, id):
#     statement = update(orm.ParcelMailingAddress).where(orm.ParcelMailingAddress.linkid==id).values(**_common)
#     session.execute(statement)
#
#
# def linked_humans_and_address(session, id):
#     statement = update(orm.HumanMailingAddress).where(orm.HumanMailingAddress.link)

def linking_model(session: Session, model):
    model_type = type(model)
    statement = update(model_type).where(model_type.linkid == model.linkid).values(**_common)
    session.execute(statement)
