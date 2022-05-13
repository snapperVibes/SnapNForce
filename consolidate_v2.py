from sqlalchemy import text
from sqlalchemy.engine import Connection
from app.database import get_db_context

from sqlalchemy import MetaData, Table, Column, Integer

metadata_obj = MetaData()

linked_object_role = Table(
    "linkedobjectrole", metadata_obj, Column("lorid", Integer, primary_key=True)
)


def consolidate_parcels(conn: Connection):
    # dup_parcels_cte = text(
    #     "SELECT parcelidcnty, dups.keys FROM ("
    #     "  SELECT parcelidcnty, array_agg(parcelkey) AS keys"
    #     "  FROM parcel AS p"
    #     "  GROUP BY parcelidcnty, deactivatedts"
    #     "  HAVING count(*) > 1 AND deactivatedts IS null"
    #     ") as dups"
    # ).columns().cte()
    dup_parcels_stmt = text(
        "SELECT parcelidcnty, array_agg(parcelkey)"
        "  FROM parcel"
        "  GROUP BY parcelidcnty, deactivatedts"
        "  HAVING count(*) > 1 AND deactivatedts IS null"
    )
    dup_parcels_result = conn.execute(dup_parcels_stmt)

    for parcelidcnty, parcelkeys in dup_parcels_result:
        number_active = 0
        to_deactivate = []
        for parcel_key in parcelkeys:
            SELECT_PARCEL_MAILING = text(
                "SELECT mailingaddress_addressid, deactivatedts FROM parcelmailingaddress WHERE"
                "  parcel_parcelkey = :parcel_key"
            ).params({"parcel_key": parcel_key})
            address_id, parcel_mailing_deactivated = conn.execute(SELECT_PARCEL_MAILING).one()
            SELECT_ADDRESS = text(
                "SELECT deactivatedts FROM mailingaddress WHERE addressid = :address_id"
            ).params({"address_id": address_id})
            mailing_deactivated = conn.execute(SELECT_ADDRESS).scalar_one()
            if mailing_deactivated or parcel_mailing_deactivated:
                to_deactivate.append((parcel_key, address_id))
            else:
                number_active += 1
        print(number_active, to_deactivate)


if __name__ == "__main__":
    with get_db_context() as conn:
        with conn.begin():
            consolidate_parcels(conn)
