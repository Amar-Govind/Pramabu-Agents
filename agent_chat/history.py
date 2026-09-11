from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def history_path(session_dir: Path) -> Path:
    return session_dir / "history.json"


def load_history(session_dir: Path) -> list[dict[str, Any]]:
    path = history_path(session_dir)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_history(session_dir: Path, history: list[dict[str, Any]]) -> None:
    session_dir.mkdir(parents=True, exist_ok=True)
    history_path(session_dir).write_text(
        json.dumps(history[-40:], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def as_llm_messages(history: list[dict[str, Any]], limit: int = 16) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    for item in history[-limit:]:
        role = item.get("role")
        content = (item.get("content") or "").strip()
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})
    return messages
