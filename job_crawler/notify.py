from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .greenhouse import Job


@dataclass(frozen=True)
class Notification:
    title: str
    body: str


def build_notification(job: "Job", summary: str | None = None) -> Notification:
    title = f"New job: {job.title}"
    if job.company_name:
        title = f"New job: {job.title} — {job.company_name}"

    lines: list[str] = [f"**{job.title}**"]
    if job.company_name:
        lines.append(job.company_name)
    lines.append(f"_{job.location_name}_")
    if job.department:
        lines.append(f"Department: {job.department}")
    lines.append("")
    if summary:
        lines.append(summary)
        lines.append("")
    lines.append(f"[View posting]({job.absolute_url})")

    return Notification(title=title, body="\n".join(lines))
