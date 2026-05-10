# Run locally without Docker

For development or quick experiments you can run the bot directly on your host.

## Prerequisites

- Python 3.14+
- [`uv`](https://docs.astral.sh/uv/)
- A reachable Valkey or Redis (`brew install valkey`, `apt install valkey`, or `docker run -p 6379:6379 valkey/valkey`)
- A reachable LLM endpoint (Ollama, OpenAI, etc.)
- A reachable Apprise API endpoint

## Install

```bash
git clone https://github.com/BlackPythonDevs/job-crawler
cd job-crawler
uv sync
```

## Configure

```bash
cp .env.example .env
cp config.toml.example config.toml
# Edit both
```

Make sure `LOG_FILE` points somewhere your user can write — the default `/var/log/job-crawler/job-crawler.log` is meant for the container. For local use, set:

```
LOG_FILE=./job-crawler.log
```

## Run

```bash
job-crawler
```

The bot will preflight, then start the poll loop and the FastAPI server on `localhost:8080`.

## One-shot mode

If you just want a single fetch + post cycle (e.g. testing changes):

```bash
job-crawler --once
```

## Dry run

To see what would post without hitting Apprise or Valkey:

```bash
job-crawler --dry-run --limit 3
```

`APPRISE_URL` is not required when `--dry-run` is set.
