from __future__ import annotations

import httpx

from .board_config import BoardConfig, BoardEntry
from .greenhouse import Job
from .greenhouse import fetch_jobs as fetch_greenhouse_jobs
from .ripling import fetch_jobs as fetch_ripling_jobs


def _get_fetcher(url: str):
    if "rippling.com" in url or "ripling.com" in url:
        return fetch_ripling_jobs
    if "greenhouse.io" in url:
        return fetch_greenhouse_jobs
    raise ValueError(f"Unsupported job board URL: {url}")


async def _fetch_for_board(
    client: httpx.AsyncClient, board: BoardEntry
) -> list[Job]:
    fetcher = _get_fetcher(board.url)
    jobs = await fetcher(client, board.url)
    return [j for j in jobs if board.allows(j.department)]


async def fetch_all_jobs(
    client: httpx.AsyncClient,
    config: BoardConfig,
) -> list[Job]:
    jobs: list[Job] = []
    for board in config.boards:
        jobs.extend(await _fetch_for_board(client, board))
    return jobs
