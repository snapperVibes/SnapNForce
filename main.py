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

if __name__ == "__main__":
    _LOG_FOLDER = "log"
    if not os.path.exists(_LOG_FOLDER):
        os.makedirs(_LOG_FOLDER)
    logging.basicConfig(filename=os.path.join(_LOG_FOLDER, "demo.log"), filemode="a")

    # Uvicorn.run is passed a string from which the web application is found.
    # I have highlighted which "app" the string refers to
    # In the folder "APP.app:app",
    # In the file   "app.APP:app"
    # The object    "app.app:APP"
    uvicorn.run("app.app:app", reload=False)
