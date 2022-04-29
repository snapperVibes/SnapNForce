"""
One off script to add a database integrity check to ensure
multiple mailingaddress referring to the same building cannot be active at the same time
"""
from sqlalchemy import text
from app.database import get_db_context, Connection
from app.operations._common import USER_ID


def consolidate_mailing_addresses(conn: Connection):
    DUPLICATE_ADDRESSES = text(
        "SELECT street_streetid, bldgno, count(*)"
        "  FROM mailingaddress"
        "  WHERE deactivatedts is NULL"
        "  GROUP BY street_streetid, bldgno"
        "  HAVING count(*) > 1"
    )
    for x in conn.execute(DUPLICATE_ADDRESSES):
        street_id, number, count = x
        statement = text(
            "SELECT addressid, deactivatedts FROM mailingaddress"
            "  WHERE street_streetid=:street_id"
            "  AND bldgno=:number"
            "  AND deactivatedts is NULL"
            "  ORDER BY lastupdatedts DESC",
        ).bindparams(street_id=street_id, number=number)
        dups: list[int] = [x[0] for x in conn.execute(statement).all()]
        old_dups = dups[1:]
        statement = text(
            "UPDATE mailingaddress"
            "  SET deactivatedts=now()"
            "  AND deactivatedby_userid=:user_id"
            "  WHERE addressid = ANY(:old_dups)"
        ).bindparams(old_dups=old_dups, user_id=USER_ID)
        conn.execute(statement)

    statement = text(
        "CREATE UNIQUE INDEX IF NOT EXISTS mailingaddress_unique_where_not_null"
        "  ON mailingaddress (bldgno, attention, secondary)"
        "  WHERE (deactivatedts is null)"
    )
    conn.execute(statement)


def consolidate_parcels(conn: Connection):
    DUPLICATED_PARCELS = text(
        "SELECT parcelidcnty, dups.keys FROM ("
        "  SELECT parcelidcnty, array_agg(parcelkey) AS keys"
        "  FROM parcel AS p"
        "  GROUP BY parcelidcnty, deactivatedts"
        "  HAVING count(*) > 1 AND deactivatedts IS null"
        ") as dups"
    )
    dups = conn.execute(DUPLICATED_PARCELS).all()

    for parcel_id, parcel_keys in dups:
        print(parcel_id, parcel_keys)
        # There needs to be one (and only one) active address to merge
        number_active = 0
        # Parcel, Parcel MailingAddress, and MailingAddress
        to_deactivate = []

        for parcel_key in parcel_keys:
            SELECT_PARCEL_MAILING = text(
                "SELECT mailingaddress_addressid, deactivatedts FROM parcelmailingaddress WHERE"
                "  parcel_parcelkey = :parcel_key"
            ).params({"parcel_key": parcel_key})
            address_id, parcel_mailing_deactivated = conn.execute(SELECT_PARCEL_MAILING).one()
            SELECT_ADDRESS = text(
                "SELECT deactivatedts FROM mailingaddress WHERE" "  addressid = :address_id"
            ).params({"address_id": address_id})
            mailing_deactivated = conn.execute(SELECT_ADDRESS).scalar_one()

            if parcel_mailing_deactivated or mailing_deactivated:
                print(parcel_key)
                to_deactivate.append((parcel_key, address_id))
            else:
                number_active += 1

        if number_active == 1:
            for parcel_key, address_id in to_deactivate:
                statement = text(
                    "UPDATE parcelmailingaddress SET deactivatedts=now(), deactivatedby_userid=:USER_ID WHERE parcel_parcelkey=:parcel_key and mailingaddress_addressid=:address_id AND deactivatedts IS null; "
                    "UPDATE mailingaddress       SET deactivatedts=now(), deactivatedby_userid=:USER_ID WHERE addressid=:address_id and deactivatedts is null; "
                    "UPDATE parcel               SET deactivatedts=now(), deactivatedby_userid=:USER_ID WHERE parcelkey=:parcel_key and deactivatedts is null; "
                ).params({"USER_ID": USER_ID, "parcel_key": parcel_key, "address_id": address_id})
                conn.execute(statement)
        else:
            raise RuntimeError("Hmmm")

    statement = text(
        "CREATE UNIQUE INDEX IF NOT EXISTS parcel_unique_where_not_null"
        "  ON parcel (parcelidcnty, deactivatedts)"
        "  WHERE (deactivatedts is null)"
    )
    conn.execute(statement)


def main():
    with get_db_context() as conn:
        with conn.begin():
            consolidate_mailing_addresses(conn)
            consolidate_parcels(conn)
            conn.commit()
    print("nice")


conn: Connection  # This is a type hint
if __name__ == "__main__":
    main()
    print("Script ran 👍")
