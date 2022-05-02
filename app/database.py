import warnings
from collections import namedtuple
from contextlib import contextmanager

from sqlalchemy import MetaData
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import create_engine
from sqlalchemy.orm import sessionmaker

from lib.vendor import pgpasslib


_db_user = "sylvia"
_host = "127.0.0.1"
_port = "5432"
_db_name = "cogdb"
try:
    _db_password = pgpasslib.getpass(host=_host, port=_port, dbname=_db_name, user=_db_user)
except pgpasslib.PgPassException as err:
    warnings.warn(
        f"\nAn exception was handled while trying to read the password file:\n\t{type(err)}:{str(err)}.\nUsing development password instead.\nNote: you can specify the password file using the PGPASS environment variable."
    )
    _db_password = "changeme"

_engine_params = f"postgresql+psycopg2://{_db_user}:{_db_password}@{_host}:{_port}/{_db_name}"
_engine: Engine = create_engine(_engine_params, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
metadata = MetaData()
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    # For use outside of FastAPI
    with _engine.connect() as conn:
        yield conn
