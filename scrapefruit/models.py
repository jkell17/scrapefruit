from urllib.parse import urljoin

from parsel import Selector


class Request:
    def __init__(self, url, callback, data=None, method="GET", headers=None, body=None):
        self.url = url
        self.callback = callback
        self.data = data

        self.method = method
        self.headers = headers
        self.body = body

    def __repr__(self):
        return "{}; Callback:{}".format(self.url, self.callback.__name__)


class Response:
    def __init__(self, html, url, data):
        self.html = html
        self.url = url
        self.data = data

        self.sel = Selector(html)

    def css(self, r):
        return self.sel.css(r)

    def xpath(self, r):
        return self.sel.xpath(r)

    def urljoin(self, url):
        return urljoin(self.url, url)

    def __repr__(self):
        return "Response('{}')".format(self.url)
