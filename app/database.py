from contextlib import contextmanager
from typing import Generator

from sqlalchemy import text, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import create_engine
from sqlalchemy.engine import Engine, Connection


_db_user = "sylvia"
_db_password = "changeme"
_host = "127.0.0.1"
_port = "5432"
_db_name = "cogdb"
_engine_params = f"postgresql+psycopg2://{_db_user}:{_db_password}@{_host}:{_port}/{_db_name}"
_engine: Engine = create_engine(_engine_params, echo=True)
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
def _get_db2():
    with _engine.connect() as conn:
        yield conn
