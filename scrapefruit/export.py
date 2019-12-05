import json  # type: ignore
from pathlib import Path
from typing import Dict, Set, TextIO

from .models import Record


class Exporter:
    def __init__(self, output_file: str):
        self.default_out_file = Path(output_file)
        self.out_files: Dict[Path, TextIO] = {
            self.default_out_file: open(self.default_out_file, "w")
        }

    def write_dict(self, item: Dict) -> None:
        fp = self.out_files[self.default_out_file]
        write_json_line_record(item, fp)

    def get_all_files(self) -> Set[Path]:
        return set(self.out_files.keys())

    def write_record(self, record: Record) -> None:
        save_to_path = Path(record.save_to)

        # Get file pointer
        if record.save_to not in self.out_files:
            self.out_files[save_to_path] = open(save_to_path, "w")
        fp = self.out_files[save_to_path]

        if record.format.upper() == "JSONLINES":
            write_json_line_record(record.data, fp)

    def shutdown(self) -> None:
        for val in self.out_files.values():
            val.close()


def write_json_line_record(data, fp):
    formatted_line = json.dumps(data)
    fp.write(formatted_line)
    fp.write("\n")
