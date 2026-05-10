# Environment variables

All runtime configuration is via environment variables. See [`.env.example`](../../.env.example).

| Variable | Required | Default | Description |
|---|---|---|---|
| `APPRISE_URL` | Yes | — | Apprise API notify endpoint. Not required when running with `--dry-run`. |
| `LLM_BASE_URL` | No | `http://localhost:11434/v1` | OpenAI-compatible base URL. |
| `MODEL_NAME` | No | `ministral-3` | Model name sent in chat completion requests. |
| `LLM_API_KEY` | No | `not-needed` | Bearer token. Ollama ignores it. |
| `VALKEY_URL` | No | `valkey://localhost:6379/0` | Valkey/Redis connection URL. |
| `JOB_TTL_SECONDS` | No | `7776000` | How long a posted job is remembered (90 days). |
| `POLL_INTERVAL_SECONDS` | No | `14400` | Seconds between polls (4 hours). |
| `JOB_CRAWLER_CONFIG` | No | `./config.toml` | Path to the TOML board config file. |
| `API_HOST` | No | `0.0.0.0` | FastAPI bind host. |
| `API_PORT` | No | `8080` | FastAPI bind port. |
| `LOG_FILE` | No | `/var/log/job-crawler/job-crawler.log` | Rotating log file path (10 MB × 3). |

## Notes

- The bot reads env vars **once at startup**. Changing a variable requires a restart.
- The Pydantic AI SDK reads `LLM_BASE_URL` indirectly through the `OpenAIProvider` configured in `summarize.py`; you do not need to set `OPENAI_BASE_URL`.
