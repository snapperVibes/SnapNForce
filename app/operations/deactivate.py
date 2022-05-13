# fmt: off
from app import orm
from app.constants import USER_ID
from sqlmodel import update
from sqlalchemy.sql import func

_common = {
    "deactivatedts": func.now(),
    "deactivatedbyuser_userid": USER_ID
}

def human_to_parcel(session, id):
    statement = update(orm.HumanParcel).where(orm.HumanParcel.linkid == id).values(**_common)
    session.execute(statement)

def parcel_to_address(session, id):
    statement = update(orm.ParcelMailingAddress).where(orm.ParcelMailingAddress.linkid==id).values(**_common)
    session.execute(statement)

def human_to_address(session, id):
    statement = update(orm.HumanMailingAddress).where(orm.HumanMailingAddress.linkid==id).values(**_common)
    session.execute(statement)

def address(session, id):
    statement = update(orm.MailingAddress).where(orm.MailingAddress.addressid==id).values(**_common)
    session.execute(statement)

def human(session, id):
    statement = update(orm.MailingAddress).where(orm.Human.humanid==id).values(**_common)
    session.execute(statement)
