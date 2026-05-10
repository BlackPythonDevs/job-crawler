from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class BoardEntry:
    url: str
    departments: tuple[str, ...] = field(default_factory=tuple)

    def allows(self, department: str) -> bool:
        if not self.departments:
            return True
        target = department.strip().casefold()
        return any(d.strip().casefold() == target for d in self.departments)


@dataclass(frozen=True)
class BoardConfig:
    boards: tuple[BoardEntry, ...]


def load_board_config(path: str | Path) -> BoardConfig:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"Board config not found at {p}. Set JOB_CRAWLER_CONFIG or create the file."
        )
    with p.open("rb") as f:
        data = tomllib.load(f)

    raw_boards = data.get("boards") or []
    if not raw_boards:
        raise ValueError(
            f"Board config at {p} has no [[boards]] entries."
        )

    boards: list[BoardEntry] = []
    for i, entry in enumerate(raw_boards):
        url = entry.get("url")
        if not url:
            raise ValueError(f"[[boards]] entry #{i} missing required 'url'")
        departments = tuple(entry.get("departments") or ())
        boards.append(BoardEntry(url=url, departments=departments))

    return BoardConfig(boards=tuple(boards))
