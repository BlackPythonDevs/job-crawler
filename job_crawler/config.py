from __future__ import annotations

import os

DEFAULT_BOARD_URL = (
    "https://boards-api.greenhouse.io/v1/boards/temporaltechnologies/jobs"
)


class Config:
    def __init__(self, *, dry_run: bool = False, max_posts: int | None = None) -> None:
        self.dry_run = dry_run
        self.max_posts = max_posts
        self.discord_token: str = "" if dry_run else _require("DISCORD_TOKEN")
        self.discord_channel_id: int = (
            0 if dry_run else int(_require("DISCORD_CHANNEL_ID"))
        )
        self.valkey_url: str = os.getenv("VALKEY_URL", "valkey://localhost:6379/0")
        self.job_ttl_seconds: int = int(
            os.getenv("JOB_TTL_SECONDS", "7776000")  # 90 days
        )
        self.greenhouse_board_url: str = os.getenv(
            "GREENHOUSE_BOARD_URL", DEFAULT_BOARD_URL
        )
        self.ollama_model: str = os.getenv("OLLAMA_MODEL", "ministral-3")


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value
