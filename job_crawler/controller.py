from __future__ import annotations

import httpx

from .greenhouse import Job
from .greenhouse import fetch_jobs as fetch_greenhouse_jobs
from .ripling import fetch_jobs as fetch_ripling_jobs


def _get_fetcher(url: str):
    if "rippling.com" in url or "ripling.com" in url:
        return fetch_ripling_jobs
    if "greenhouse.io" in url:
        return fetch_greenhouse_jobs
    raise ValueError(f"Unsupported job board URL: {url}")


async def fetch_all_jobs(
    client: httpx.AsyncClient,
    board_urls: list[str],
) -> list[Job]:
    jobs: list[Job] = []
    for url in board_urls:
        fetcher = _get_fetcher(url)
        jobs.extend(await fetcher(client, url))
    return jobs
