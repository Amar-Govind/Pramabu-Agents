from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from pramabu_agents.models import CreativeBrief, PosterAsset


def _hex_to_rgb(value: str, fallback: tuple[int, int, int]) -> tuple[int, int, int]:
    text = (value or "").strip().lstrip("#")
    if len(text) != 6:
        return fallback
    try:
        return tuple(int(text[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
    except ValueError:
        return fallback


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug[:60] or "poster"


def _load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _find_logo() -> Path | None:
    candidates = [
        Path("storefront/public/brand/logo-wordmark-transparent.png"),
        Path("storefront/public/brand/logo-stacked-transparent.png"),
        Path("storefront/public/brand/logo-gold.png"),
        Path("brand/logo-gold.png"),
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def render_poster(
    creative: CreativeBrief,
    *,
    brand_name: str,
    website: str,
    colors: list[str],
    output_path: Path,
    width: int = 1080,
    height: int = 1350,
) -> PosterAsset:
    """Render a branded Instagram-ready poster PNG from a creative brief."""
    gold = _hex_to_rgb(colors[0] if colors else "#D6AA84", (214, 170, 132))
    forest = _hex_to_rgb(colors[1] if len(colors) > 1 else "#1B4332", (27, 67, 50))
    cream = _hex_to_rgb(colors[2] if len(colors) > 2 else "#F7F1E4", (247, 241, 228))
    ink = _hex_to_rgb(colors[3] if len(colors) > 3 else "#1A1A1A", (26, 26, 26))

    image = Image.new("RGB", (width, height), cream)
    draw = ImageDraw.Draw(image)

    # Atmosphere: top forest wash + soft gold glow
    draw.rectangle((0, 0, width, int(height * 0.42)), fill=forest)
    draw.ellipse(
        (int(width * 0.15), int(height * 0.08), int(width * 0.85), int(height * 0.55)),
        fill=(max(0, forest[0] - 8), max(0, forest[1] - 8), max(0, forest[2] - 8)),
    )
    draw.ellipse(
        (int(width * 0.55), -80, width + 120, int(height * 0.28)),
        fill=(gold[0], gold[1], gold[2]),
    )

    # Decorative fan-leaf arcs (simple brand motif)
    cx, cy = int(width * 0.22), int(height * 0.22)
    for i, radius in enumerate(range(40, 180, 18)):
        bbox = (cx - radius, cy - radius, cx + radius, cy + radius)
        start = 200 + i * 2
        end = 250 + i
        draw.arc(bbox, start=start, end=end, fill=gold, width=3)

    # Content panel
    panel = (72, int(height * 0.38), width - 72, height - 120)
    draw.rounded_rectangle(panel, radius=28, fill=(255, 250, 240), outline=gold, width=3)

    logo_path = _find_logo()
    y = panel[1] + 48
    if logo_path:
        logo = Image.open(logo_path).convert("RGBA")
        logo.thumbnail((360, 120), Image.Resampling.LANCZOS)
        lx = (width - logo.size[0]) // 2
        image.paste(logo, (lx, y), logo)
        y += logo.size[1] + 36
    else:
        brand_font = _load_font(42, bold=True)
        bw = draw.textlength(brand_name.upper(), font=brand_font)
        draw.text(((width - bw) / 2, y), brand_name.upper(), font=brand_font, fill=forest)
        y += 70

    headline_font = _load_font(54, bold=True)
    body_font = _load_font(30)
    meta_font = _load_font(24)
    cta_font = _load_font(28, bold=True)

    max_text_width = panel[2] - panel[0] - 80
    headline_lines = _wrap_text(draw, creative.headline, headline_font, max_text_width)
    for line in headline_lines[:4]:
        lw = draw.textlength(line, font=headline_font)
        draw.text(((width - lw) / 2, y), line, font=headline_font, fill=ink)
        y += 66

    y += 18
    draw.line((width // 2 - 60, y, width // 2 + 60, y), fill=gold, width=3)
    y += 28

    body_lines = _wrap_text(draw, creative.body, body_font, max_text_width)
    for line in body_lines[:5]:
        lw = draw.textlength(line, font=body_font)
        draw.text(((width - lw) / 2, y), line, font=body_font, fill=(60, 60, 60))
        y += 40

    # CTA chip
    cta = "Shop now"
    cta_pad_x, cta_pad_y = 34, 16
    cta_w = draw.textlength(cta, font=cta_font) + cta_pad_x * 2
    cta_h = 54
    cta_x = (width - cta_w) / 2
    cta_y = panel[3] - 150
    draw.rounded_rectangle(
        (cta_x, cta_y, cta_x + cta_w, cta_y + cta_h),
        radius=12,
        fill=gold,
    )
    tw = draw.textlength(cta, font=cta_font)
    draw.text((cta_x + (cta_w - tw) / 2, cta_y + cta_pad_y - 2), cta, font=cta_font, fill=ink)

    site = website.replace("https://", "").replace("http://", "")
    sw = draw.textlength(site, font=meta_font)
    draw.text(((width - sw) / 2, panel[3] - 70), site, font=meta_font, fill=forest)

    # Footer bar
    draw.rectangle((0, height - 70, width, height), fill=forest)
    tag = "Everyday Pure & Natural"
    tag_w = draw.textlength(tag, font=meta_font)
    draw.text(((width - tag_w) / 2, height - 48), tag, font=meta_font, fill=cream)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, format="PNG", optimize=True)

    return PosterAsset(
        idea_title=creative.idea_title,
        headline=creative.headline,
        path=str(output_path),
        width=width,
        height=height,
        format=creative.format,
    )
