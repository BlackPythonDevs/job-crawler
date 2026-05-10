from __future__ import annotations

import argparse
import asyncio
import logging

import httpx
import uvicorn
import valkey.asyncio as avalkey

from .api import create_app
from .board_config import load_board_config
from .log_buffer import setup_logging
from .notify import build_notification
from .runner import RunnerState, poll_once, run_forever
from .settings import Settings
from .state import filter_new_jobs
from .summarize import summarize_job

log = logging.getLogger("job_crawler")


async def _serve_api(app, host: str, port: int) -> None:
    config = uvicorn.Config(app, host=host, port=port, log_level="info", access_log=False)
    server = uvicorn.Server(config)
    await server.serve()


async def _async_main() -> None:
    settings = Settings()
    board_config = load_board_config(settings.config_path)
    state = RunnerState()

    async with (
        httpx.AsyncClient() as http_client,
        avalkey.from_url(settings.valkey_url) as valkey_client,
    ):
        app = create_app(
            settings, state, valkey_client, http_client, len(board_config.boards)
        )
        await asyncio.gather(
            run_forever(settings, board_config, http_client, valkey_client, state),
            _serve_api(app, settings.api_host, settings.api_port),
        )


async def _async_once(*, max_posts: int | None) -> None:
    settings = Settings(max_posts=max_posts)
    board_config = load_board_config(settings.config_path)
    state = RunnerState()
    async with (
        httpx.AsyncClient() as http_client,
        avalkey.from_url(settings.valkey_url) as valkey_client,
    ):
        await poll_once(
            settings, board_config, http_client, valkey_client, state
        )


async def _async_dry_run(*, max_posts: int | None) -> None:
    settings = Settings(dry_run=True, max_posts=max_posts)
    board_config = load_board_config(settings.config_path)

    from .controller import fetch_all_jobs

    async with (
        httpx.AsyncClient() as http_client,
        avalkey.from_url(settings.valkey_url) as valkey_client,
    ):
        log.info(
            "[fetch] Fetching jobs from %d board(s) ...",
            len(board_config.boards),
        )
        all_jobs = await fetch_all_jobs(http_client, board_config)
        log.info("[fetch] Got %d jobs", len(all_jobs))

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
            print(f"         Body:")
            for line in notification.body.splitlines():
                print(f"           {line}")
            print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Job crawler")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single poll cycle, then exit (no API server).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch + summarize, print to stdout, don't post or persist.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of jobs to post per poll cycle.",
    )
    args = parser.parse_args()

    log_file_env = __import__("os").getenv(
        "LOG_FILE", "/var/log/job-crawler/job-crawler.log"
    )
    try:
        setup_logging(log_file_env)
    except OSError:
        # Fall back to stdout-only if the log dir isn't writable.
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )

    from .preflight import run as preflight_run

    preflight_run()

    if args.dry_run:
        asyncio.run(_async_dry_run(max_posts=args.limit))
    elif args.once:
        asyncio.run(_async_once(max_posts=args.limit))
    else:
        asyncio.run(_async_main())
