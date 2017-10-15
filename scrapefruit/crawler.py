import aiohttp
import asyncio
import async_timeout

from .models import Response, Request

class Crawler:
	seen_urls = set()

	def __init__(self, queue, logger, output, config):
		self.queue = queue
		self.logger = logger
		self.exporter = output
		self.config = config

	async def crawl(self):
		"""Startup function. Sets off fetcher and queues"""
		async with aiohttp.ClientSession() as session:
			fetcher = asyncio.ensure_future(self.engine(session))
			await self.queue.join()
			fetcher.cancel()

	async def engine(self, session):
		while True:
			req = await self.queue.get()
			resp = await self.fetch(session, req)
			
			await self.process_callback(req.callback, resp)
			self.queue.task_done()

	async def fetch(self, session, request):
		await asyncio.sleep(self.config['WAIT'])
		sem = asyncio.Semaphore(100)
		with async_timeout.timeout(self.config['TIMEOUT']):
			async with sem, session.get(request.url) as response:
				text = await response.text()
				self.logger.info("Fetched: {}".format(request.url))
				return Response(text, request.url, request.data)	

	async def process_callback(self, callback, resp):
		result = callback(resp) # This will either be a dict or a Request object
		for item in result:
			if isinstance(item, Request):
				if item.url not in self.seen_urls:
					await self.queue.put(item)
					self.seen_urls.add(item.url)
			else:
				self.exporter.write(item)
				self.logger.info('Scraped: {}'.format(item))