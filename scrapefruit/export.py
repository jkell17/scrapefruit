from typing import Dict, List

import jsonlines  # type: ignore


class Exporter:
    def __init__(self, output_file: str):
        self.file = output_file
        self.writer = jsonlines.open(self.file, "w")

    def write(self, item: Dict) -> None:
        self.writer.write(item)

    def shutdown(self) -> None:
        self.writer.close()

    def get_output(self) -> List[str]:
        result = []
        with jsonlines.open(self.file) as reader:
            for obj in reader:
                result.append(obj)
        return result
