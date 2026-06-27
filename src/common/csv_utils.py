"""Small CSV helpers shared by scripts."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Iterable


def write_rows_csv(rows: Iterable[dict[str, Any]], path: str | Path) -> None:
    row_list = list(rows)
    if not row_list:
        return

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=list(row_list[0].keys()),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(row_list)


def read_rows_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))
