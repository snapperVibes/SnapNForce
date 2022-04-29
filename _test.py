import logging
from os import path

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.database import get_db_context, SessionLocal
from app.lib import sync_parcel_data

logging.basicConfig(filename=path.join("log", "_test.log"), filemode="a", level=logging.INFO)
logging.getLogger("root")


def get_parcel_ids(conn: Connection):
    cursor_result = conn.execute(
        text("SELECT parcelidcnty FROM parcel WHERE deactivatedts IS NULL LIMIT 300;")
    )
    return [i[0] for i in cursor_result]


# SKIP_TO = 5
SKIP_TO = 204

logging.info("Having another go at it 🙂")
if __name__ == "__main__":
    with get_db_context() as conn:
        parcel_ids = get_parcel_ids(conn)
    with SessionLocal() as db:
        for i, parcel_id in enumerate(parcel_ids):
            if i < SKIP_TO:
                continue
            # TODO: fix caching
            # cog_data = get_cog_tables(parcel_id)
            # print(parcel_id, cog_data, sep="\t")
            logging.info(f"Parcel:\t{parcel_id}\tNumber:\t{i}")
            d = sync_parcel_data(db, parcel_id)
            print("\n")
            print(f"{i}\t{parcel_id}\n" f"GENERAL:\t{d.general}\n" f"MORTGAGE:\t{d.mortgage}\n")
            print("\n" + "-" * 89)
