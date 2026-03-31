from __future__ import annotations

from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from .greenhouse import Job


def job_embed(job: Job, summary: str | None = None) -> discord.Embed:
    embed = discord.Embed(
        title=job.title,
        url=job.absolute_url,
        description=summary,
        colour=discord.Colour.green(),
    )
    embed.add_field(name="Location", value=job.location_name, inline=True)
    if job.first_published:
        embed.add_field(name="Posted", value=job.first_published, inline=True)
    embed.set_footer(text=f"Job ID: {job.id}")
    return embed
