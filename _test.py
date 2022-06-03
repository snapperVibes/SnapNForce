import logging
from os import path
from time import sleep

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import MultipleResultsFound

from app import database
from app.database import get_db_context
from app.lib import sync_parcel_data

logging.basicConfig(filename=path.join("log", "_test.log"), filemode="a", level=logging.INFO)
logging.getLogger("root")


def get_parcel_ids(conn: Connection):
    cursor_result = conn.execute(
        text("SELECT parcelidcnty FROM parcel WHERE deactivatedts IS NULL LIMIT 300;")
    )
    return [i[0] for i in cursor_result]


SKIP_TO = 1


async def main():
    with get_db_context() as conn:
        parcel_ids = get_parcel_ids(conn)
    import sqlmodel

    with sqlmodel.Session(database._engine) as db:
        for i, parcel_id in enumerate(parcel_ids):
            if i < SKIP_TO:
                continue
            # TODO: fix caching
            # cog_data = get_cog_tables(parcel_id)
            # print(parcel_id, cog_data, sep="\t")
            logging.info(f"Parcel:\t{parcel_id}\tNumber:\t{i}")

            try:
                d = await sync_parcel_data(db, parcel_id)
                print("\n")
                print(f"{i}\t{parcel_id}\n" f"GENERAL:\t{d.general}\n" f"MORTGAGE:\t{d.mortgage}")
                print("\n" + "-" * 89)
            except MultipleResultsFound as err:
                print(f"MULTIPLE RESULTS on {parcel_id}")
                logging.error(err)
            # Let's be polite neighbors
            sleep(0.75)


logging.info("Having another go at it 🙂")
if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
