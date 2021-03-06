import json  # type: ignore
import logging
from pathlib import Path
from typing import Dict, List, Set

from .models import Record

logger = logging.getLogger("ScrapeFruit.app")


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
        logger.debug(f"Saved {formatted_line} to {self.filepath}")
        self.opened_fp.write(formatted_line)
        self.opened_fp.write("\n")
        self.opened_fp.flush()


class CSVWriter(Writer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.columns: List[str] = []

    def write(self, data):

        columns = sorted([i for i in data.keys()])

        # Formatted line
        formatted_line = ",".join([f"'{data[i]}'" for i in columns])

        # First record, set header row
        if len(self.columns) == 0:
            self.columns = columns
            header_line = ",".join([f"'{i}'" for i in columns])
            self.opened_fp.write(header_line)
            self.opened_fp.write("\n")
            self.opened_fp.flush()

        if self.columns != columns:
            logger.error(
                f"Invalid columns. For CSV format, all items must have the same keys. Skipping {data}"
            )
            return

        logger.debug(f"Saved {formatted_line} to {self.filepath}")
        self.opened_fp.write(formatted_line)
        self.opened_fp.write("\n")
        self.opened_fp.flush()


class Exporter:
    def __init__(self, default_out_file: str, default_out_format: str):
        self.default_out_file = default_out_file
        self.default_out_format = default_out_format

        writer = create_writer(default_out_file, default_out_format)
        self.writers: Dict[str, Writer] = {self.default_out_file: writer}

    def write_dict(self, item: Dict) -> None:
        record = Record(
            data=item,
            save_to=str(self.default_out_file),
            format=self.default_out_format,
        )
        self.write_record(record)

    def get_all_files(self) -> Set[Path]:
        # Convert to Paths
        return set([Path(i) for i in self.writers.keys()])

    def write_record(self, record: Record) -> None:

        # Get file pointer
        if record.save_to not in self.writers:
            self.writers[record.save_to] = create_writer(record.save_to, record.format)

        writer = self.writers[record.save_to]
        writer.write(record.data)

    def shutdown(self) -> None:
        for writer in self.writers.values():
            writer.close()


def write_json_line_record(data, fp):
    formatted_line = json.dumps(data)
    fp.write(formatted_line)
    fp.write("\n")


def create_writer(out_file: str, out_format: str) -> Writer:
    if out_format.upper() == "JSONLINES":
        return JsonlinesWriter(Path(out_file))
    elif out_format.upper() == "CSV":
        return CSVWriter(Path(out_file))
    else:
        raise ValueError
