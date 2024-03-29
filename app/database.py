import warnings
from sqlmodel import Session
from contextlib import contextmanager

from sqlalchemy.engine import Engine
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
        f"\nAn exception was handled while trying to read the password file:\n\t{type(err)}:{str(err)}.\n"
        f"Using development password instead.\n"
        f"Note: you can specify the password file using the PGPASS environment variable."
    )
    _db_password = "c0d3"

_engine_params = f"postgresql+psycopg2://{_db_user}:{_db_password}@{_host}:{_port}/{_db_name}"
_engine: Engine = create_engine(_engine_params, echo=True)
# to write to DB, turn this autocommit to True
SessionLocal = sessionmaker(autocommit=True, autoflush=False, bind=_engine)


def get_db():
    db = Session(_engine)
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    # For use outside FastAPI
    with Session(_engine) as conn:
        yield conn
