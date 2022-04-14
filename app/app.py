from fastapi import FastAPI
from app import lib

app = FastAPI()


@app.get("/")
def root():
    return {"msg": "Hello, world 🌏"}


@app.get("/parcel/get-data")
def get_data(id: str):
    return lib.get_parcel_data(id)


@app.get("/parcel/sync")
def sync(id: str):
    parcel_data = lib.get_parcel_data(id)
    return lib.sync_parcel_data(parcel_data)
