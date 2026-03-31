from __future__ import annotations

from typing import TYPE_CHECKING

import valkey.asyncio as avalkey

if TYPE_CHECKING:
    from .greenhouse import Job

KEY_PREFIX = "job:"


def _key(job_id: int) -> str:
    return f"{KEY_PREFIX}{job_id}"


async def filter_new_jobs(
    client: avalkey.Valkey, jobs: list[Job]
) -> list[Job]:
    if not jobs:
        return []

    pipe = client.pipeline(transaction=False)
    for job in jobs:
        pipe.exists(_key(job.id))
    results = await pipe.execute()

    return [job for job, exists in zip(jobs, results) if not exists]


async def mark_job_posted(
    client: avalkey.Valkey, job_id: int, ttl_seconds: int
) -> None:
    await client.set(_key(job_id), "1", ex=ttl_seconds)


async def is_job_known(client: avalkey.Valkey, job_id: int) -> bool:
    return bool(await client.exists(_key(job_id)))
