from __future__ import annotations

from job_crawler.greenhouse import Job
from job_crawler.notify import build_notification


def _job(**overrides):
    base = dict(
        id=1,
        title="Backend Engineer",
        absolute_url="https://example.com/jobs/1",
        location_name="NYC",
        company_name="Acme",
        updated_at="",
        first_published="",
        content="",
        department="Engineering",
    )
    base.update(overrides)
    return Job(**base)


def test_title_includes_company():
    n = build_notification(_job())
    assert "Backend Engineer" in n.title
    assert "Acme" in n.title


def test_body_includes_link_and_summary():
    n = build_notification(_job(), summary="A short summary.")
    assert "A short summary." in n.body
    assert "https://example.com/jobs/1" in n.body
    assert "NYC" in n.body
    assert "Engineering" in n.body


def test_body_without_summary_skips_summary_block():
    n = build_notification(_job())
    assert "summary" not in n.body.lower()
