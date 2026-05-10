# Job Crawler

A long-running crawler that fetches job postings from [Greenhouse](https://www.greenhouse.io/) and [Rippling](https://www.rippling.com/) boards, summarizes them via any OpenAI-compatible LLM endpoint (using [Pydantic AI](https://ai.pydantic.dev/)), and posts new listings through an [Apprise API](https://github.com/caronc/apprise-api) endpoint. [Valkey](https://valkey.io/) tracks posted jobs to prevent duplicates. A small FastAPI status server exposes runtime info.

## Quickstart

```bash
cp .env.example .env
cp config.toml.example config.toml
# Edit both
docker compose up --build
```

For a guided walkthrough, see [Get your first job posting delivered](docs/tutorials/first-job-posting.md).

## Documentation

Full documentation is in [`docs/`](docs/), organized in [Diátaxis](https://diataxis.fr/) form:

- **[Tutorials](docs/tutorials/)** — learn by doing.
- **[How-to guides](docs/how-to/)** — solve a specific problem.
- **[Reference](docs/reference/)** — exact details (env vars, config, API, CLI).
- **[Explanation](docs/explanation/)** — design rationale.

## Testing

```bash
uv run pytest
```
