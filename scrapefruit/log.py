import logging
from typing import Optional

import click


class DefaultFormatter(logging.Formatter):
    """
    A custom log formatter class that outputs
    the LOG_LEVEL with an appropriate color (if use_colors=True)

    Based on uvicorn: https://github.com/encode/uvicorn/blob/master/uvicorn/logging.py
    """

    level_name_colors = {
        logging.DEBUG: "blue",
        logging.INFO: "green",
        logging.WARNING: "yellow",
        logging.ERROR: "magenta",
        logging.CRITICAL: "red",
    }

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: str = "%",
        use_colors=True,
    ):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self.use_colors = use_colors

    def color_level_name(self, level_name: str, level_no: int) -> str:
        color = self.level_name_colors[level_no]
        return click.style(level_name, fg=color)

    def formatMessage(self, record: logging.LogRecord) -> str:
        levelname = record.levelname
        seperator = " " * (8 - len(record.levelname))
        if self.use_colors:
            levelname = self.color_level_name(levelname, record.levelno)
        record.__dict__["levelprefix"] = levelname + ":" + seperator
        return super().formatMessage(record)


def create_logger(log_level: str, log_file: Optional[str]) -> logging.Logger:
    """ ScrapeFruit logger has a stream handler and an optional log
    handler

    Arguments:
        log_level {str} -- Log severity
        log_file {str} -- Log file
    """
    logger = logging.getLogger("ScrapeFruit.app")
    level_no = getattr(logging, log_level)
    logger.setLevel(level_no)

    fmt = "%(levelprefix)s %(asctime)s || %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    # Stream handler (with colors)
    handler = logging.StreamHandler()
    handler.setFormatter(DefaultFormatter(fmt=fmt, datefmt=datefmt, use_colors=True))
    logger.addHandler(handler)

    # File handler (no colors)
    if log_file:
        fileHandler = logging.FileHandler(log_file)
        fileHandler.setFormatter(
            DefaultFormatter(fmt=fmt, datefmt=datefmt, use_colors=False)
        )
        logger.addHandler(fileHandler)

    return logger
