import asyncio
import sys
from pathlib import Path
from typing import Callable, List, Optional

from .crawler import Crawler, ReturnCode
from .export import Exporter
from .log import create_logger
from .models import Request


class ScrapeFruit:

    default_config = {
        "LOG_FILE": None,
        "LOG_LEVEL": "INFO",
        "OUTPUT_FILE": "output.jl",
        "WAIT": 0.5,
        "TIMEOUT": 10,
        "CONCURRENCY": 3,
        "MAX_RETRIES": 2,
    }

    def __init__(self, config: dict = {}):
        self.config = {**config, **self.default_config}
        self._starting_requests: List[Request] = []

    def _check_valid_config(self):
        """ Validate that user has not added
        any new keys, or deleted required ones
        """
        default_keys = self.default_config.keys()
        current_keys = self.config.keys()

        if default_keys != current_keys:
            msg = f"Config must have the following keys : {list(default_keys)}"
            self.logger.critical(msg)
            sys.exit(0)

    def crawl(self, url: str) -> Callable:
        # This decorator will add Request to q
        assert isinstance(url, str)

        def decorator(f):
            req = Request(url, callback=f)
            self._starting_requests.append(req)
            return f

        return decorator

    def crawl_many(self, urls: List[str]) -> Callable:
        # This decorator will add Request to either main queue or test queue:
        assert isinstance(urls, list)

        def decorator(f):
            for url in urls:
                req = Request(url, callback=f)
                self._starting_requests.append(req)
            return f

        return decorator

    def run(self) -> None:
        """Main function. Starts loop"""

        # These are set here, because user may
        # change settings (i.e. app.config['LOG_LEVEL] = 'DEBUG')
        # after instantiation
        self.logger = create_logger(self.config["LOG_LEVEL"], self.config["LOG_FILE"])

        self._check_valid_config()
        self.exporter = Exporter(self.config["OUTPUT_FILE"])
        self.crawler = Crawler(
            self.logger,
            self.exporter,
            wait=self.config["WAIT"],
            timeout=self.config["TIMEOUT"],
            concurrency=self.config["CONCURRENCY"],
            max_retries=self.config["MAX_RETRIES"],
        )

        self.logger.info("Starting crawler")
        indent = " " * 4
        for key, val in self.config.items():
            self.logger.info(f"{indent}{key}: {val}")

        # Create a new event loop for each execution
        # Allows run() to be called multiple times
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            rc = loop.run_until_complete(self.crawler.crawl(self._starting_requests))
        finally:
            loop.close()
            self.end()

        if rc == ReturnCode.SUCCESS:
            self.logger.info("Crawler ended successfully")
        else:
            self.logger.critical("Crawler ended with error")

    def end(self) -> None:
        self.exporter.shutdown()

    def clean_outputs(self) -> None:
        """ Delete logs and output file. Useful for testing.
        """

        def _delete_if_not_none(fn: Optional[str]) -> None:
            if fn is not None:
                Path(fn).unlink()

        _delete_if_not_none(self.config["LOG_FILE"])

        for file_ in self.exporter.get_all_files():
            file_.unlink()
