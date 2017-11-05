import aiohttp
import asyncio
import async_timeout

from .models import Response, Request

class Crawler:
	seen_urls = set()

	def __init__(self, queue, logger, output, wait, timeout, single_depth=False):
		self.queue = queue
		self.logger = logger
		self.exporter = output
		self.wait = wait
		self.timeout = timeout
		self.single_depth = single_depth # Used in debug mode. Will not add new urls to the queue.

	def shutdown(self):
		"""Empty the queue. Shut it down."""
		while not self.queue.empty():
			self.queue.get_nowait()
			self.queue.task_done()

	async def crawl(self):
		"""Startup function. Sets off fetcher and queues"""
		async with aiohttp.ClientSession() as session:
			fetcher = asyncio.ensure_future(self.engine(session))
			await self.queue.join()
			fetcher.cancel()

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
		sem = asyncio.Semaphore(100)
		with async_timeout.timeout(self.timeout):
			if request.method == 'GET':
				async with sem, session.get(request.url) as response:
					text = await response.text()
			elif request.method == 'POST':
				async with sem, session.post(request.url, data = request.body) as response:
					text = await response.text()
			self.logger.info("Fetched: {}".format(request.url))
			return Response(text, request.url, request.data)

	async def process_callback(self, callback, resp):

		result = callback(resp)

		if result is None:
			self.logger.warning("Nothing from {}; Callback({})".format(resp, callback.__name__))
			return

		result = iter(result)

		for item in result:
			if isinstance(item, Request):
				if item.url not in self.seen_urls and not self.single_depth:
					await self.queue.put(item)
					self.seen_urls.add(item.url)

			elif isinstance(item, dict):
				self.exporter.write(item)
				self.logger.info('Scraped {}'.format(item))
			else:
				self.logger.info('No item scraped')
