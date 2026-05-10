# Trigger a manual poll

The bot polls on its own every `POLL_INTERVAL_SECONDS` (4 hours by default). To poll right now without waiting, hit the API.

## From the host

```bash
curl -X POST http://localhost:8080/run
```

You'll get back `{"triggered": true}` and a `202 Accepted` status code.

If a poll is already running, you'll get `409 Conflict` instead — the bot only runs one cycle at a time.

## Inspect the result

```bash
curl http://localhost:8080/last-fetch
```

Returns counts of total fetched, new (deduped), posted, errors, and per-board breakdown.

## From inside the container

```bash
docker compose exec bot curl -X POST http://localhost:8080/run
```

## See also

- [HTTP API reference](../reference/http-api.md)
- [Status](../reference/http-api.md#get-status)
