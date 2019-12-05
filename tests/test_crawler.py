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
    app.config["WAIT"] = 0.5  # Be slow.
    app.config["LOG_LEVEL"] = "DEBUG"
    app.config["CONCURRENCY"] = 5

    @app.crawl("https://news.ycombinator.com/")
    def start(resp):

        comment_urls = resp.xpath("//td[2]/a[3]/@href").extract()
        for url in comment_urls:
            # Crawl additional links
            yield Request(resp.urljoin(url), callback=callback)
            # Output results
            yield {"url": resp.urljoin(url)}

    def callback(resp):
        first_user_name = resp.xpath("//td[3]/div[1]/span/a[1]/text()").extract_first()
        yield {"first_comment_username": first_user_name}

    app.run()
    app.clean_outputs()
