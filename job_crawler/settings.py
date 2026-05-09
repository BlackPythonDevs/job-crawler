from __future__ import annotations

import os


class Settings:
    def __init__(
        self,
        *,
        dry_run: bool = False,
        max_posts: int | None = None,
    ) -> None:
        self.dry_run = dry_run
        self.max_posts = max_posts

        self.apprise_url: str = (
            "" if dry_run else _require("APPRISE_URL")
        )

        self.llm_base_url: str = os.getenv(
            "LLM_BASE_URL", "http://localhost:11434/v1"
        )
        self.model_name: str = os.getenv("MODEL_NAME", "ministral-3")
        self.llm_api_key: str = os.getenv("LLM_API_KEY", "not-needed")

        self.valkey_url: str = os.getenv(
            "VALKEY_URL", "valkey://localhost:6379/0"
        )
        self.job_ttl_seconds: int = int(os.getenv("JOB_TTL_SECONDS", "7776000"))

        self.config_path: str = os.getenv("JOB_CRAWLER_CONFIG", "./config.toml")


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value
