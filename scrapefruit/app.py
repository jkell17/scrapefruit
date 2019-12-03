import asyncio
from typing import Callable, List

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
        "MAX_LEVEL": None,
        "CONCURRENCY": 3,
    }

    def __init__(self, config: dict = {}):
        self.config = {**config, **self.default_config}
        self.logger = create_logger(self.config["LOG_LEVEL"], self.config["LOG_FILE"])
        self.exporter = Exporter(self.config["OUTPUT_FILE"])
        self.queue: asyncio.Queue = asyncio.Queue()

    def start(self, urls: List[str]) -> Callable:
        # This decorator will add Request to either main queue or test queue:
        def decorator(f):
            if isinstance(urls, str):
                urls_as_list = [urls]
            else:
                urls_as_list = urls
            for url in urls_as_list:
                req = Request(url, callback=f)
                self.queue.put_nowait(req)
            return f

        return decorator

    def run(self) -> None:
        """Main function. Starts loop"""
        loop = asyncio.get_event_loop()
        self.logger.info("Starting crawler")
        self.crawler = Crawler(
            self.queue,
            self.logger,
            self.exporter,
            wait=self.config["WAIT"],
            timeout=self.config["TIMEOUT"],
            concurrency=self.config["CONCURRENCY"],
        )
        loop.run_until_complete(self.crawler.crawl())

        self.logger.info("Crawler ended")
        loop.close()
        self.exporter.shutdown()

    def end(self) -> None:
        self.crawler.shutdown()
