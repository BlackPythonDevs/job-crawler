from __future__ import annotations

import pytest

from job_crawler.greenhouse import Job


@pytest.fixture
def sample_job():
    return Job(
        id=123,
        title="Software Engineer",
        absolute_url="https://boards.greenhouse.io/example/jobs/123",
        location_name="San Francisco, CA",
        company_name="Example Corp",
        updated_at="2025-01-15T12:00:00Z",
        first_published="2025-01-10T09:00:00Z",
        content="Build and maintain backend services.",
    )


@pytest.fixture
def sample_api_response():
    """Mimics a Greenhouse board API response."""
    return {
        "jobs": [
            {
                "id": 1,
                "title": "Backend Engineer",
                "absolute_url": "https://boards.greenhouse.io/co/jobs/1",
                "location": {"name": "New York, NY"},
                "company_name": "Acme",
                "updated_at": "2025-02-01T00:00:00Z",
                "first_published": "2025-01-20T00:00:00Z",
                "content": "<p>Build APIs and services.</p>",
            },
            {
                "id": 2,
                "title": "Frontend Engineer",
                "absolute_url": "https://boards.greenhouse.io/co/jobs/2",
                "location": {"name": "Remote"},
                "company_name": "Acme",
                "updated_at": "2025-02-02T00:00:00Z",
                "first_published": "2025-01-25T00:00:00Z",
                "content": "<p>Build UI components.</p>",
            },
        ]
    }
