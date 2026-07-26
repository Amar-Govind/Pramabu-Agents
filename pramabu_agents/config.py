from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BRAND_PATH = ROOT / "brand" / "brand_bible.yaml"


def load_env() -> None:
    load_dotenv(ROOT / ".env", override=False)


def load_brand(path: Path | None = None) -> dict[str, Any]:
    brand_path = path or Path(os.getenv("BRAND_BIBLE_PATH", DEFAULT_BRAND_PATH))
    with brand_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # Optional env overrides
    brand = data.setdefault("brand", {})
    brand["name"] = os.getenv("BRAND_NAME", brand.get("name", "Parambu Organics"))
    brand["category"] = os.getenv("BRAND_CATEGORY", brand.get("category", "Organic FMCG"))
    brand["website"] = os.getenv("BRAND_WEBSITE", brand.get("website", "https://parambu.in"))
    channels = data.setdefault("channels", {})
    channels["website"] = brand["website"]
    return data


def llm_enabled() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def openai_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")
