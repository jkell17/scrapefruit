from scrapefruit import Request, ScrapeFruit


def test_run_twice():

    app = ScrapeFruit()
    app.run()

    app = ScrapeFruit()
    app.run()
    app.run()

    app.clean_outputs()


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
    app.clean_outputs()
