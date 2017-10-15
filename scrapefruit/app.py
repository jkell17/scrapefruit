import asyncio

from .models import Request, Response
from .log import create_logger
from .export import Exporter
from .crawler import Crawler

class ScrapeFruit:

	queue = asyncio.Queue()

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
		self.export = Exporter(self)

	def start(self, url):
		def decorator(f):
			req = Request(url,callback = f)
			self.queue.put_nowait(req)
			return f
		return decorator

	def run(self):
		"""Main function. Starts loop"""
		loop = asyncio.get_event_loop()
		self.logger.info('Starting crawler')

		crawler = Crawler(self.queue, self.logger, self.export, self.config)
		loop.run_until_complete(crawler.crawl())
		
		self.logger.info('Crawler ended')
		loop.close()
		self.export.shutdown()


	def export_output(self):
		return self.export.get_output()

	def test(self, url, callback):
		"""Empty the queue"""
		while not self.queue.empty():
			self.queue.get_nowait()
			self.queue.task_done()

		req = Request(url,callback = callback)
		self.queue.put_nowait(req)

		self.config['OUTPUT_FILE'] = 'test-'+ self.config['OUTPUT_FILE']
		self.export = Exporter(self)
		self.run()
		
		return self.export()