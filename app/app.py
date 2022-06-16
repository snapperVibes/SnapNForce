import logging
import random
import time

from fastapi import FastAPI, Depends
from sqlmodel import Session

from app import lib, schemas
from app.database import get_db
from app.logging import logger
from lib.parse.exceptions import HtmlParsingError

app = FastAPI()


@app.get("/")
def root():
    globe = random.choice(["🌎", "🌍", "🌏"])
    return {"msg": f"Hello, world {globe}"}


@app.get("/parcel/get-data", response_model=schemas.GeneralAndMortgage)
async def get_data(id: str):
    return await lib.get_parcel_data_from_county(id)


@app.get("/parcel/sync", response_model=schemas.GeneralAndMortgage)
async def sync(id: str, db: Session = Depends(get_db)):
    return await lib.sync_parcel_data(db, parcel_id=id)


@app.get("/municipality/sync", response_model=schemas.MunicipalitySyncData)
async def sync_municipality(municode: int, db: Session = Depends(get_db)):
    sync_data = schemas.MunicipalitySyncData(total=0, skipped=[])

    for parcel in lib.select_all_parcels_in_municode(db, municode=municode):
        success = None
        try:
            await lib.sync_parcel_data(db, parcel_id=parcel.parcelidcnty)
            success = True
        except HtmlParsingError:
            sync_data.skipped.append(parcel.parcelkey)
            success = False
        finally:
            sync_data.total += 1
            logger.info("Synced parcel", parcel_count=sync_data.total, skipped_count=len(sync_data.skipped), success=success)
            time.sleep(1)

    logger.info("Finished syncing municipality\n\n\n", municode=municode, skipped_count=len(sync_data.skipped), skipped_parcels=sync_data.skipped)
    return sync_data

