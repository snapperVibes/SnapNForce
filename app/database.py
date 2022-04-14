from contextlib import contextmanager
from typing import Generator

from sqlalchemy.future import create_engine as sqlalchemy_create_engine
from sqlalchemy.engine import Engine, Connection


def _create_engine() -> Engine:
    _db_user = "sylvia"
    _db_password = "changeme"
    _host = "127.0.0.1"
    _port = "5432"
    _db_name = "cogdb"
    _engine_params = (
        f"postgresql+psycopg2://{_db_user}:{_db_password}@{_host}:{_port}/{_db_name}"
    )
    return sqlalchemy_create_engine(_engine_params,)


_db = _create_engine()


@contextmanager
def get_db() -> Generator[Connection, None, None]:
    with _db.connect() as connection:
        yield connection
