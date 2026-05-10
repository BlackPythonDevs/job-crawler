from __future__ import annotations

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

SYSTEM_PROMPT = (
    "You summarize job postings in 1-2 short sentences. "
    "Focus on the role, key responsibilities, and team. "
    "Keep it concise and plain-language."
)


def _make_agent(base_url: str, api_key: str, model: str) -> Agent[None, str]:
    provider = OpenAIProvider(base_url=base_url, api_key=api_key)
    return Agent(
        OpenAIModel(model, provider=provider),
        system_prompt=SYSTEM_PROMPT,
        output_type=str,
    )


async def summarize_job(
    base_url: str, api_key: str, model: str, content: str
) -> str:
    agent = _make_agent(base_url, api_key, model)
    result = await agent.run(content)
    return result.output
