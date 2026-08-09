from __future__ import annotations

import json
import os
from typing import Any

from pramabu_agents.config import llm_enabled, openai_model


def complete_json(system: str, user: str, fallback: dict[str, Any]) -> dict[str, Any]:
    """Return structured JSON from an LLM, or the deterministic fallback."""
    if not llm_enabled():
        return fallback

    try:
        from openai import OpenAI
    except ImportError:
        return fallback

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=openai_model(),
        temperature=0.4,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    content = response.choices[0].message.content or "{}"
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return fallback


def complete_chat(
    *,
    system: str,
    messages: list[dict[str, str]],
    fallback: str,
    temperature: float = 0.5,
) -> tuple[str, dict[str, Any]]:
    """Free-form conversational completion with history.

    Returns (text, meta) where meta includes ok/error details for the UI.
    """
    if not llm_enabled():
        return fallback, {
            "ok": False,
            "provider": "local-knowledge",
            "error": "OPENAI_API_KEY is not set",
        }

    try:
        from openai import OpenAI
    except ImportError:
        return fallback, {
            "ok": False,
            "provider": "local-knowledge",
            "error": "openai package is not installed",
        }

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=openai_model(),
            temperature=temperature,
            messages=[{"role": "system", "content": system}, *messages],
        )
        content = (response.choices[0].message.content or "").strip()
        if not content:
            return fallback, {
                "ok": False,
                "provider": "openai",
                "error": "Empty model response",
            }
        return content, {
            "ok": True,
            "provider": "openai",
            "model": openai_model(),
        }
    except Exception as exc:  # noqa: BLE001
        return fallback, {
            "ok": False,
            "provider": "local-knowledge",
            "error": str(exc),
        }
