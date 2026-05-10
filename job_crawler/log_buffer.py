from __future__ import annotations

import logging
import os
from collections import deque
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(log_file: str, level: int = logging.INFO) -> None:
    """Install a stdout handler and a rotating file handler on the root logger."""
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    root = logging.getLogger()
    root.setLevel(level)
    # Avoid double-installing handlers if called twice (tests, /run reloads).
    if not any(isinstance(h, RotatingFileHandler) for h in root.handlers):
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=3
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
    if not any(isinstance(h, logging.StreamHandler) and not isinstance(h, RotatingFileHandler) for h in root.handlers):
        stream = logging.StreamHandler()
        stream.setFormatter(formatter)
        root.addHandler(stream)


def tail(path: str, n: int) -> list[str]:
    """Return the last n lines of the log file (best-effort)."""
    if not os.path.exists(path):
        return []
    n = max(0, min(n, 2000))
    if n == 0:
        return []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return list(deque(f, maxlen=n))
