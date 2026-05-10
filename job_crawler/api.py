from __future__ import annotations

from typing import Any

import httpx
import valkey.asyncio as avalkey
from fastapi import FastAPI, HTTPException, Query

from .log_buffer import tail
from .preflight import check_llm, check_valkey
from .runner import RunnerState
from .settings import Settings


def create_app(
    settings: Settings,
    state: RunnerState,
    valkey_client: avalkey.Valkey,
    http_client: httpx.AsyncClient,
    board_count: int,
) -> FastAPI:
    app = FastAPI(title="job-crawler", version="1.0")

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return {
            "valkey": check_valkey(settings.valkey_url),
            "llm": check_llm(
                settings.llm_base_url, settings.llm_api_key, settings.model_name
            ),
        }

    @app.get("/status")
    async def status() -> dict[str, Any]:
        return {
            "last_firing": state.last_firing.isoformat() if state.last_firing else None,
            "next_firing": state.next_firing.isoformat() if state.next_firing else None,
            "running": state.running,
            "board_count": board_count,
            "poll_interval_seconds": settings.poll_interval_seconds,
        }

    @app.get("/logs")
    async def logs(limit: int = Query(default=200, ge=1, le=2000)) -> dict[str, Any]:
        return {"lines": tail(settings.log_file, limit)}

    @app.get("/last-fetch")
    async def last_fetch() -> dict[str, Any]:
        s = state.last_summary
        if s is None:
            return {"available": False}
        return {
            "available": True,
            "started_at": s.started_at.isoformat(),
            "finished_at": s.finished_at.isoformat() if s.finished_at else None,
            "total_fetched": s.total_fetched,
            "new_jobs": s.new_jobs,
            "posted": s.posted,
            "errors": s.errors,
            "per_board": s.per_board,
        }

    @app.post("/run", status_code=202)
    async def run() -> dict[str, Any]:
        if state.running:
            raise HTTPException(409, "Poll already running")
        state.trigger.set()
        return {"triggered": True}

    return app
