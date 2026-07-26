from __future__ import annotations

import re
from typing import Any


def extract_focus(message: str, brand: dict[str, Any]) -> dict[str, Any]:
    """Pull product/category focus from a user message so template replies vary."""
    text = (message or "").lower()
    products = brand.get("products", [])

    matched_products: list[dict[str, Any]] = []
    for product in products:
        name = str(product.get("name", ""))
        tokens = [t for t in re.split(r"[^a-z0-9]+", name.lower()) if len(t) > 2]
        # Match full name or distinctive tokens (neem, rose, charcoal, coco, virgin...)
        if name and name.lower() in text:
            matched_products.append(product)
            continue
        distinctive = [t for t in tokens if t not in {"soap", "oil", "organic", "handcrafted", "low", "high"}]
        if distinctive and all(token in text for token in distinctive[:2] if distinctive):
            # if one strong token matches, accept
            if any(token in text for token in distinctive):
                matched_products.append(product)

    # de-dupe preserving order
    seen: set[str] = set()
    unique_products = []
    for product in matched_products:
        key = product.get("sku") or product.get("name")
        if key in seen:
            continue
        seen.add(key)
        unique_products.append(product)

    categories = []
    for label, aliases in (
        ("Soap", ["soap", "skin", "bar"]),
        ("Oils", ["oil", "hair", "vco", "coconut"]),
        ("Gardening", ["garden", "gardening", "coco", "cocopeat", "plant"]),
    ):
        if any(alias in text for alias in aliases):
            categories.append(label)

    formats = [fmt for fmt in ("poster", "reel", "short", "carousel") if fmt in text]

    return {
        "products": unique_products,
        "product_names": [p.get("name") for p in unique_products if p.get("name")],
        "categories": categories,
        "formats": formats,
        "raw": message.strip(),
    }
