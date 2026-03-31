from __future__ import annotations

from pydantic_ai import Agent

SYSTEM_PROMPT = (
    "You summarize job postings in 1-2 short sentences. "
    "Focus on the role, key responsibilities, and team. "
    "Keep it concise and plain-language."
)


def _make_agent(model: str) -> Agent[None, str]:
    return Agent(
        f"ollama:{model}",
        system_prompt=SYSTEM_PROMPT,
        output_type=str,
    )


async def summarize_job(model: str, content: str) -> str:
    agent = _make_agent(model)
    result = await agent.run(content)
    return result.output
