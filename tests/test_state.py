from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from job_crawler.greenhouse import Job
from job_crawler.state import (
    KEY_PREFIX,
    filter_new_jobs,
    is_job_known,
    mark_job_posted,
)


def _make_job(job_id: int) -> Job:
    return Job(
        id=job_id,
        title=f"Job {job_id}",
        absolute_url=f"https://example.com/{job_id}",
        location_name="Remote",
        company_name="Co",
        updated_at="",
        first_published="",
        content="",
    )


@pytest.fixture
def mock_valkey():
    client = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_filter_new_jobs_returns_unseen(mock_valkey):
    jobs = [_make_job(1), _make_job(2), _make_job(3)]

    pipe = MagicMock()
    pipe.exists = MagicMock()  # exists on a pipeline is sync (buffered)
    pipe.execute = AsyncMock(return_value=[1, 0, 0])
    # pipeline() is sync on valkey clients, so override with MagicMock
    mock_valkey.pipeline = MagicMock(return_value=pipe)

    new = await filter_new_jobs(mock_valkey, jobs)

    assert len(new) == 2
    assert new[0].id == 2
    assert new[1].id == 3


@pytest.mark.asyncio
async def test_filter_new_jobs_empty_list(mock_valkey):
    result = await filter_new_jobs(mock_valkey, [])
    assert result == []
    mock_valkey.pipeline.assert_not_called()


@pytest.mark.asyncio
async def test_mark_job_posted(mock_valkey):
    await mark_job_posted(mock_valkey, 42, ttl_seconds=3600)
    mock_valkey.set.assert_awaited_once_with(f"{KEY_PREFIX}42", "1", ex=3600)


@pytest.mark.asyncio
async def test_is_job_known_true(mock_valkey):
    mock_valkey.exists.return_value = 1
    assert await is_job_known(mock_valkey, 42) is True


@pytest.mark.asyncio
async def test_is_job_known_false(mock_valkey):
    mock_valkey.exists.return_value = 0
    assert await is_job_known(mock_valkey, 42) is False
