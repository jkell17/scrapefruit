import asyncio
from typing import Set

import aiohttp
import async_timeout

from .models import Request, Response


class Crawler:
    seen_urls: Set[str] = set()

    def __init__(self, queue, logger, output, wait, timeout, concurrency):
        self.queue = queue
        self.logger = logger
        self.exporter = output
        self.wait = wait
        self.timeout = timeout
        self.concurrency = concurrency

        self.sem = asyncio.Semaphore(concurrency)

    def shutdown(self):
        """Empty the queue. Shut it down."""
        while not self.queue.empty():
            self.queue.get_nowait()
            self.queue.task_done()

    async def crawl(self):
        """Startup function. Sets off fetcher and queues"""
        async with aiohttp.ClientSession() as session:
            workers = [
                asyncio.create_task(self.engine(session))
                for i in range(self.concurrency)
            ]
            await self.queue.join()
            for worker in workers:
                worker.cancel()

    async def engine(self, session):
        while True:
            req = await self.queue.get()
            try:
                resp = await self.fetch(session, req)
                await self.process_callback(req.callback, resp)
            except Exception as err:
                self.logger.error(err)
            self.queue.task_done()

    async def fetch(self, session, request):
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

    async def process_callback(self, callback, resp):

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
