from __future__ import annotations

import pytest

from job_crawler.settings import Settings


def test_dry_run_skips_apprise(monkeypatch):
    monkeypatch.delenv("APPRISE_URL", raising=False)
    s = Settings(dry_run=True)
    assert s.apprise_url == ""


def test_missing_apprise_raises(monkeypatch):
    monkeypatch.delenv("APPRISE_URL", raising=False)
    with pytest.raises(RuntimeError, match="APPRISE_URL"):
        Settings()


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("APPRISE_URL", "http://apprise/notify/x")
    monkeypatch.setenv("LLM_BASE_URL", "https://api.openai.com/v1")
    monkeypatch.setenv("MODEL_NAME", "gpt-4o-mini")
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    monkeypatch.setenv("POLL_INTERVAL_SECONDS", "60")
    monkeypatch.setenv("API_PORT", "9090")

    s = Settings()
    assert s.apprise_url == "http://apprise/notify/x"
    assert s.llm_base_url == "https://api.openai.com/v1"
    assert s.model_name == "gpt-4o-mini"
    assert s.llm_api_key == "sk-test"
    assert s.poll_interval_seconds == 60
    assert s.api_port == 9090


def test_defaults(monkeypatch):
    monkeypatch.setenv("APPRISE_URL", "http://apprise/notify/x")
    s = Settings()
    assert s.llm_base_url == "http://localhost:11434/v1"
    assert s.model_name == "ministral-3"
    assert s.poll_interval_seconds == 14400
    assert s.api_port == 8080
