import logging
import os

import structlog
from structlog.stdlib import LoggerFactory

_LOG_FOLDER = "log"
if not os.path.exists(_LOG_FOLDER):
    os.makedirs(_LOG_FOLDER)
logging.basicConfig(
    filename=os.path.join(_LOG_FOLDER, "server.log"), filemode="a", level=logging.DEBUG
)
structlog.configure(logger_factory=LoggerFactory())
logger = structlog.get_logger()
logger.format = "%(asctime)s\t%(name)s:%(levelname)s\t%(message)s"
