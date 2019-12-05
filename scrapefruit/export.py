import json  # type: ignore
from typing import Dict, TextIO

from .models import Record


class Exporter:
    def __init__(self, output_file: str):
        self.file = output_file
        self.default_writer = open(self.file, "w")

        self.out_files: Dict[str, TextIO] = {}

    def write_dict(self, item: Dict) -> None:
        self.default_writer.write(json.dumps(item))
        self.default_writer.write("\n")

    def write_record(self, record: Record) -> None:
        if record.format.upper() == "JSONLINES":
            formatted_line = json_lines_formater(record.data)

        if record.save_to not in self.out_files:
            self.out_files[record.save_to] = open(record.save_to, "w")

        fp = self.out_files[record.save_to]
        fp.write(formatted_line)
        fp.write("\n")

    def shutdown(self) -> None:
        self.default_writer.close()

        for val in self.out_files.values():
            val.close()


def json_lines_formater(record_dict):
    return json.dumps(record_dict)
