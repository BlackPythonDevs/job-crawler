from __future__ import annotations

import httpx
import pytest
import respx

from job_crawler.apprise_sink import send
from job_crawler.notify import Notification

APPRISE_URL = "http://apprise.local/notify/x"


@pytest.mark.asyncio
async def test_send_posts_markdown():
    with respx.mock:
        route = respx.post(APPRISE_URL).mock(
            return_value=httpx.Response(200, json={"ok": True})
        )
        async with httpx.AsyncClient() as client:
            await send(
                client,
                APPRISE_URL,
                Notification(title="t", body="**b**"),
            )
        req = route.calls.last.request
        import json
        body = json.loads(req.content)
        assert body == {"title": "t", "body": "**b**", "format": "markdown"}
