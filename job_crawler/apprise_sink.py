from __future__ import annotations

import httpx

from .notify import Notification


async def send(
    client: httpx.AsyncClient,
    apprise_url: str,
    notification: Notification,
) -> None:
    payload = {
        "title": notification.title,
        "body": notification.body,
        "format": "markdown",
    }
    response = await client.post(apprise_url, json=payload, timeout=15)
    response.raise_for_status()
