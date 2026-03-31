# Job Crawler

A Discord bot that fetches job postings from job boards (e.g. [Greenhouse](https://www.greenhouse.io/), [Rippling](https://www.rippling.com/)), generates AI-powered summaries via [Ollama](https://ollama.com/), and posts new listings to a Discord channel. Valkey (Redis-compatible) tracks already-posted jobs to prevent duplicates.

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
            SUM[Summarizer]
            GHC[Greenhouse Client]
        end
        VK[(Valkey)]
        OL[Ollama LLM]
    end

    PF -->|health check| VK
    PF -->|health check| OL
    BOT --> CFG
    BOT --> PF
    BOT --> GHC
    GHC -->|fetch jobs| GH
    BOT -->|filter new jobs| VK
    BOT --> SUM
    SUM -->|summarize job| OL
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
| `DISCORD_TOKEN` | Yes | — | Discord bot token |
| `DISCORD_CHANNEL_ID` | Yes | — | Channel to post job listings |
| `VALKEY_URL` | No | `valkey://localhost:6379/0` | Valkey/Redis connection URL |
| `JOB_TTL_SECONDS` | No | `7776000` (90 days) | How long to remember posted jobs |
| `GREENHOUSE_BOARD_URL` | No | Temporal Technologies board | Greenhouse board API endpoint |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434/v1` | Ollama API URL |
| `OLLAMA_MODEL` | No | `ministral-3` | LLM model for summarization |

## Testing

```bash
uv run pytest
```
