import logging
import os

import uvicorn

if __name__ == "__main__":
    _LOG_FOLDER = "log"
    if not os.path.exists(_LOG_FOLDER):
        os.makedirs(_LOG_FOLDER)
    logging.basicConfig(filename=os.path.join(_LOG_FOLDER, "demo.log"), filemode="a")

    uvicorn.run("app.app:app", reload=True)
