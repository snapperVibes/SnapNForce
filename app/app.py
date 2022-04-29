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
def get_data(id: str):
    return lib.get_parcel_data_from_county(id)


@app.get("/parcel/sync", response_model=schemas.GeneralAndMortgage)
def sync(id: str, db: Session = Depends(get_db)):
    return lib.sync_parcel_data(db, parcel_id=id)
