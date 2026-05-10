# HTTP API

The bot exposes a FastAPI server on `API_HOST:API_PORT` (default `0.0.0.0:8080`). Auto-generated OpenAPI docs are at `/docs`.

There is no authentication. The API is intended for use behind network isolation.

## `GET /health`

Reachability checks for required services.

```json
{
  "valkey": true,
  "llm": true
}
```

## `GET /status`

Runtime state.

```json
{
  "last_firing": "2026-05-09T12:34:56+00:00",
  "next_firing": "2026-05-09T16:34:56+00:00",
  "running": false,
  "board_count": 2,
  "poll_interval_seconds": 14400
}
```

`last_firing` and `next_firing` are `null` until the first cycle finishes.

## `GET /logs`

Tail of the log file.

| Query | Default | Range | Description |
|---|---|---|---|
| `limit` | 200 | 1–2000 | Number of lines to return. |

```json
{
  "lines": [
    "2026-05-09 12:34:56 INFO job_crawler: [fetch] Got 14 jobs\n",
    ...
  ]
}
```

## `GET /last-fetch`

Summary of the most recent poll cycle.

```json
{
  "available": true,
  "started_at": "2026-05-09T12:34:50+00:00",
  "finished_at": "2026-05-09T12:34:56+00:00",
  "total_fetched": 14,
  "new_jobs": 3,
  "posted": 3,
  "errors": 0,
  "per_board": {"boards-api.greenhouse.io": 14}
}
```

Returns `{"available": false}` until the first cycle finishes.

## `POST /run`

Trigger a poll cycle out-of-band.

| Status | Meaning |
|---|---|
| `202 Accepted` | Trigger queued. |
| `409 Conflict` | A poll is already running. |

```json
{ "triggered": true }
```

The triggered cycle does not reset the regular schedule.
