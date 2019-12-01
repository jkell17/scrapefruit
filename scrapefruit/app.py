import asyncio

from .crawler import Crawler
from .export import Exporter
from .log import create_logger
from .models import Request, Response


class ScrapeFruit:

    queue = asyncio.Queue()

    test_queue = asyncio.Queue()

    default_config = {
        "DEBUG": False,
        "LOG_FILE": None,
        "LOG_LEVEL": "DEBUG",
        "OUTPUT_FILE": "output.jl",
        "WAIT": 0.5,
        "TIMEOUT": 10,
        "MAX_LEVEL": None,
    }

    def __init__(self):
        self.config = self.default_config
        self.logger = create_logger(self)
        self.export = Exporter(self)

    def test(self, urls):
        # This decorator will add Request to either main queue or test queue:
        def decorator(f):
            if isinstance(urls, str):
                urls_as_list = [urls]
            else:
                urls_as_list = urls
            for url in urls_as_list:
                req = Request(url, callback=f)
                self.test_queue.put_nowait(req)
            return f

        return decorator

    def start(self, urls):
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

    def _execute(self, queue, logger, exporter, single_depth):
        """Main function. Starts loop"""
        loop = asyncio.get_event_loop()
        self.logger.info("Starting crawler")

        self.crawler = Crawler(
            queue,
            logger,
            exporter,
            wait=self.config["WAIT"],
            timeout=self.config["TIMEOUT"],
            single_depth=single_depth,
        )
        loop.run_until_complete(self.crawler.crawl())

        self.logger.info("Crawler ended")
        loop.close()
        self.export.shutdown()

    def run(self):
        self._execute(self.queue, self.logger, self.export, single_depth=False)

    def export_output(self):
        return self.export.get_output()

    def end(self):
        self.crawler.shutdown()

    def run_tests(self):
        # Set output file to test file
        self.config["OUTPUT_FILE"] = "test-" + self.config["OUTPUT_FILE"]
        self.export = Exporter(self)  #

        self._execute(self.test_queue, self.logger, self.export, single_depth=True)

        return self.export_output()
