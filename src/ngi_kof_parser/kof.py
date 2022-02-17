"""
Common super class for the KOFReader() and KOFWriter() classes
"""
import csv
from pathlib import Path
from typing import Dict, Optional


def get_srid_to_code_mapping() -> Dict[int, int]:
    field_names = ["name", "description", "code", "srid"]
    path = Path(__file__).parent.absolute()
    result = {}
    with open(path / "KoordSys.csv", mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file, fieldnames=field_names, delimiter=";")
        for row in csv_reader:
            result[int(row["srid"])] = int(row["code"])

    return result


_srid_to_code_mapping = get_srid_to_code_mapping()
_code_to_srid_mapping = {value: key for (key, value) in _srid_to_code_mapping.items()}


class Kof:
    def __init__(self):
        self.srid_to_code_mapping = _srid_to_code_mapping
        self.code_to_srid_mapping = _code_to_srid_mapping

    def get_srid(self, code: int) -> Optional[int]:
        return self.code_to_srid_mapping.get(code)

    def get_code(self, srid: int) -> Optional[int]:
        return self.srid_to_code_mapping.get(srid)
