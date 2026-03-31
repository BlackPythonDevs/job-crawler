from __future__ import annotations

import httpx
import pytest
import respx

from job_crawler.greenhouse import Job, fetch_jobs

BOARD_URL = "https://boards-api.greenhouse.io/v1/boards/testco/jobs"


@pytest.mark.asyncio
async def test_fetch_jobs_parses_response(sample_api_response):
    with respx.mock:
        respx.get(BOARD_URL).mock(return_value=httpx.Response(200, json=sample_api_response))

        async with httpx.AsyncClient() as client:
            jobs = await fetch_jobs(client, BOARD_URL)

    assert len(jobs) == 2
    assert jobs[0] == Job(
        id=1,
        title="Backend Engineer",
        absolute_url="https://boards.greenhouse.io/co/jobs/1",
        location_name="New York, NY",
        company_name="Acme",
        updated_at="2025-02-01T00:00:00Z",
        first_published="2025-01-20T00:00:00Z",
        content="Build APIs and services.",
    )
    assert jobs[1].title == "Frontend Engineer"


@pytest.mark.asyncio
async def test_fetch_jobs_empty_response():
    with respx.mock:
        respx.get(BOARD_URL).mock(return_value=httpx.Response(200, json={"jobs": []}))

        async with httpx.AsyncClient() as client:
            jobs = await fetch_jobs(client, BOARD_URL)

    assert jobs == []


@pytest.mark.asyncio
async def test_fetch_jobs_missing_location():
    payload = {
        "jobs": [
            {
                "id": 99,
                "title": "Designer",
                "absolute_url": "https://example.com/99",
                "location": None,
                "company_name": "",
                "updated_at": "",
                "first_published": "",
            }
        ]
    }
    with respx.mock:
        respx.get(BOARD_URL).mock(return_value=httpx.Response(200, json=payload))

        async with httpx.AsyncClient() as client:
            jobs = await fetch_jobs(client, BOARD_URL)

    assert jobs[0].location_name == "Unknown"


@pytest.mark.asyncio
async def test_fetch_jobs_raises_on_http_error():
    with respx.mock:
        respx.get(BOARD_URL).mock(return_value=httpx.Response(500))

        async with httpx.AsyncClient() as client:
            with pytest.raises(httpx.HTTPStatusError):
                await fetch_jobs(client, BOARD_URL)
