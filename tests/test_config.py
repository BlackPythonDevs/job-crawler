from __future__ import annotations

import os

import pytest

from job_crawler.config import Config


def test_dry_run_skips_required_vars():
    config = Config(dry_run=True)
    assert config.discord_token == ""
    assert config.discord_channel_id == 0


def test_missing_discord_token_raises(monkeypatch):
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    monkeypatch.delenv("DISCORD_CHANNEL_ID", raising=False)
    with pytest.raises(RuntimeError, match="DISCORD_TOKEN"):
        Config()


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", "tok")
    monkeypatch.setenv("DISCORD_CHANNEL_ID", "999")
    monkeypatch.setenv("VALKEY_URL", "valkey://custom:6380/1")
    monkeypatch.setenv("JOB_TTL_SECONDS", "1000")
    monkeypatch.setenv("GREENHOUSE_BOARD_URL", "https://example.com/jobs")

    config = Config()
    assert config.discord_token == "tok"
    assert config.discord_channel_id == 999
    assert config.valkey_url == "valkey://custom:6380/1"
    assert config.job_ttl_seconds == 1000
    assert config.greenhouse_board_url == "https://example.com/jobs"


def test_defaults(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", "tok")
    monkeypatch.setenv("DISCORD_CHANNEL_ID", "1")

    config = Config()
    assert config.valkey_url == "valkey://localhost:6379/0"
    assert config.job_ttl_seconds == 7776000
