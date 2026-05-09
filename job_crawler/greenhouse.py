from __future__ import annotations

import re
from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class Job:
    id: int | str
    title: str
    absolute_url: str
    location_name: str
    company_name: str
    updated_at: str
    first_published: str
    content: str
    department: str = ""


def _strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text).strip()


def _first_department(entry: dict) -> str:
    departments = entry.get("departments") or []
    for d in departments:
        name = (d or {}).get("name")
        if name:
            return name
    return ""


async def fetch_jobs(client: httpx.AsyncClient, board_url: str) -> list[Job]:
    response = await client.get(board_url, params={"content": "true"})
    response.raise_for_status()
    data = response.json()

    jobs: list[Job] = []
    for entry in data.get("jobs", []):
        location = entry.get("location", {}) or {}
        raw_content = entry.get("content", "")
        jobs.append(
            Job(
                id=entry["id"],
                title=entry["title"],
                absolute_url=entry["absolute_url"],
                location_name=location.get("name", "Unknown"),
                company_name=entry.get("company_name", ""),
                updated_at=entry.get("updated_at", ""),
                first_published=entry.get("first_published", ""),
                content=_strip_html(raw_content),
                department=_first_department(entry),
            )
        )
    return jobs
