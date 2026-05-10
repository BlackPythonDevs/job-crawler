# Job Crawler Documentation

This documentation follows the [Diátaxis](https://diataxis.fr/) framework. Pick the section that matches what you're trying to do:

| You want to... | Go to |
|---|---|
| Learn the project by following along | [Tutorials](tutorials/) |
| Solve a specific problem | [How-to guides](how-to/) |
| Look up exact details | [Reference](reference/) |
| Understand why things work the way they do | [Explanation](explanation/) |

## Tutorials

- [Get your first job posting delivered](tutorials/first-job-posting.md)

## How-to guides

- [Add a new job board](how-to/add-a-board.md)
- [Filter jobs by department](how-to/filter-by-department.md)
- [Point the LLM at OpenAI instead of Ollama](how-to/use-openai-instead-of-ollama.md)
- [Trigger a manual poll](how-to/trigger-manual-poll.md)
- [Run locally without Docker](how-to/run-without-docker.md)

## Reference

- [Environment variables](reference/environment-variables.md)
- [`config.toml` schema](reference/config-toml.md)
- [HTTP API](reference/http-api.md)
- [CLI](reference/cli.md)

## Explanation

- [Architecture](explanation/architecture.md)
- [Why Apprise instead of Discord directly](explanation/why-apprise.md)
- [Why an OpenAI-compatible LLM endpoint](explanation/why-openai-compatible.md)
- [Deduplication strategy](explanation/deduplication.md)
