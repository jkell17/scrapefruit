import logging

log_levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def create_logger(app):
    logger = logging.getLogger("ScrapeFruit.app")

    log_level = log_levels[app.config["LOG_LEVEL"]]
    logger.setLevel(log_level)

    default_handler = logging.StreamHandler()
    logger.addHandler(default_handler)

    file_ = app.config["LOG_FILE"]
    if file_:
        fileHandler = logging.FileHandler(file_)
        logger.addHandler(fileHandler)

    return logger
