from __future__ import annotations

import httpx
import pytest
import respx

from job_crawler.greenhouse import Job
from job_crawler.ripling import fetch_jobs

BOARD_URL = "https://api.rippling.com/platform/api/ats/v1/board/anaconda/jobs"


def _sample_response():
    return [
        {
            "uuid": "3ad90fe4-90e6-48b2-867e-1d48d6bc92aa",
            "name": "Deal Desk Manager",
            "department": {"id": "Legal", "label": "Legal"},
            "url": "https://ats.rippling.com/anaconda/jobs/3ad90fe4-90e6-48b2-867e-1d48d6bc92aa",
            "workLocation": {"label": "Remote (United States)", "id": "Remote (United States)"},
        },
        {
            "uuid": "d7b9ce10-fabd-4f70-8113-701eb8a36ecd",
            "name": "Director Enterprise Sales",
            "department": {"id": "Sales", "label": "Sales"},
            "url": "https://ats.rippling.com/anaconda/jobs/d7b9ce10-fabd-4f70-8113-701eb8a36ecd",
            "workLocation": {"label": "Austin, TX", "id": "Austin, TX"},
        },
    ]


@pytest.mark.asyncio
async def test_fetch_jobs_parses_response():
    with respx.mock:
        respx.get(BOARD_URL).mock(return_value=httpx.Response(200, json=_sample_response()))

        async with httpx.AsyncClient() as client:
            jobs = await fetch_jobs(client, BOARD_URL)

    assert len(jobs) == 2
    assert jobs[0] == Job(
        id="3ad90fe4-90e6-48b2-867e-1d48d6bc92aa",
        title="Deal Desk Manager",
        absolute_url="https://ats.rippling.com/anaconda/jobs/3ad90fe4-90e6-48b2-867e-1d48d6bc92aa",
        location_name="Remote (United States)",
        company_name="Legal",
        updated_at="",
        first_published="",
        content="",
    )
    assert jobs[1].location_name == "Austin, TX"
    assert jobs[1].company_name == "Sales"


@pytest.mark.asyncio
async def test_fetch_jobs_empty_response():
    with respx.mock:
        respx.get(BOARD_URL).mock(return_value=httpx.Response(200, json=[]))

        async with httpx.AsyncClient() as client:
            jobs = await fetch_jobs(client, BOARD_URL)

    assert jobs == []


@pytest.mark.asyncio
async def test_fetch_jobs_missing_location():
    payload = [
        {
            "uuid": "abc-123",
            "name": "Designer",
            "department": None,
            "url": "https://example.com/abc-123",
            "workLocation": None,
        }
    ]
    with respx.mock:
        respx.get(BOARD_URL).mock(return_value=httpx.Response(200, json=payload))

        async with httpx.AsyncClient() as client:
            jobs = await fetch_jobs(client, BOARD_URL)

    assert jobs[0].location_name == "Unknown"
    assert jobs[0].company_name == ""


@pytest.mark.asyncio
async def test_fetch_jobs_raises_on_http_error():
    with respx.mock:
        respx.get(BOARD_URL).mock(return_value=httpx.Response(500))

        async with httpx.AsyncClient() as client:
            with pytest.raises(httpx.HTTPStatusError):
                await fetch_jobs(client, BOARD_URL)
