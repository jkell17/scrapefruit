
ScrapeFruit
===========
ScrapeFruit is a microframework to build asynchronous webscrapers in Python. Built on top of aiohttp, with inspiration from Flask.


```python
from scrapefruit import Request, ScrapeFruit

app = ScrapeFruit()
app.config["WAIT"] = 1  # Be slow.


@app.crawl("http://www.thecrimson.com/")
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


if __name__ == "__main__":
    app.run()
```
