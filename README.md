# Job Crawler

A Discord bot that fetches job postings from [Greenhouse](https://www.greenhouse.io/) boards, generates AI-powered summaries via [Ollama](https://ollama.com/) (using [Pydantic AI](https://ai.pydantic.dev/)), and posts new listings to a Discord channel. [Valkey](https://valkey.io/) (Redis-compatible) tracks already-posted jobs to prevent duplicates.

> **Note:** A [Rippling](https://www.rippling.com/) client and multi-source controller exist in the codebase but are not yet wired into the bot.

## Architecture

```mermaid
flowchart LR
    subgraph External Services
        GH[Greenhouse API]
        DC[Discord Channel]
    end

    subgraph Docker Compose
        subgraph Bot Container
            BOT[Bot / Polling Loop]
            PF[Preflight Checks]
            CFG[Config]
            EMB[Embed Builder]
            SUM[Summarizer — Pydantic AI]
            GHC[Greenhouse Client]
        end
        VK[(Valkey)]
        OL[Ollama LLM]
    end

    BOT --> PF
    PF -->|health check| VK
    PF -->|health check| OL
    BOT --> CFG
    BOT --> GHC
    GHC -->|fetch jobs| GH
    BOT -->|filter new| VK
    BOT --> SUM
    SUM -->|summarize| OL
    BOT --> EMB
    EMB -->|post embed| DC
    BOT -->|mark posted| VK
```

## Prerequisites

- Python 3.14+
- A Discord bot token and target channel ID
- Valkey (or Redis) instance
- Ollama instance with your preferred model

## Quickstart

### With Docker Compose

```bash
cp .env.example .env
# Edit .env with your values
docker compose up --build
```

This starts three services: the bot, Valkey, and Ollama.

### Local Development

```bash
uv sync
cp .env.example .env
# Edit .env with your values
job-crawler
```

### CLI Options

```
job-crawler              # Run the bot (polls once, posts to Discord, then exits)
job-crawler --dry-run    # Preview jobs locally without Discord
job-crawler --limit 5    # Cap the number of jobs posted per cycle
job-preflight            # Check that Valkey and Ollama are reachable
```

## Configuration

All configuration is via environment variables. See [`.env.example`](.env.example).

| Variable | Required | Default | Description |
|---|---|---|---|
| `DISCORD_TOKEN` | Yes | — | Discord bot token (not required for `--dry-run`) |
| `DISCORD_CHANNEL_ID` | Yes | — | Channel to post job listings (not required for `--dry-run`) |
| `VALKEY_URL` | No | `valkey://localhost:6379/0` | Valkey/Redis connection URL |
| `JOB_TTL_SECONDS` | No | `7776000` (90 days) | How long to remember posted jobs |
| `GREENHOUSE_BOARD_URL` | No | Temporal Technologies board | Greenhouse board API endpoint |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434/v1` | Ollama API URL (read by Pydantic AI) |
| `OLLAMA_MODEL` | No | `ministral-3` | LLM model for summarization |

## Testing

```bash
uv run pytest
```

## Project Structure

```
job_crawler/
├── bot.py          # Discord bot, polling loop, and CLI entrypoint
├── config.py       # Environment variable configuration
├── greenhouse.py   # Greenhouse API client and Job dataclass
├── ripling.py      # Rippling API client (not yet wired in)
├── controller.py   # Multi-source job fetcher router (not yet wired in)
├── state.py        # Valkey-backed job deduplication
├── summarize.py    # LLM summarization via Pydantic AI + Ollama
├── embeds.py       # Discord embed builder
└── preflight.py    # Service health checks (Valkey, Ollama)
```
