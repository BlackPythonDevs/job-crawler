"""Preflight checks for required services (Ollama, Valkey)."""

from __future__ import annotations

import os
import sys

import httpx
import valkey


def check_valkey(url: str) -> bool:
    """Ping Valkey and return True if it responds."""
    try:
        client = valkey.from_url(url)
        client.ping()
        return True
    except Exception as exc:
        print(f"  Valkey ({url}): {exc}")
        return False


def check_ollama(base_url: str, model: str) -> bool:
    """Hit the Ollama tags endpoint and verify the expected model is pulled."""
    # Strip /v1 suffix if present — the native Ollama API lives at the root.
    native_url = base_url.rstrip("/").removesuffix("/v1")
    tags_url = f"{native_url}/api/tags"
    try:
        resp = httpx.get(tags_url, timeout=5)
        resp.raise_for_status()
        models = [m["name"].split(":")[0] for m in resp.json().get("models", [])]
        if model not in models:
            print(f"  Ollama: model '{model}' not found (available: {models})")
            return False
        return True
    except Exception as exc:
        print(f"  Ollama ({base_url}): {exc}")
        return False


def run() -> None:
    valkey_url = os.getenv("VALKEY_URL", "valkey://localhost:6379/0")
    ollama_base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    ollama_model = os.getenv("OLLAMA_MODEL", "ministral-3")

    print("[preflight] Checking required services...")

    print(f"[preflight] Checking Valkey at {valkey_url} ...")
    valkey_ok = check_valkey(valkey_url)
    print(f"[preflight] Valkey: {'ok' if valkey_ok else 'FAILED'}")

    print(f"[preflight] Checking Ollama for model '{ollama_model}' at {ollama_base} ...")
    ollama_ok = check_ollama(ollama_base, ollama_model)
    print(f"[preflight] Ollama: {'ok' if ollama_ok else 'FAILED'}")

    if not all([valkey_ok, ollama_ok]):
        print("[preflight] Preflight failed — aborting.")
        sys.exit(1)

    print("[preflight] All services ready.\n")


if __name__ == "__main__":
    run()
