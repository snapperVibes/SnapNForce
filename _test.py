import warnings

import app
import lib.parse
from app.lib import get_parcel_data_from_county, mailing_from_raw_general
from app.database import _get_db2, SessionLocal
from sqlalchemy import text
from sqlalchemy.engine import Connection

from lib import scrape, parse


def get_parcel_ids(conn: Connection):
    cursor_result = conn.execute(
        text("SELECT parcelidcnty FROM parcel WHERE deactivatedts IS NULL LIMIT 300;")
    )
    return [i[0] for i in cursor_result]


SKIP_TO = 0
if __name__ == "__main__":
    with _get_db2() as conn:
        parcel_ids = get_parcel_ids(conn)
    with SessionLocal() as session:
        for i, parcel_id in enumerate(parcel_ids):
            if i < SKIP_TO:
                continue
            # TODO: fix caching
            # cog_data = get_cog_tables(parcel_id)
            # print(parcel_id, cog_data, sep="\t")
            d = get_parcel_data_from_county(parcel_id)

            print(f"{i}\t{parcel_id}\n" f"GENERAL:\t{d.general}\n" f"MORTGAGE:\t{d.mortgage}\n")
