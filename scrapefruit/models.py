from dataclasses import dataclass
from typing import Callable, Dict, Optional
from urllib.parse import urljoin  # type: ignore

from parsel import Selector  # type: ignore


@dataclass
class Request:
    url: str
    callback: Callable
    data: Optional[Dict] = None
    method: str = "GET"
    headers: Optional[Dict] = None
    body: Optional[Dict] = None
    attempts: int = 0


@dataclass
class Response:
    html: str
    url: str
    data: Optional[Dict] = None

    def css(self, r: str) -> Selector:
        return Selector(self.html).css(r)

    def xpath(self, r: str) -> Selector:
        return Selector(self.html).xpath(r)

    def urljoin(self, url: str) -> str:
        return urljoin(self.url, url)


@dataclass
class Record:
    data: Dict
    save_to: str
    format: str

    def ___post_init__(self):

        # Check if valid format
        assert self.format.upper() in ("JSONLINES")
