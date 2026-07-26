from __future__ import annotations

import re
from typing import Any

from agent_chat.focus import extract_focus
from pramabu_agents.config import load_brand


def _product_card(product: dict[str, Any]) -> str:
    benefits = "; ".join(product.get("benefits") or [])
    return (
        f"**{product.get('name')}** ({product.get('category')}) — ₹{product.get('price_inr')}.\n"
        f"{benefits}\n"
        f"Shop: {product.get('url')}"
    )


def _draft_caption(product: dict[str, Any], brand: dict[str, Any]) -> str:
    name = product.get("name", "Parambu")
    benefit = (product.get("benefits") or ["Pure heritage care"])[0]
    website = (brand.get("brand") or {}).get("website", "https://parambu.in")
    tagline = (brand.get("brand") or {}).get("tagline", "Everyday Pure & Natural")
    return (
        f"Soft mornings. Honest ingredients.\n"
        f"{name} — {benefit.lower()}.\n"
        f"{tagline}.\n"
        f"Shop now: {website}\n\n"
        f"#ParambuOrganics #EverydayPureAndNatural #OrganicLiving"
    )


def _last_mentioned_product(history: list[dict[str, Any]], brand: dict[str, Any]) -> dict[str, Any] | None:
    products = brand.get("products") or []
    # Search newest assistant/user messages for a product name
    for item in reversed(history or []):
        text = str(item.get("content") or "").lower()
        for product in products:
            name = str(product.get("name") or "").lower()
            if name and name in text:
                return product
            token = name.split()[0] if name else ""
            if len(token) > 3 and token in text and token not in {"virgin", "coco", "handcrafted"}:
                return product
    return None


def local_chat_reply(
    *,
    message: str,
    history: list[dict[str, Any]] | None = None,
    knowledge: str = "",
    tool_facts: str | None = None,
    agent_name: str = "Parambu Assistant",
) -> str:
    """Richer local assistant when OPENAI_API_KEY is not configured."""
    brand = load_brand()
    focus = extract_focus(message, brand)
    matched = list(focus.get("products") or [])
    lowered = message.lower().strip()
    history = history or []

    if tool_facts:
        return (
            f"Done — I ran **{agent_name}** for you.\n\n"
            f"{tool_facts}\n\n"
            "Download the files from the chips below. "
            "Want me to adjust the tone, focus on another product, or draft matching captions?"
        )

    if re.search(r"\b(hi|hello|hey|good morning|good evening)\b", lowered):
        return (
            "Hi — I’m **Parambu Assistant**, your brand chat for Parambu Organics.\n\n"
            "I can answer from the brand bible/products, draft captions, and create posters or campaign packs.\n\n"
            "Try:\n"
            "- What’s special about Rose Soap?\n"
            "- Write an Instagram caption for Virgin Coconut Oil\n"
            "- Create posters for neem soap\n\n"
            "_Tip: add `OPENAI_API_KEY` in `.env` for full LLM chat quality._"
        )

    wants_caption = any(
        k in lowered
        for k in ("caption", "instagram", "rewrite", "hook", "copy", "post text", "ad text")
    )
    asks_price = "price" in lowered or "cost" in lowered or "how much" in lowered

    product = matched[0] if matched else _last_mentioned_product(history, brand)

    if wants_caption:
        if not product:
            product = next((p for p in brand.get("products") or [] if p.get("name") == "Rose Soap"), None)
            product = product or (brand.get("products") or [None])[0]
        if product:
            return (
                f"Here’s a brand-safe Instagram caption for **{product.get('name')}**:\n\n"
                f"{_draft_caption(product, brand)}\n\n"
                "I can make a Tamil/English version, a shorter hook, or generate a matching poster."
            )

    if asks_price and product:
        return (
            f"**{product.get('name')}** is listed at **₹{product.get('price_inr')}** on "
            f"{product.get('url')}.\n\nWant a caption or poster for it?"
        )

    if product:
        voice = (brand.get("brand") or {}).get("voice") or {}
        return (
            "Here’s what I know from the Parambu knowledge base:\n\n"
            f"{_product_card(product)}\n\n"
            f"Brand tone: {voice.get('tone', 'warm, natural, heritage-rooted')}.\n\n"
            "Ask me for a caption, comparison, or poster next."
        )

    if any(k in lowered for k in ("voice", "tone", "claim", "brand bible", "forbidden")):
        voice = (brand.get("brand") or {}).get("voice") or {}
        forbidden = ((brand.get("brand") or {}).get("compliance") or {}).get("forbidden_claims") or []
        return (
            f"Parambu voice: **{voice.get('tone', 'warm and natural')}**.\n\n"
            f"**Do:** {'; '.join(voice.get('do') or [])}\n\n"
            f"**Don’t:** {'; '.join(voice.get('dont') or [])}\n\n"
            f"**Forbidden claims:** {', '.join(forbidden)}\n\n"
            "Paste any draft and I’ll rewrite it in brand voice."
        )

    if any(k in lowered for k in ("llm", "openai", "api key", "not working", "broken")):
        return (
            "The chat app is running, but **live LLM mode is off** because `OPENAI_API_KEY` is not set.\n\n"
            "To enable your Parambu LLM chat:\n"
            "1. `cp .env.example .env`\n"
            "2. Put your key in `.env` as `OPENAI_API_KEY=sk-...`\n"
            "3. Restart: `python -m agent_chat.app`\n\n"
            "Until then I still answer from the Parambu knowledge base and can generate posters/campaign files."
        )

    # Generic grounded response
    snippet = "\n\n".join((knowledge or "").split("\n\n")[:2]) or "Parambu Organics brand bible is loaded."
    return (
        "I can help with that using the Parambu knowledge base.\n\n"
        f"{snippet}\n\n"
        "Ask about a product, brand voice, captions, or say **create posters for Rose Soap** to generate files.\n\n"
        "_For fuller LLM conversation quality, add `OPENAI_API_KEY` to `.env`._"
    )
