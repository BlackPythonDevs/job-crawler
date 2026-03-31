from __future__ import annotations

from dataclasses import dataclass

import httpx

from .greenhouse import Job


async def fetch_jobs(client: httpx.AsyncClient, board_url: str) -> list[Job]:
    response = await client.get(board_url)
    response.raise_for_status()
    data = response.json()

    jobs: list[Job] = []
    for entry in data:
        location = entry.get("workLocation") or {}
        department = entry.get("department") or {}
        jobs.append(
            Job(
                id=entry["uuid"],
                title=entry["name"],
                absolute_url=entry["url"],
                location_name=location.get("label", "Unknown"),
                company_name=department.get("label", ""),
                updated_at="",
                first_published="",
                content="",
            )
        )
    return jobs
