from __future__ import annotations

from pathlib import Path

import pytest

from job_crawler.board_config import BoardEntry, load_board_config


def write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "config.toml"
    p.write_text(content)
    return p


def test_load_basic(tmp_path):
    p = write(tmp_path, """
[[boards]]
url = "https://greenhouse.io/a"
departments = ["Engineering", "DevRel"]

[[boards]]
url = "https://rippling.com/b"
""")
    cfg = load_board_config(p)
    assert len(cfg.boards) == 2
    assert cfg.boards[0].url == "https://greenhouse.io/a"
    assert cfg.boards[0].departments == ("Engineering", "DevRel")
    assert cfg.boards[1].departments == ()


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_board_config(tmp_path / "missing.toml")


def test_no_boards_raises(tmp_path):
    p = write(tmp_path, "")
    with pytest.raises(ValueError, match="no \\[\\[boards\\]\\]"):
        load_board_config(p)


def test_missing_url_raises(tmp_path):
    p = write(tmp_path, "[[boards]]\ndepartments = [\"X\"]\n")
    with pytest.raises(ValueError, match="missing required 'url'"):
        load_board_config(p)


def test_allows_empty_list_passes_all():
    b = BoardEntry(url="x", departments=())
    assert b.allows("Engineering")
    assert b.allows("")


def test_allows_case_insensitive():
    b = BoardEntry(url="x", departments=("Engineering",))
    assert b.allows("engineering")
    assert b.allows("ENGINEERING")
    assert not b.allows("Sales")
