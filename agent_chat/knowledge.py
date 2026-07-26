from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from pramabu_agents.config import DEFAULT_BRAND_PATH, load_brand


def _product_blurb(product: dict[str, Any]) -> str:
    benefits = "; ".join(product.get("benefits") or [])
    price = product.get("price_inr")
    price_bit = f" Price ₹{price}." if price else ""
    return (
        f"{product.get('name')} ({product.get('category')}) — {benefits}.{price_bit} "
        f"URL: {product.get('url', '')}"
    )


def brand_knowledge_chunks(brand: dict[str, Any] | None = None) -> list[dict[str, str]]:
    data = brand or load_brand()
    b = data.get("brand", {})
    voice = b.get("voice", {})
    chunks = [
        {
            "id": "brand-overview",
            "title": "Brand overview",
            "text": (
                f"{b.get('name')} ({b.get('short_name')}) — {b.get('tagline')}. "
                f"Category: {b.get('category')}. Website: {b.get('website')}. "
                f"Markets: {', '.join(b.get('markets') or [])}. "
                f"Categories: {', '.join(b.get('categories') or [])}."
            ),
        },
        {
            "id": "brand-voice",
            "title": "Brand voice",
            "text": (
                f"Tone: {voice.get('tone')}. "
                f"Do: {'; '.join(voice.get('do') or [])}. "
                f"Don't: {'; '.join(voice.get('dont') or [])}."
            ),
        },
        {
            "id": "compliance",
            "title": "Compliance",
            "text": "Forbidden claims: "
            + ", ".join((b.get("compliance") or {}).get("forbidden_claims") or []),
        },
    ]

    for product in data.get("products") or []:
        chunks.append(
            {
                "id": f"product-{(product.get('sku') or product.get('name', 'sku')).lower()}",
                "title": f"Product: {product.get('name')}",
                "text": _product_blurb(product),
            }
        )

    goals = data.get("goals") or {}
    if goals:
        chunks.append(
            {
                "id": "goals",
                "title": "Goals & KPIs",
                "text": (
                    f"Primary: {'; '.join(goals.get('primary') or [])}. "
                    f"KPIs: {', '.join(goals.get('kpis') or [])}."
                ),
            }
        )

    channels = data.get("channels") or {}
    if channels:
        chunks.append(
            {
                "id": "channels",
                "title": "Channels",
                "text": json.dumps(channels, ensure_ascii=False),
            }
        )

    # Optional storefront site copy
    site_path = Path("storefront/src/data/site.json")
    if site_path.exists():
        try:
            site = json.loads(site_path.read_text(encoding="utf-8"))
            chunks.append(
                {
                    "id": "storefront-site",
                    "title": "Storefront site copy",
                    "text": json.dumps(site, ensure_ascii=False)[:4000],
                }
            )
        except Exception:
            pass

    # Raw brand bible for completeness
    if DEFAULT_BRAND_PATH.exists():
        raw = DEFAULT_BRAND_PATH.read_text(encoding="utf-8")
        chunks.append({"id": "brand-bible-yaml", "title": "Brand bible", "text": raw[:8000]})

    return chunks


def score_chunk(query: str, chunk: dict[str, str]) -> float:
    q = query.lower()
    text = f"{chunk.get('title', '')} {chunk.get('text', '')}".lower()
    score = 0.0
    for token in set(q.replace("/", " ").replace("-", " ").split()):
        if len(token) < 3:
            continue
        if token in text:
            score += 1.0
            if token in chunk.get("title", "").lower():
                score += 1.5
    return score


def retrieve_knowledge(
    query: str,
    *,
    extra_chunks: list[dict[str, str]] | None = None,
    brand: dict[str, Any] | None = None,
    limit: int = 8,
) -> list[dict[str, str]]:
    chunks = brand_knowledge_chunks(brand)
    if extra_chunks:
        chunks.extend(extra_chunks)
    ranked = sorted(chunks, key=lambda c: score_chunk(query, c), reverse=True)
    selected = [c for c in ranked if score_chunk(query, c) > 0][:limit]
    if not selected:
        # Always give core brand context
        selected = chunks[:4]
    return selected


def format_knowledge_block(chunks: list[dict[str, str]]) -> str:
    parts = []
    for chunk in chunks:
        parts.append(f"### {chunk['title']}\n{chunk['text']}")
    return "\n\n".join(parts)


def attachment_chunks(attachment_summary: dict[str, Any]) -> list[dict[str, str]]:
    chunks = []
    for doc in attachment_summary.get("documents") or []:
        chunks.append(
            {
                "id": f"upload-{doc.get('name')}",
                "title": f"Uploaded document: {doc.get('name')}",
                "text": (doc.get("text") or "")[:5000],
            }
        )
    for image in attachment_summary.get("images") or []:
        name = Path(image).name
        chunks.append(
            {
                "id": f"image-{name}",
                "title": f"Uploaded image: {name}",
                "text": f"User uploaded image file at {image}. Use it as creative reference when relevant.",
            }
        )
    return chunks


def dump_brand_snapshot() -> str:
    """Compact brand snapshot for system prompts."""
    brand = load_brand()
    return yaml.safe_dump(
        {
            "brand": brand.get("brand", {}),
            "products": [
                {
                    "name": p.get("name"),
                    "category": p.get("category"),
                    "price_inr": p.get("price_inr"),
                    "benefits": p.get("benefits"),
                    "url": p.get("url"),
                }
                for p in (brand.get("products") or [])
            ],
            "goals": brand.get("goals"),
            "channels": brand.get("channels"),
        },
        sort_keys=False,
    )
