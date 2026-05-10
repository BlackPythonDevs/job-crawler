# Get your first job posting delivered

By the end of this tutorial you will have job-crawler running on your laptop and pushing a real Greenhouse job posting through an Apprise endpoint to a Discord channel of your choice.

You will need:

- Docker and Docker Compose
- A Discord webhook URL (Channel Settings → Integrations → Webhooks → New Webhook → Copy URL)
- An OpenAI-compatible LLM endpoint — for this tutorial we'll use a local [Ollama](https://ollama.com/) instance with `ministral-3` pulled

This tutorial will take about 15 minutes.

## 1. Pull a model into Ollama

```bash
ollama pull ministral:3b
```

Confirm it's there:

```bash
ollama list
```

## 2. Run an Apprise API instance

Apprise turns a single HTTP endpoint into many notification destinations. Run it locally:

```bash
docker run -d --name apprise -p 8000:8000 caronc/apprise:latest
```

Visit `http://localhost:8000` and add a configuration with a key of `job-crawler` and a single Discord URL of the form `discord://webhook_id/webhook_token` (you can derive this from the webhook URL Discord gave you — see the [Apprise Discord docs](https://github.com/caronc/apprise/wiki/Notify_discord)).

Save it. Your notify endpoint is now `http://localhost:8000/notify/job-crawler`.

## 3. Clone and configure job-crawler

```bash
git clone https://github.com/BlackPythonDevs/job-crawler
cd job-crawler
cp .env.example .env
cp config.toml.example config.toml
```

Edit `.env` so it points at the services running on your host:

```
APPRISE_URL=http://host.docker.internal:8000/notify/job-crawler
LLM_BASE_URL=http://host.docker.internal:11434/v1
MODEL_NAME=ministral:3b
```

Leave `config.toml` as-is — it crawls the Temporal Technologies Greenhouse board out of the box.

## 4. Start the bot

```bash
docker compose up --build
```

You should see preflight pass, then a fetch cycle log a count of jobs and post a handful through Apprise. Check your Discord channel — new postings should appear as embeds.

## 5. Confirm it's running

In another terminal:

```bash
curl http://localhost:8080/status
```

You'll get JSON with `last_firing`, `next_firing`, and `running: false`. The bot will poll again in 4 hours, or you can trigger an immediate poll:

```bash
curl -X POST http://localhost:8080/run
```

## What you've built

You now have a job-crawler that:

- Polls the Temporal Greenhouse board every 4 hours
- Summarizes each posting via your local Ollama
- Posts new jobs to your Discord webhook through Apprise
- Remembers what it has posted (90-day TTL) in Valkey
- Exposes a status API on port 8080

## Where to go next

- Add another board: see [Add a new job board](../how-to/add-a-board.md)
- Filter to specific departments: see [Filter jobs by department](../how-to/filter-by-department.md)
- Understand the architecture: see [Architecture](../explanation/architecture.md)
