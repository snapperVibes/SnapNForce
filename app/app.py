import logging
import random
import time

from fastapi import FastAPI, Depends
from sqlmodel import Session

from app import lib, schemas, orm
from app.database import get_db
from app.logging import logger
from lib.parse.exceptions import HtmlParsingError

app = FastAPI()


@app.get("/")
def root():
    globe = random.choice(["🌎", "🌍", "🌏"])
    return {"msg": f"Hello, world {globe}"}


@app.get("/parcel/muni_parcel_stats", response_model=schemas.MunicipalityParcelStats)
async def get_data(municode: str,  db: Session = Depends(get_db)):
    '''
    Check status of a municipality by its municode
    Parameters
    ----------
    municode
    about which to generate the statistics

    Returns
    -------
    The total number of parcels, the total parcels which the system believes are valid county entities

    '''
    return await lib.generate_muni_parcel_status(municode, db)


@app.get("/muni/get-muni-list", response_model=schemas.Munilist)
async def get_muni_list(db: Session = Depends(get_db)):
    return await lib.show_muni_list(db)


@app.get("/parcel/list-parcels-by-muni", response_model=schemas.ParcelList)
async def get_parcel_list_by_municode(municode: int, db: Session = Depends(get_db)):
    """
    Dump all the active records from the parcel table in JSON format into output, mostly useful
    for other robot users of the API to start with a full list of active parcels
    Parameters
    ----------
    municode
    :for the where clause
    db
    :the database

    Returns
    -------
    JSON encoded list of active parcels by muni
    """
    return await lib.get_parcelids_by_muni(municode, db)


@app.get("/parcel/get-data", response_model=schemas.GeneralAndMortgage)
async def get_data(county_parcel_id: str):
    """
    Scrapes a single county parcel ID from the county website for testing purposes
    Parameters
    ----------
    county_parcel_id
    :the parcel ID assigned by Allegheny County
    Returns
    -------
    JSON-encoded scraped data
    """
    return await lib.get_parcel_data_from_county(county_parcel_id)


@app.get("/parcel/sync", response_model=schemas.GeneralAndMortgage)
async def sync(id: str, municode: int, db: Session = Depends(get_db)):
    """
    Triggers the massive synchronize operation on a single parcel assigned to a single municipality
    Parameters
    ----------
    id
    :county assigned identifier
    municode
    :of the host municipality
    db
    :the database

    Returns
    -------
    Result of the synchronize operation, equal to the event log written onto the synced parcel
    """
    return await lib.sync_parcel_data(db, parcel_id=id, municode=municode)


@app.post("/bob/source", response_model=orm.BObSource)
async def create_bob_source(title: str, db: Session = Depends(get_db)):
    """
    Writes a new object source record to the bobsource table and by default
    attaches the source to cogland, municode 999
    Parameters
    ----------
    title
    :the name of the new source
    db

    Returns
    -------
    The new object with its ID
    """
    return await lib.write_bob_source(db, title=title)


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

