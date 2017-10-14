import aiohttp
import asyncio
import async_timeout
from .models import Request, Response
from .log import create_logger
from .output import Outputter

class ScrapeFruit(object):

	queue = asyncio.Queue()

	seen_urls = set()

	default_config = {
        'DEBUG':		False,
        'LOG_FILE':		None,
        'LOG_LEVEL':	'DEBUG',
        'OUTPUT_FILE':	'output.jl',
        'WAIT':			0.5,
        'TIMEOUT':		10,
        'MAX_LEVEL':	None,
    }

	def __init__(self):
		self.config = self.default_config
		self.logger = create_logger(self)
		self.output = Outputter(self)

	def start(self, url):
		def decorator(f):
			req = Request(url,callback = f)
			self.queue.put_nowait(req)
			self.seen_urls.add(url)
			return f
		return decorator

	def run(self):
		"""Main function. Starts loop"""
		loop = asyncio.get_event_loop()
		self.logger.info('Starting crawler')

		loop.run_until_complete(self.crawl())
		
		self.logger.info('Crawler ended')
		loop.close()
		self.output.shutdown()


	async def crawl(self):
		"""Crawl function. Sets off fetcher and queues"""
		async with aiohttp.ClientSession() as session:
			fetcher = asyncio.ensure_future(self.engine(session))
			await self.queue.join()
			fetcher.cancel()

	async def engine(self, session):
		while True:
			req = await self.queue.get()
			resp = await self.fetch(session, req)
			result = await self.process_callback(req.callback, resp)
			self.queue.task_done()

	async def fetch(self, session, request):
		await asyncio.sleep(self.config['WAIT'])
		sem = asyncio.Semaphore(100)
		with async_timeout.timeout(self.config['TIMEOUT']):
			async with sem, session.get(request.url) as response:
				text = await response.text()
				self.logger.info("Fetched: {}".format(request.url))
				return Response(text, request.url ,request.data)	

	async def process_callback(self, callback, resp):
		result = callback(resp)
		for item in result:
			if isinstance(item, Request):
				if item.url not in self.seen_urls:
					await self.queue.put(item)
					self.seen_urls.add(item.url)
			else:
				self.output.write(item)
				self.logger.info('Scraped: {}'.format(item))

	def export(self):
		return self.output.get_output()


	def test(self, url, callback):
		"""Empty the queue"""
		while not self.queue.empty():
			self.queue.get_nowait()
			self.queue.task_done()

		req = Request(url,callback = callback)
		self.queue.put_nowait(req)

		self.config['OUTPUT_FILE'] = 'test-'+ self.config['OUTPUT_FILE']
		self.output = Outputter(self)
		self.run()
		
		return self.export()