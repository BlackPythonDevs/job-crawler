# CLI

The package installs two scripts.

## `job-crawler`

Main entrypoint.

| Flag | Description |
|---|---|
| _(none)_ | Long-running mode: poll loop + FastAPI server. The default for production. |
| `--once` | Run a single poll cycle, then exit. The API server is not started. |
| `--dry-run` | Fetch + summarize jobs and print to stdout. No Apprise post, no Valkey write. `APPRISE_URL` not required. |
| `--limit N` | Cap the number of jobs posted per cycle to N. Combine with any of the modes above. |

## `job-preflight`

Verifies that Valkey and the LLM endpoint are reachable, and that `MODEL_NAME` is available at `LLM_BASE_URL`. Exits non-zero on failure.

Run before launching the bot to catch misconfiguration early. The bot also runs preflight on startup automatically.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success (or graceful shutdown). |
| `1` | Preflight failure or fatal startup error. |
