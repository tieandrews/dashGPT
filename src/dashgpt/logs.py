# INspired from Son Nguyen Kim gist here: https://gist.github.com/nguyenkims/e92df0f8bd49973f0c94bddf36ed7fd0
import logging
import sys, os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime as dt


FORMATTER = logging.Formatter(
    "%(asctime)s - %(filename)s:%(lineno)s - %(funcName)s - %(levelname)s - %(message)s"
)

LOG_FILE = os.environ.get("LOG_OUTPUT_DIR", "") + dt.now().strftime(
    "logs_%Y-%m-%dT%H-%M-%S.log"
)

LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG").upper()


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    file_handler = TimedRotatingFileHandler(LOG_FILE, when="midnight")
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(get_console_handler())
    # logger.addHandler(get_file_handler())

    gunicorn_logger = logging.getLogger("gunicorn.error")
    for h in gunicorn_logger.handlers:
        logger.addHandler(h)

    logger.setLevel(LOG_LEVEL)  # better to have too much log than not enough

    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False

    return logger
