from app.operations._common import USER_ID
from sqlmodel import Session, text


def parcel_mailing_address(db: Session, *, parcel_key: int, address_id: int):
    # Using the orm isn't important, as per SQLAlchemy's author
    db.execute(
        text(
            "UPDATE parcelmailingaddress"
            "  SET deactivatedts=now(),"
            "    deactivatedby_userid=:user_id"
            "  WHERE parcel_parcelkey=:parcel_key AND"
            "  mailingaddress_addressid=:address_id"
        ),
        params={"parcel_key": parcel_key, "address_id": address_id, "user_id": USER_ID},
    )


def human_mailing_address(db, *, human_id, mailing_id):
    db.execute(
        text(
            "UPDATE humanmailingaddress"
            "  SET deactivatedts=now(),"
            "    deactivatedby_userid=:user_id"
            "  WHERE humanmailing_addressid=:human_id AND"
            "  humanmailing_addressid=:mailing_id"
        ),
        params={"human_id": human_id, "mailing_id": mailing_id, "user_id": USER_ID},
    )
