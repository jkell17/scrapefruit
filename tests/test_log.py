import logging

from scrapefruit import ScrapeFruit


def test_set_log_level():
    LOG_LEVEL = "DEBUG"

    app = ScrapeFruit()
    app.config["LOG_LEVEL"] = LOG_LEVEL
    app.run()
    app.clean_outputs()
    assert LOG_LEVEL == logging.getLevelName(app.logger.level)


def test_log_file():
    LOG_FILE = "test.log"

    app = ScrapeFruit()
    app.config["LOG_FILE"] = LOG_FILE
    app.run()

    with open(LOG_FILE) as f:
        logs = f.read()
        assert "Starting crawler" in logs
    app.clean_outputs()
