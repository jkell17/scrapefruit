import logging

from scrapefruit import ScrapeFruit


def test_set_log_level():
    LOG_LEVEL = "DEBUG"

    app = ScrapeFruit()
    app.config["LOG_LEVEL"] = LOG_LEVEL
    app.run()
    app.run()

    assert LOG_LEVEL == logging.getLevelName(app.logger.level)
