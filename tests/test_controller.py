from __future__ import annotations

import httpx
import pytest
import respx

from job_crawler.controller import _get_fetcher, fetch_all_jobs
from job_crawler.greenhouse import Job
from job_crawler.greenhouse import fetch_jobs as fetch_greenhouse_jobs
from job_crawler.ripling import fetch_jobs as fetch_ripling_jobs

GREENHOUSE_URL = "https://boards-api.greenhouse.io/v1/boards/testco/jobs"
RIPLING_URL = "https://api.rippling.com/platform/api/ats/v1/board/anaconda/jobs"


def test_get_fetcher_greenhouse():
    assert _get_fetcher(GREENHOUSE_URL) is fetch_greenhouse_jobs


def test_get_fetcher_ripling():
    assert _get_fetcher(RIPLING_URL) is fetch_ripling_jobs


def test_get_fetcher_unsupported():
    with pytest.raises(ValueError, match="Unsupported job board URL"):
        _get_fetcher("https://example.com/jobs")


@pytest.mark.asyncio
async def test_fetch_all_jobs_mixed_sources():
    greenhouse_payload = {
        "jobs": [
            {
                "id": 1,
                "title": "Backend Engineer",
                "absolute_url": "https://boards.greenhouse.io/co/jobs/1",
                "location": {"name": "NYC"},
                "company_name": "Acme",
                "updated_at": "2025-02-01T00:00:00Z",
                "first_published": "2025-01-20T00:00:00Z",
                "content": "<p>Build APIs.</p>",
            }
        ]
    }
    ripling_payload = [
        {
            "uuid": "abc-123",
            "name": "Designer",
            "department": {"id": "Design", "label": "Design"},
            "url": "https://ats.rippling.com/co/jobs/abc-123",
            "workLocation": {"label": "Remote", "id": "Remote"},
        }
    ]

    with respx.mock:
        respx.get(GREENHOUSE_URL).mock(return_value=httpx.Response(200, json=greenhouse_payload))
        respx.get(RIPLING_URL).mock(return_value=httpx.Response(200, json=ripling_payload))

        async with httpx.AsyncClient() as client:
            jobs = await fetch_all_jobs(client, [GREENHOUSE_URL, RIPLING_URL])

    assert len(jobs) == 2
    assert jobs[0].title == "Backend Engineer"
    assert jobs[1].title == "Designer"
