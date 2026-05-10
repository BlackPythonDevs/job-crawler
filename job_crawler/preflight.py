"""Preflight checks for required services (Valkey, LLM)."""

from __future__ import annotations

import os
import sys

import httpx
import valkey


def check_valkey(url: str) -> bool:
    try:
        client = valkey.from_url(url)
        client.ping()
        return True
    except Exception as exc:
        print(f"  Valkey ({url}): {exc}")
        return False


def check_llm(base_url: str, api_key: str, model: str) -> bool:
    """GET {base_url}/models and verify the requested model is available."""
    url = f"{base_url.rstrip('/')}/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        resp = httpx.get(url, headers=headers, timeout=5)
        resp.raise_for_status()
        payload = resp.json()
        items = payload.get("data") if isinstance(payload, dict) else None
        models = [m.get("id", "") for m in (items or [])]
        # Match exact or case-insensitive prefix (Ollama returns "name:tag")
        target = model.casefold()
        if not any(
            m.casefold() == target or m.casefold().split(":")[0] == target
            for m in models
        ):
            print(f"  LLM: model '{model}' not found (available: {models})")
            return False
        return True
    except Exception as exc:
        print(f"  LLM ({base_url}): {exc}")
        return False


def run() -> None:
    valkey_url = os.getenv("VALKEY_URL", "valkey://localhost:6379/0")
    llm_base = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
    llm_api_key = os.getenv("LLM_API_KEY", "not-needed")
    model = os.getenv("MODEL_NAME", "ministral-3")

    print("[preflight] Checking required services...")

    print(f"[preflight] Checking Valkey at {valkey_url} ...")
    valkey_ok = check_valkey(valkey_url)
    print(f"[preflight] Valkey: {'ok' if valkey_ok else 'FAILED'}")

    print(f"[preflight] Checking LLM for model '{model}' at {llm_base} ...")
    llm_ok = check_llm(llm_base, llm_api_key, model)
    print(f"[preflight] LLM: {'ok' if llm_ok else 'FAILED'}")

    if not all([valkey_ok, llm_ok]):
        print("[preflight] Preflight failed — aborting.")
        sys.exit(1)

    print("[preflight] All services ready.\n")


if __name__ == "__main__":
    run()
