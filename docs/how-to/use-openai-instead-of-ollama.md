# Point the LLM at OpenAI instead of Ollama

The summarizer talks to any OpenAI-compatible `/v1` endpoint. Switching from Ollama (the default) to OpenAI's hosted API is a configuration change.

## OpenAI

In `.env`:

```
LLM_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini
LLM_API_KEY=sk-...your key...
```

Restart the bot.

## Other providers

Any provider that ships an OpenAI-compatible API works the same way. Examples:

- **OpenRouter** — `LLM_BASE_URL=https://openrouter.ai/api/v1`, `MODEL_NAME=anthropic/claude-3.5-haiku`, `LLM_API_KEY=sk-or-...`
- **vLLM** — `LLM_BASE_URL=http://your-vllm:8000/v1`, `MODEL_NAME=` whatever you served, `LLM_API_KEY=not-needed`
- **Groq** — `LLM_BASE_URL=https://api.groq.com/openai/v1`, plus a Groq API key

## Verify

```bash
job-preflight
```

Preflight calls `GET {LLM_BASE_URL}/models` and checks that `MODEL_NAME` appears in the list. If preflight passes, summarization will work.

## Cost note

The bot calls the LLM once per new job per cycle. With a 4-hour interval and a typical board, expect tens of calls per day. Hosted APIs charge per call — see your provider's pricing.
