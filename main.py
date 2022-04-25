import uvicorn
import logging
from os import path

logging.basicConfig(filename=path.join("log", "demo.log"), filemode="a")

if __name__ == "__main__":
    uvicorn.run("app.app:app", reload=True)
