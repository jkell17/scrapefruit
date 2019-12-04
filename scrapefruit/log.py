import logging
from typing import Optional

import click


class ColourizedFormatter(logging.Formatter):
    """
    A custom log formatter class that outputs
    the LOG_LEVEL with an appropriate color.

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
        self, fmt: Optional[str] = None, datefmt: Optional[str] = None, style: str = "%"
    ):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def color_level_name(self, level_name: str, level_no: int) -> str:
        color = self.level_name_colors[level_no]
        return click.style(level_name, fg=color)

    def formatMessage(self, record: logging.LogRecord) -> str:
        levelname = record.levelname
        seperator = " " * (8 - len(record.levelname))
        levelname = self.color_level_name(levelname, record.levelno)
        record.__dict__["levelprefix"] = levelname + ":" + seperator
        return super().formatMessage(record)


def create_logger(log_level: str, log_file: str) -> logging.Logger:
    handler = logging.StreamHandler()
    handler.setFormatter(
        ColourizedFormatter(
            fmt="%(levelprefix)s %(asctime)s || %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    logger = logging.getLogger("ScrapeFruit.app")
    logger.addHandler(handler)
    level_no = getattr(logging, log_level)
    logger.setLevel(level_no)

    file_ = log_file
    if file_:
        fileHandler = logging.FileHandler(file_)
        logger.addHandler(fileHandler)

    return logger
