from collections import namedtuple
from contextlib import contextmanager

from sqlalchemy import MetaData
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import create_engine
from sqlalchemy.orm import sessionmaker

_Settings = namedtuple("_Settings", ["hostname", "port", "database", "username", "password"])

# https://www.postgresql.org/docs/current/libpq-pgpass.html
# def _parse_passwordfile(filename: str) -> list[_Settings]:
#     with open(filename, "r") as f:
#         original_lines = f.readlines()
#     pattern = re.compile(r"(.*?)(#.*)?")
#     lines = filter(lambda x: x == "", [re.split(pattern, line)[1].strip() for line in original_lines])
#     pattern = re.compile(r"[^\\]:")
#     return [_Settings(*re.split(pattern, line)[1:]) for line in lines]
#
# settings = _parse_passwordfile(PASSWORD_FILE)
# if len(settings) > 1:
#     raise RuntimeError("Multiple users are listed in the password file.")
# settings = settings[0]


_db_user = "sylvia"
_db_password = "changeme"
_host = "127.0.0.1"
_port = "5432"
_db_name = "cogdb"
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
