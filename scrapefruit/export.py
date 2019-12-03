import json  # type: ignore
from typing import Dict


class Exporter:
    def __init__(self, output_file: str):
        self.file = output_file
        self.writer = open(self.file, "w")

    def write(self, item: Dict) -> None:
        self.writer.write(json.dumps(item))
        self.writer.write("\n")

    def shutdown(self) -> None:
        self.writer.close()
