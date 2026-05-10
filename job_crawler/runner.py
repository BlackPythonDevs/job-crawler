from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

import httpx
import valkey.asyncio as avalkey

from .apprise_sink import send as apprise_send
from .board_config import BoardConfig
from .controller import fetch_all_jobs
from .notify import build_notification
from .settings import Settings
from .state import filter_new_jobs, mark_job_posted
from .summarize import summarize_job

log = logging.getLogger("job_crawler")


@dataclass
class FetchSummary:
    started_at: datetime
    finished_at: datetime | None = None
    total_fetched: int = 0
    new_jobs: int = 0
    posted: int = 0
    errors: int = 0
    per_board: dict[str, int] = field(default_factory=dict)


@dataclass
class RunnerState:
    last_firing: datetime | None = None
    next_firing: datetime | None = None
    running: bool = False
    last_summary: FetchSummary | None = None
    trigger: asyncio.Event = field(default_factory=asyncio.Event)


async def poll_once(
    settings: Settings,
    board_config: BoardConfig,
    http_client: httpx.AsyncClient,
    valkey_client: avalkey.Valkey,
    state: RunnerState,
    *,
    post: bool = True,
) -> FetchSummary:
    summary = FetchSummary(started_at=datetime.now(timezone.utc))
    state.running = True
    state.last_summary = summary
    try:
        log.info("[fetch] Fetching jobs from %d board(s) ...", len(board_config.boards))
        try:
            all_jobs = await fetch_all_jobs(http_client, board_config)
        except Exception:
            log.exception("[fetch] Failed to fetch jobs")
            summary.errors += 1
            return summary

        summary.total_fetched = len(all_jobs)
        for j in all_jobs:
            key = j.absolute_url.split("/")[2] if "://" in j.absolute_url else "unknown"
            summary.per_board[key] = summary.per_board.get(key, 0) + 1
        log.info("[fetch] Got %d jobs", len(all_jobs))

        new_jobs = await filter_new_jobs(valkey_client, all_jobs)
        summary.new_jobs = len(new_jobs)
        log.info("[filter] %d new of %d total", len(new_jobs), len(all_jobs))

        posts = (
            new_jobs[: settings.max_posts] if settings.max_posts else new_jobs
        )
        for i, job in enumerate(posts, 1):
            log.info("[post] (%d/%d) %s — %s", i, len(posts), job.id, job.title)
            try:
                summary_text: str | None = None
                if job.content:
                    try:
                        summary_text = await summarize_job(
                            settings.llm_base_url,
                            settings.llm_api_key,
                            settings.model_name,
                            job.content,
                        )
                    except Exception:
                        log.warning(
                            "[summarize] (%d/%d) failed for %s",
                            i, len(posts), job.id, exc_info=True,
                        )
                notification = build_notification(job, summary=summary_text)
                if post:
                    await apprise_send(http_client, settings.apprise_url, notification)
                await mark_job_posted(
                    valkey_client, job.id, settings.job_ttl_seconds
                )
                summary.posted += 1
            except Exception:
                log.exception("[post] failed for %s", job.id)
                summary.errors += 1
        return summary
    finally:
        summary.finished_at = datetime.now(timezone.utc)
        state.last_firing = summary.finished_at
        state.next_firing = datetime.fromtimestamp(
            summary.finished_at.timestamp() + settings.poll_interval_seconds,
            tz=timezone.utc,
        )
        state.running = False


async def run_forever(
    settings: Settings,
    board_config: BoardConfig,
    http_client: httpx.AsyncClient,
    valkey_client: avalkey.Valkey,
    state: RunnerState,
) -> None:
    while True:
        await poll_once(
            settings, board_config, http_client, valkey_client, state
        )
        try:
            await asyncio.wait_for(
                state.trigger.wait(), timeout=settings.poll_interval_seconds
            )
            state.trigger.clear()
            log.info("[runner] Triggered manual poll")
        except asyncio.TimeoutError:
            pass
