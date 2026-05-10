# Add a new job board

Boards are configured in `config.toml`. The crawler currently understands two URL shapes: Greenhouse (`*.greenhouse.io/...`) and Rippling (`*.rippling.com/...`).

## Add the entry

Open `config.toml` and append a new `[[boards]]` table:

```toml
[[boards]]
url = "https://boards-api.greenhouse.io/v1/boards/<slug>/jobs"
```

For Greenhouse, the `<slug>` is the company identifier in the URL of their public board (e.g. `temporaltechnologies`).

For Rippling:

```toml
[[boards]]
url = "https://api.rippling.com/platform/api/ats/v1/board/<slug>/jobs"
```

## Reload

If you're running under Docker Compose, restart the bot container:

```bash
docker compose restart bot
```

If you're running locally, send `Ctrl-C` and start `job-crawler` again.

## Verify

Hit the status endpoint and check `board_count`:

```bash
curl http://localhost:8080/status
```

Trigger an immediate poll to see jobs from the new board flow through:

```bash
curl -X POST http://localhost:8080/run
curl http://localhost:8080/last-fetch
```

`/last-fetch` shows per-board counts so you can confirm the new board is being read.

## Unsupported URL?

If the URL doesn't match Greenhouse or Rippling, the bot will refuse to start with a `ValueError: Unsupported job board URL`. New providers require code in `job_crawler/controller.py` — see [Architecture](../explanation/architecture.md).
