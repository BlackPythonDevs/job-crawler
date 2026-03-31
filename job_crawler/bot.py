from __future__ import annotations

import asyncio
import logging

import discord
import httpx
import valkey.asyncio as avalkey
from discord.ext import tasks

from .config import Config
from .embeds import job_embed
from .greenhouse import fetch_jobs
from .state import filter_new_jobs, mark_job_posted
from .summarize import summarize_job

log = logging.getLogger("job_crawler")


class JobCrawlerBot(discord.Client):
    def __init__(
        self,
        config: Config,
        http_client: httpx.AsyncClient,
        valkey_client: avalkey.Valkey,
    ) -> None:
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.config = config
        self.http_client = http_client
        self.valkey_client = valkey_client

    async def setup_hook(self) -> None:
        self.poll_greenhouse.start()

    @tasks.loop(count=1)
    async def poll_greenhouse(self) -> None:
        channel = self.get_channel(self.config.discord_channel_id)
        if channel is None:
            channel = await self.fetch_channel(self.config.discord_channel_id)
        if not isinstance(channel, discord.abc.Messageable):
            log.error("Channel %s is not messageable", self.config.discord_channel_id)
            return

        log.info("[fetch] Fetching jobs from Greenhouse ...")
        try:
            all_jobs = await fetch_jobs(
                self.http_client, self.config.greenhouse_board_url
            )
        except Exception:
            log.exception("[fetch] Failed to fetch jobs from Greenhouse")
            return
        log.info("[fetch] Got %d jobs from Greenhouse", len(all_jobs))

        log.info("[filter] Checking Valkey for already-posted jobs ...")
        new_jobs = await filter_new_jobs(self.valkey_client, all_jobs)
        log.info("[filter] Found %d new jobs out of %d total", len(new_jobs), len(all_jobs))

        posts = new_jobs[: self.config.max_posts] if self.config.max_posts else new_jobs
        for i, job in enumerate(posts, 1):
            log.info("[post] (%d/%d) Processing job %s — %s", i, len(posts), job.id, job.title)
            try:
                summary = None
                if job.content:
                    log.info("[summarize] (%d/%d) Summarizing job %s ...", i, len(posts), job.id)
                    try:
                        summary = await summarize_job(
                            self.config.ollama_model, job.content
                        )
                        log.info("[summarize] (%d/%d) Done summarizing job %s", i, len(posts), job.id)
                    except Exception:
                        log.warning("[summarize] (%d/%d) Failed to summarize job %s, posting without summary", i, len(posts), job.id, exc_info=True)
                await channel.send(embed=job_embed(job, summary=summary))
                await mark_job_posted(
                    self.valkey_client, job.id, self.config.job_ttl_seconds
                )
                log.info("[post] (%d/%d) Posted job %s", i, len(posts), job.id)
            except Exception:
                log.exception("[post] (%d/%d) Failed to post job %s (%s)", i, len(posts), job.id, job.title)

    @poll_greenhouse.before_loop
    async def before_poll(self) -> None:
        await self.wait_until_ready()

    @poll_greenhouse.after_loop
    async def after_poll(self) -> None:
        log.info("[poll] Poll cycle complete, shutting down.")
        await self.close()

    async def close(self) -> None:
        await super().close()


async def _dry_run(max_posts: int | None = None) -> None:
    config = Config(dry_run=True)

    async with (
        httpx.AsyncClient() as http_client,
        avalkey.from_url(config.valkey_url) as valkey_client,
    ):
        log.info("[fetch] Fetching jobs from Greenhouse ...")
        all_jobs = await fetch_jobs(http_client, config.greenhouse_board_url)
        log.info("[fetch] Got %d jobs from Greenhouse", len(all_jobs))

        log.info("[filter] Checking Valkey for already-posted jobs ...")
        new_jobs = await filter_new_jobs(valkey_client, all_jobs)
        display = new_jobs[:max_posts] if max_posts else new_jobs

        print(f"Total jobs from Greenhouse: {len(all_jobs)}")
        print(f"New jobs (not in Valkey):    {len(new_jobs)}")
        if max_posts and len(new_jobs) > max_posts:
            print(f"Showing first {max_posts} of {len(new_jobs)}")
        print()
        for i, job in enumerate(display, 1):
            print(f"  [{job.id}] {job.title}")
            print(f"         {job.location_name}")
            print(f"         {job.absolute_url}")
            if job.content:
                log.info("[summarize] (%d/%d) Summarizing job %s ...", i, len(display), job.id)
                try:
                    summary = await summarize_job(config.ollama_model, job.content)
                    print(f"         Summary: {summary}")
                except Exception:
                    print("         Summary: (summarization failed)")
            print()


async def _async_main(max_posts: int | None = None) -> None:
    config = Config(max_posts=max_posts)

    async with (
        httpx.AsyncClient() as http_client,
        avalkey.from_url(config.valkey_url) as valkey_client,
    ):
        bot = JobCrawlerBot(config, http_client, valkey_client)
        async with bot:
            await bot.start(config.discord_token)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Job crawler Discord bot")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch jobs and show what would be posted, then exit (no Discord needed)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of jobs to post per poll cycle (default: no limit)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    from .preflight import run as preflight_run

    preflight_run()

    if args.dry_run:
        asyncio.run(_dry_run(max_posts=args.limit))
    else:
        asyncio.run(_async_main(max_posts=args.limit))
