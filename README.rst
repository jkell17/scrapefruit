
ScrapeFruit: HTTP for Humans
=========================
ScrapeFruit is a microframework to build asynchronous webscrapers in Python. Built on top of aiohttp, with inspiration from Flask.

	
.. code:: python
	from scrapefruit import ScrapeFruit, Request
	app = ScrapeFruit()
	app.config['WAIT'] = 1 # Be slow!

	@app.start('http://www.thecrimson.com/')
	def start(resp):
		urls = resp.xpath(".//*[@class='article-content']/h2/a/@href").extract()
		for url in urls:
			# Crawl additional links
			yield Request(resp.urljoin(url), callback = callback)
			# Output results
			yield {'url': resp.urljoin(url)}

	def callback(resp):
		title = resp.xpath(".//*[@id='top']/text()").extract_first()
		yield {"url": resp.url, "title": title}
