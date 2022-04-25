"""
One off script to add a database integrity check to ensure
multiple mailingaddress referring to the same building cannot be active at the same time
"""
from sqlalchemy import text
from app.database import _get_db2, Connection
from app.operations._common import USER_ID


def main():
    with _get_db2() as conn:
        with conn.begin():
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
                "CREATE UNIQUE INDEX parcel_unique_where_not_null"
                "  ON parcel (parcelidcnty, deactivatedts)"
                "  WHERE (deactivatedts is null)"
            )
            conn.execute(statement)


conn: Connection  # This is a type hint
if __name__ == "__main__":
    main()
    print("Consolidated mailing addresses")
