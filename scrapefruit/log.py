import logging

log_levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def create_logger(app):

    logging.basicConfig(
        level=log_levels[app.config["LOG_LEVEL"]],
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger("ScrapeFruit.app")

    file_ = app.config["LOG_FILE"]
    if file_:
        fileHandler = logging.FileHandler(file_)
        logger.addHandler(fileHandler)

    return logger
