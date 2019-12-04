import asyncio
import logging
import traceback
from typing import Callable, List, Set

import aiohttp  # type: ignore
import async_timeout  # type: ignore

from .export import Exporter
from .models import Request, Response


class Crawler:
    seen_urls: Set[str] = set()

    def __init__(
        self,
        logger: logging.Logger,
        exporter: Exporter,
        wait: float,
        timeout: float,
        concurrency: int,
    ):
        self.logger = logger
        self.exporter = exporter
        self.wait = wait
        self.timeout = timeout
        self.concurrency = concurrency
        self.sem = asyncio.Semaphore(concurrency)

    def shutdown(self, success: bool = True) -> None:
        """Empty the queue. Shut it down."""
        while not self.queue.empty():
            self.queue.get_nowait()
            self.queue.task_done()

        if success:
            self.logger.info("Crawler ended succesfully")
        else:
            self.logger.error("Crawler ended with error")

    async def crawl(self, requests: List[Request]) -> None:
        self.queue: asyncio.Queue = asyncio.Queue()
        for request in requests:
            self.queue.put_nowait(request)

        """Startup function. Sets off fetcher and queues"""
        async with aiohttp.ClientSession() as session:
            workers = [
                asyncio.create_task(self.worker(session))
                for i in range(self.concurrency)
            ]
            await self.queue.join()
            for worker in workers:
                worker.cancel()

    async def worker(self, session: aiohttp.ClientSession) -> None:

        while True:
            req = await self.queue.get()

            # Check if seen request previousy
            if req.url in self.seen_urls:
                self.logger.warning(f"Skipped duplicate url: {req.url}")
                self.queue.task_done()
                continue
            else:
                self.seen_urls.add(req.url)

            try:
                resp = await self.fetch(session, req)
                await self.process_callback(req.callback, resp)
            except Exception:
                self.logger.error(f"Error fetching: {req.url}")
                traceback.print_exc()

                self.shutdown(success=False)

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
        """ Execute callback on response. Write results to Exporter, or
        add Requests to queue.

        Arguments:
            callback {Callable} -- Callback function
            resp {Response} -- Response
        """

        result = callback(resp)

        if result is None:
            self.logger.warning(
                "Nothing from {}; Callback({})".format(resp, callback.__name__)
            )
            return

        result = iter(result)
        for item in result:
            if isinstance(item, Request):
                await self.queue.put(item)
            elif isinstance(item, dict):
                self.exporter.write(item)
                self.logger.debug("Scraped {}".format(item))
            else:
                self.logger.error(
                    f"`{callback.__name__}` yields a {type(item)}. Can only yield `Request` objects or `dict`"
                )
