import random

from fastapi import FastAPI, Depends
from sqlmodel import Session

from app import lib, schemas
from app.database import get_db

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
