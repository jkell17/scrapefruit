import json  # type: ignore
from pathlib import Path
from typing import Dict, Set, TextIO

from .models import Record


class Writer:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.opened_fp = open(filepath, "w")

    def write(self, data):
        pass

    def close(self):
        self.opened_fp.close()


class JsonlinesWriter(Writer):
    def write(self, data):
        formatted_line = json.dumps(data)
        self.opened_fp.write(formatted_line)
        self.opened_fp.write("\n")


class Exporter:
    def __init__(self, default_out_file: str, default_out_format: str):
        writer = create_writer(default_out_file, default_out_format)

        self.default_out_file = Path(default_out_file)

        self.out_files: Dict[Path, TextIO] = {
            self.default_out_file: open(self.default_out_file, "w")
        }

        self.writers: Dict[Path, Writer] = {self.default_out_file: writer}

    def write_dict(self, item: Dict) -> None:
        fp = self.out_files[self.default_out_file]
        write_json_line_record(item, fp)

    def get_all_files(self) -> Set[Path]:
        return set(self.out_files.keys())

    def write_record(self, record: Record) -> None:
        save_to_path = Path(record.save_to)

        # # Get file pointer
        if record.save_to not in self.out_files:
            self.out_files[save_to_path] = open(save_to_path, "w")
        fp = self.out_files[save_to_path]

        if record.format.upper() == "JSONLINES":
            write_json_line_record(record.data, fp)

    def shutdown(self) -> None:
        for val in self.out_files.values():
            val.close()

        for writer in self.writers.values():
            writer.close()


def write_json_line_record(data, fp):
    formatted_line = json.dumps(data)
    fp.write(formatted_line)
    fp.write("\n")


def create_writer(out_file: str, out_format: str) -> Writer:
    if out_format.upper() == "JSONLINES":
        return JsonlinesWriter(Path(out_file))
    else:
        print(out_format)
        raise ValueError
