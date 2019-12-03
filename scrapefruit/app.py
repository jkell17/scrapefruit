import asyncio
from typing import List

from .crawler import Crawler
from .export import Exporter
from .log import create_logger
from .models import Request


class ScrapeFruit:

    queue: asyncio.Queue = asyncio.Queue()

    default_config = {
        "LOG_FILE": None,
        "LOG_LEVEL": "INFO",
        "OUTPUT_FILE": "output.jl",
        "WAIT": 0.5,
        "TIMEOUT": 10,
        "MAX_LEVEL": None,
    }

    def __init__(self):
        self.config = self.default_config
        self.logger = create_logger(self)
        self.export = Exporter(self)

    def start(self, urls: List[str]):
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

    def _execute(self, queue: asyncio.Queue, exporter):
        """Main function. Starts loop"""
        loop = asyncio.get_event_loop()
        self.logger.info("Starting crawler")
        self.crawler = Crawler(
            queue,
            self.logger,
            exporter,
            wait=self.config["WAIT"],
            timeout=self.config["TIMEOUT"],
        )
        loop.run_until_complete(self.crawler.crawl())

        self.logger.info("Crawler ended")
        loop.close()
        self.export.shutdown()

    def run(self):
        self._execute(self.queue, self.export)

    def export_output(self):
        return self.export.get_output()

    def end(self):
        self.crawler.shutdown()
