"""
    This file serves as an entrypoint to SnapNForce.
    After ensuring a "log" folder, main.py wraps the command `uvicorn app.app:app`.

    The purpose of this file is to simplify usage for the team.
    Telling someone to run `python main.py` is far less confusing than trying to explain why they should run `uvicorn app.app:app`

    For the interested: uvicorn is an ASGI web server implementation for Python.
    ASGI (Asynchronous Server Gateway Interface) is the asynchronous spiritual successor to WSGI.
    WSGI (Web Server Gateway Interface) is a standard interface between web servers and Python web applications and frameworks.

    uvicorn is the ASGI server, whereas FastAPI is the ASGI framework.
"""
import logging
import os

import uvicorn
from rich.console import Console
from rich.logging import RichHandler  # Pretty logs

if __name__ == "__main__":
    # Set up logging. You can watch the logs by running `tail -f log/sqlalchemy.engine.log` on the command line.
    #  (f stands for follolw)
    _LOG_FOLDER = "log"
    _SQL_FILE = "sqlalchemy.engine.log"
    SQL_FILE = os.path.join(_LOG_FOLDER, _SQL_FILE)
    if not os.path.exists(_LOG_FOLDER):
        os.makedirs(_LOG_FOLDER)
    with open(SQL_FILE, "a") as sql_file:
        rich_handler = RichHandler(console=Console(file=sql_file))
        rich_handler.setLevel(logging.DEBUG)
        sql_log = logging.getLogger("sqlalchemy.engine")
        sql_log.setLevel(logging.DEBUG)
        sql_log.handlers = [rich_handler]

        # Uvicorn.run is passed a string from which the web application is found.
        #  I have highlighted which "app" the string refers to
        #  In the folder "APP.app:app",
        #  In the file   "app.APP:app"
        #  The object    "app.app:APP"
        uvicorn.run("app.app:app", reload=False)
