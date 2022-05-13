from app.operations.insert import _insert_event, _common
from app import orm
from sqlmodel import insert


def parcel_to_address(session, parcelkey, address_id, role):
    statement = insert(orm.ParcelMailingAddress).values(
        parcel_parcelkey=parcelkey,
        mailingaddress_addressid=address_id,
        linkedobjectrole_lorid=role,
        **_common
    ).returning(orm.ParcelMailingAddress)
    return session.execute(statement).one()


def human_to_parcel(session, parcelkey, humanid, role):
    statement = insert(orm.HumanParcel).values(
        parcel_parcelkey=parcelkey,
        human_humanid = humanid,
        linkedobjectrole_lorid = role,
        ** _common
    ).returning(orm.HumanParcel)
    return session.execute(statement).one()


def human_to_address(session, human_id, address_id, role):
    statement = insert(orm.HumanMailingAddress).values(
        humanmailing_humanid=human_id,
        humanmailing_addressid=address_id,
        linkedobjectrole_lorid=role,
        **_common
    ).returning(orm.HumanMailingAddress)
    return session.execute(statement).one()

