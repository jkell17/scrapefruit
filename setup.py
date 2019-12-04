import sys
from pathlib import Path
from typing import List

from setuptools import find_packages, setup  # type: ignore

assert sys.version_info >= (3, 7, 0), "Requires Python 3.7+"

CURRENT_DIR = Path(__file__).parent

MAJOR = 0
MINOR = 0
MICRO = 3


NAME = "scrapefruit-jfk"
VERSION = f"{MAJOR}.{MINOR}.{MICRO}"


def get_requirements() -> List[str]:

    with open(CURRENT_DIR / "requirements.txt") as f:
        return f.read().split("\n")


def get_long_description() -> str:

    with open(CURRENT_DIR / "README.md") as f:
        return f.read()


if __name__ == "__main__":

    setup(
        name=NAME,
        version=VERSION,
        author="Jimmy Kelleher",
        author_email="kelleher.jimmy@gmail.com",
        description="A microframework to build asynchronous webscrapers in Python",
        long_description=get_long_description(),
        long_description_content_type="text/markdown",
        url="https://github.com/jkell17/scrapefruit",
        packages=find_packages(),
        install_requires=get_requirements(),
        python_requires=">=3.7",
    )
