import asyncio
from pathlib import Path
from typing import Callable, List, Optional, Union

from .crawler import Crawler
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
    }

    def __init__(self, config: dict = {}):
        self.config = {**config, **self.default_config}

        self._starting_requests: List[Request] = []

    def start(self, urls: Union[str, List[str]]) -> Callable:
        # This decorator will add Request to either main queue or test queue:
        def decorator(f):
            if isinstance(urls, str):
                urls_as_list = [urls]
            else:
                urls_as_list = urls
            for url in urls_as_list:
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
        self.exporter = Exporter(self.config["OUTPUT_FILE"])
        self.crawler = Crawler(
            self.logger,
            self.exporter,
            wait=self.config["WAIT"],
            timeout=self.config["TIMEOUT"],
            concurrency=self.config["CONCURRENCY"],
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
            loop.run_until_complete(self.crawler.crawl(self._starting_requests))
        finally:
            loop.close()
            self.end()

    def end(self) -> None:
        self.exporter.shutdown()

    def clean_outputs(self) -> None:
        """ Delete logs and output file. Useful for testing.
        """

        def _delete_if_not_none(fn: Optional[str]) -> None:
            if fn is not None:
                Path(fn).unlink()

        _delete_if_not_none(self.config["LOG_FILE"])
        _delete_if_not_none(self.config["OUTPUT_FILE"])
