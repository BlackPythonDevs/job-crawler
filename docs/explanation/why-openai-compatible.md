# Why an OpenAI-compatible LLM endpoint

Earlier versions used Pydantic AI's Ollama provider directly. That meant the only way to swap in a different model host was to edit `summarize.py`.

The OpenAI chat-completions API has become a de facto standard. Ollama, vLLM, OpenRouter, Groq, LM Studio, llama.cpp's server, and OpenAI itself all speak it. By targeting that protocol instead of one specific implementation, we get every one of those for free.

## What changed

- `summarize.py` builds an `OpenAIModel` against an `OpenAIProvider(base_url=..., api_key=...)`.
- Three env vars now configure the LLM: `LLM_BASE_URL`, `MODEL_NAME`, `LLM_API_KEY`.
- Preflight checks `GET {LLM_BASE_URL}/models` and verifies `MODEL_NAME` is in the response.
- The Ollama-specific Compose service is gone. You bring your own LLM endpoint.

## Trade-offs

- An extra moving part: you have to run the LLM somewhere. The default URL still points at a local Ollama, so the laptop dev story doesn't change.
- Provider-specific features (e.g. function-calling syntax variants, structured output controls) are only available to the extent both Pydantic AI and the provider implement the OpenAI-shape contract.
- API keys for paid providers add a real cost dimension — see [Point the LLM at OpenAI instead of Ollama](../how-to/use-openai-instead-of-ollama.md).

## Why not `pydantic-ai`'s native multi-provider support?

Pydantic AI does support multiple providers natively, but the code path differs per provider. Coupling to one shape (OpenAI) keeps the summarizer small (~20 lines) and the configuration surface small (three env vars).
