# Job Crawler

A job board crawler that fetches postings from [Greenhouse](https://www.greenhouse.io/) and [Rippling](https://www.rippling.com/) boards, summarizes them via any OpenAI-compatible LLM endpoint (using [Pydantic AI](https://ai.pydantic.dev/)), and posts new listings through an [Apprise API](https://github.com/caronc/apprise-api) endpoint (Discord, Slack, email, anywhere Apprise reaches). [Valkey](https://valkey.io/) tracks already-posted jobs to prevent duplicates.

## Prerequisites

- Python 3.14+
- Apprise API instance with destinations configured
- OpenAI-compatible LLM endpoint (Ollama, vLLM, OpenRouter, OpenAI, etc.)
- Valkey (or Redis) instance

## Quickstart

### Docker Compose

```bash
cp .env.example .env
cp config.toml.example config.toml
# Edit both files
docker compose up --build
```

### Local Development

```bash
uv sync
cp .env.example .env
cp config.toml.example config.toml
job-crawler
```

### CLI Options

```
job-crawler              # Run a poll cycle, post via Apprise, exit
job-crawler --dry-run    # Preview jobs locally; no Apprise post, no state write
job-crawler --limit 5    # Cap the number of jobs posted per cycle
job-preflight            # Verify Valkey + LLM are reachable
```

## Configuration

### Environment variables

See [`.env.example`](.env.example).

| Variable | Required | Default | Description |
|---|---|---|---|
| `APPRISE_URL` | Yes | — | Apprise API notify endpoint (not required for `--dry-run`). |
| `LLM_BASE_URL` | No | `http://localhost:11434/v1` | OpenAI-compatible base URL. |
| `MODEL_NAME` | No | `ministral-3` | Model name sent in chat completion requests. |
| `LLM_API_KEY` | No | `not-needed` | Bearer token. Ollama ignores it. |
| `VALKEY_URL` | No | `valkey://localhost:6379/0` | Valkey/Redis URL. |
| `JOB_TTL_SECONDS` | No | `7776000` | Dedup TTL (90 days). |
| `JOB_CRAWLER_CONFIG` | No | `./config.toml` | Path to the TOML board config. |

### Board config (`config.toml`)

```toml
[[boards]]
url = "https://boards-api.greenhouse.io/v1/boards/temporaltechnologies/jobs"
departments = ["Engineering", "Developer Relations"]  # optional allowlist

[[boards]]
url = "https://api.rippling.com/platform/api/ats/v1/board/<slug>/jobs"
```

- Each `[[boards]]` entry has a `url` (required) and an optional `departments` allowlist.
- Department match is case-insensitive, exact name. Omit the list to allow every job from that board.

## Testing

```bash
uv run pytest
```

## Project Structure

```
job_crawler/
├── bot.py            # CLI entrypoint
├── settings.py       # Environment variable settings
├── board_config.py   # TOML board/allowlist loader
├── greenhouse.py     # Greenhouse API client and Job dataclass
├── ripling.py        # Rippling API client
├── controller.py     # Multi-board fetcher with department filter
├── state.py          # Valkey-backed job deduplication
├── summarize.py      # OpenAI-compatible LLM summarizer
├── notify.py         # Markdown body builder for Apprise
├── apprise_sink.py   # Apprise API HTTP client
└── preflight.py      # Service health checks (Valkey, LLM)
```
