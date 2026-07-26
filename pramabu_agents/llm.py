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
) -> str:
    """Free-form conversational completion with history."""
    if not llm_enabled():
        return fallback

    try:
        from openai import OpenAI
    except ImportError:
        return fallback

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=openai_model(),
            temperature=temperature,
            messages=[{"role": "system", "content": system}, *messages],
        )
        content = (response.choices[0].message.content or "").strip()
        return content or fallback
    except Exception:
        return fallback
