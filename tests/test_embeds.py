from __future__ import annotations

import discord

from job_crawler.embeds import job_embed
from job_crawler.greenhouse import Job


def test_job_embed_fields(sample_job):
    embed = job_embed(sample_job)

    assert embed.title == "Software Engineer"
    assert embed.url == "https://boards.greenhouse.io/example/jobs/123"
    assert embed.colour == discord.Colour.green()

    field_names = [f.name for f in embed.fields]
    assert "Location" in field_names
    assert "Posted" in field_names

    location_field = next(f for f in embed.fields if f.name == "Location")
    assert location_field.value == "San Francisco, CA"

    assert embed.footer.text == "Job ID: 123"


def test_job_embed_no_posted_field_when_empty():
    job = Job(
        id=1,
        title="Role",
        absolute_url="https://example.com/1",
        location_name="Remote",
        company_name="Co",
        updated_at="",
        first_published="",
        content="",
    )
    embed = job_embed(job)
    field_names = [f.name for f in embed.fields]
    assert "Posted" not in field_names
