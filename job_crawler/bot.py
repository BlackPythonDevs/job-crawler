from __future__ import annotations

import argparse
import asyncio
import logging

import httpx
import valkey.asyncio as avalkey

from .apprise_sink import send as apprise_send
from .board_config import load_board_config
from .controller import fetch_all_jobs
from .notify import build_notification
from .settings import Settings
from .state import filter_new_jobs, mark_job_posted
from .summarize import summarize_job

log = logging.getLogger("job_crawler")


async def _poll_once(settings: Settings, board_config) -> None:
    async with (
        httpx.AsyncClient() as http_client,
        avalkey.from_url(settings.valkey_url) as valkey_client,
    ):
        log.info(
            "[fetch] Fetching jobs from %d board(s) ...",
            len(board_config.boards),
        )
        try:
            all_jobs = await fetch_all_jobs(http_client, board_config)
        except Exception:
            log.exception("[fetch] Failed to fetch jobs")
            return
        log.info("[fetch] Got %d jobs", len(all_jobs))

        new_jobs = await filter_new_jobs(valkey_client, all_jobs)
        log.info("[filter] %d new of %d total", len(new_jobs), len(all_jobs))

        posts = (
            new_jobs[: settings.max_posts] if settings.max_posts else new_jobs
        )
        for i, job in enumerate(posts, 1):
            log.info("[post] (%d/%d) %s — %s", i, len(posts), job.id, job.title)
            try:
                summary_text = None
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
                await apprise_send(http_client, settings.apprise_url, notification)
                await mark_job_posted(
                    valkey_client, job.id, settings.job_ttl_seconds
                )
            except Exception:
                log.exception("[post] failed for %s", job.id)


async def _async_main(max_posts: int | None) -> None:
    settings = Settings(max_posts=max_posts)
    board_config = load_board_config(settings.config_path)
    await _poll_once(settings, board_config)


async def _async_dry_run(max_posts: int | None) -> None:
    settings = Settings(dry_run=True, max_posts=max_posts)
    board_config = load_board_config(settings.config_path)

    async with (
        httpx.AsyncClient() as http_client,
        avalkey.from_url(settings.valkey_url) as valkey_client,
    ):
        all_jobs = await fetch_all_jobs(http_client, board_config)
        new_jobs = await filter_new_jobs(valkey_client, all_jobs)
        display = new_jobs[:max_posts] if max_posts else new_jobs

        print(f"Total jobs: {len(all_jobs)}")
        print(f"New jobs (not in Valkey): {len(new_jobs)}")
        if max_posts and len(new_jobs) > max_posts:
            print(f"Showing first {max_posts} of {len(new_jobs)}")
        print()
        for job in display:
            print(f"  [{job.id}] {job.title}")
            print(f"         {job.location_name}  ({job.department or 'n/a'})")
            print(f"         {job.absolute_url}")
            summary_text = None
            if job.content:
                try:
                    summary_text = await summarize_job(
                        settings.llm_base_url,
                        settings.llm_api_key,
                        settings.model_name,
                        job.content,
                    )
                except Exception:
                    summary_text = "(summarization failed)"
            notification = build_notification(job, summary=summary_text)
            print(f"         Title: {notification.title}")
            for line in notification.body.splitlines():
                print(f"           {line}")
            print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Job crawler")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch + summarize, print to stdout, don't post or persist.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of jobs to post per cycle.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    from .preflight import run as preflight_run

    preflight_run()

    if args.dry_run:
        asyncio.run(_async_dry_run(max_posts=args.limit))
    else:
        asyncio.run(_async_main(max_posts=args.limit))
