import sys
from pathlib import Path  # noqa E402
from typing import List

from setuptools import setup

assert sys.version_info >= (3, 7, 0), "Requires Python 3.7+"

CURRENT_DIR = Path(__file__).parent


NAME = "scrapefruit"
VERSION = "0.0.1"


def get_requirements() -> List[str]:

    with open(CURRENT_DIR / "requirements.txt") as f:
        return f.read().split("\n")


if __name__ == "__main__":
    setup(name=NAME, version=VERSION, install_requires=get_requirements())
