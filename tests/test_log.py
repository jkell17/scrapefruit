import logging

from scrapefruit import Request, ScrapeFruit


def test_set_log_level():
    LOG_LEVEL = "DEBUG"

    app = ScrapeFruit()
    app.config["LOG_LEVEL"] = LOG_LEVEL
    app.run()
    app.run()

    assert LOG_LEVEL == logging.getLevelName(app.logger.level)


def test_sample_scrape():

    app = ScrapeFruit()

    @app.start("http://www.thecrimson.com/")
    def start(resp):
        urls = resp.xpath(".//*[@class='article-content']/h2/a/@href").extract()
        for url in urls:
            # Crawl additional links
            yield Request(resp.urljoin(url), callback=callback)
            # Output results
            yield {"url": resp.urljoin(url)}

    def callback(resp):
        title = resp.xpath(".//*[@id='top']/text()").extract_first()
        yield {"url": resp.url, "title": title}

    app.run()
