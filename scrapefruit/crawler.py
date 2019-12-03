import asyncio
import logging
from typing import Callable, Set

import aiohttp  # type: ignore
import async_timeout  # type: ignore

from .export import Exporter
from .models import Request, Response


class Crawler:
    seen_urls: Set[str] = set()

    def __init__(
        self,
        queue: asyncio.Queue,
        logger: logging.Logger,
        exporter: Exporter,
        wait: float,
        timeout: float,
        concurrency: int,
    ):
        self.queue = queue
        self.logger = logger
        self.exporter = exporter
        self.wait = wait
        self.timeout = timeout
        self.concurrency = concurrency

        self.sem = asyncio.Semaphore(concurrency)

    def shutdown(self) -> None:
        """Empty the queue. Shut it down."""
        while not self.queue.empty():
            self.queue.get_nowait()
            self.queue.task_done()

    async def crawl(self) -> None:
        """Startup function. Sets off fetcher and queues"""
        async with aiohttp.ClientSession() as session:
            workers = [
                asyncio.create_task(self.engine(session))
                for i in range(self.concurrency)
            ]
            await self.queue.join()
            for worker in workers:
                worker.cancel()

    async def engine(self, session: aiohttp.ClientSession) -> None:
        while True:
            req = await self.queue.get()
            try:
                resp = await self.fetch(session, req)
                await self.process_callback(req.callback, resp)
            except Exception as err:
                self.logger.error(err)
            self.queue.task_done()

    async def fetch(self, session: aiohttp.ClientSession, request: Request) -> Response:
        await asyncio.sleep(self.wait)
        with async_timeout.timeout(self.timeout):
            if request.method == "GET":
                async with self.sem, session.get(request.url) as response:
                    text = await response.text()
            elif request.method == "POST":
                async with self.sem, session.post(
                    request.url, data=request.body
                ) as response:
                    text = await response.text()
            self.logger.info("Fetched: {}".format(request.url))
            return Response(text, request.url, request.data)

    async def process_callback(self, callback: Callable, resp: Response) -> None:

        result = callback(resp)

        if result is None:
            self.logger.warning(
                "Nothing from {}; Callback({})".format(resp, callback.__name__)
            )
            return

        result = iter(result)

        for item in result:
            if isinstance(item, Request):
                if item.url not in self.seen_urls:
                    await self.queue.put(item)
                    self.seen_urls.add(item.url)

            elif isinstance(item, dict):
                self.exporter.write(item)
                self.logger.debug("Scraped {}".format(item))
