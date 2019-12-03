import logging

log_levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def create_logger(log_level: str, log_file: str) -> logging.Logger:

    logging.basicConfig(
        level=log_levels[log_level],
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger("ScrapeFruit.app")

    file_ = log_file
    if file_:
        fileHandler = logging.FileHandler(file_)
        logger.addHandler(fileHandler)

    return logger
