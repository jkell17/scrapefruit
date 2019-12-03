from typing import Callable, Dict, List, Optional
from urllib.parse import urljoin  # type: ignore

from parsel import Selector  # type: ignore


class Request:
    def __init__(
        self,
        url: str,
        callback: Callable,
        data: Dict = None,
        method: str = "GET",
        headers: Dict = None,
        body: Dict = None,
    ):
        self.url = url
        self.callback = callback
        self.data = data

        self.method = method
        self.headers = headers
        self.body = body

    def __repr__(self):
        return "{}; Callback:{}".format(self.url, self.callback.__name__)


class Response:
    def __init__(self, html: str, url: str, data: Optional[dict]):
        self.html = html
        self.url = url
        self.data = data

        self.sel = Selector(html)

    def css(self, r: str) -> List[Selector]:
        return self.sel.css(r)

    def xpath(self, r: str) -> List[Selector]:
        return self.sel.xpath(r)

    def urljoin(self, url: str) -> str:
        return urljoin(self.url, url)

    def __repr__(self):
        return "Response('{}')".format(self.url)
