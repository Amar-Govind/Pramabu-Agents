#!/usr/bin/env python3
"""Generate Parambu Organics grow kit seed pocket designs."""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
LOGO_PATH = ROOT.parents[2] / "storefront" / "public" / "brand" / "logo-wordmark-transparent.png"
PLANT_PHOTOS_DIR = ROOT / "plant-photos"
OUTPUT_DIR = ROOT / "output"

# Kraft paper palette from Parambu brand bible
CREAM = (247, 241, 228)  # #F7F1E4
KRAFT = (214, 186, 148)
KRAFT_DARK = (196, 164, 124)
FOREST = (27, 67, 50)  # #1B4332
GOLD = (214, 170, 132)  # #D6AA84

PACKETS = [
    ("tomato", "TOMATO"),
    ("chilli", "CHILLI"),
    ("brinjal-blue-white", "BRINJAL\nBLUE & WHITE"),
    ("okra-green", "OKRA GREEN"),
    ("drumsticks", "DRUMSTICKS"),
    ("bitter-gourd-long", "BITTER GOURD\nLONG"),
    ("coriander", "CORIANDER"),
    ("palak", "PALAK"),
    ("guava", "GUAVA"),
    ("black-nightshade", "BLACK\nNIGHTSHADE"),
    ("amaranthus", "AMARANTHUS"),
]

WIDTH = 900
HEIGHT = 1200


def make_kraft_texture(width: int, height: int) -> Image.Image:
    """Create a subtle kraft-paper background."""
    base = Image.new("RGB", (width, height), CREAM)
    pixels = base.load()
    rng = random.Random(42)
    for y in range(height):
        for x in range(width):
            noise = rng.randint(-12, 12)
            fiber = int(8 * math.sin(x / 17) * math.cos(y / 23))
            r = min(255, max(0, CREAM[0] + noise + fiber))
            g = min(255, max(0, CREAM[1] + noise + fiber - 4))
            b = min(255, max(0, CREAM[2] + noise + fiber - 8))
            pixels[x, y] = (r, g, b)

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for _ in range(120):
        x1 = rng.randint(0, width)
        y1 = rng.randint(0, height)
        x2 = x1 + rng.randint(-80, 80)
        y2 = y1 + rng.randint(-4, 4)
        draw.line((x1, y1, x2, y2), fill=(*KRAFT_DARK, 18), width=1)

    # Soft vignette
    vignette = Image.new("L", (width, height), 0)
    vdraw = ImageDraw.Draw(vignette)
    vdraw.ellipse((-width * 0.1, -height * 0.05, width * 1.1, height * 1.05), fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(80))
    dark = Image.new("RGBA", (width, height), (*KRAFT_DARK, 0))
    dark.putalpha(ImageOps.invert(vignette).point(lambda p: int(p * 0.08)))
    base = Image.alpha_composite(base.convert("RGBA"), overlay)
    base = Image.alpha_composite(base, dark)
    return base.convert("RGB")


def load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else (
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
    )
    return ImageFont.truetype(path, size)


def fit_image_cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(img.convert("RGBA"), size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))


def add_rounded_photo(canvas: Image.Image, photo: Image.Image, box: tuple[int, int, int, int], radius: int = 24) -> None:
    w = box[2] - box[0]
    h = box[3] - box[1]
    fitted = fit_image_cover(photo, (w, h))

    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    fitted.putalpha(mask)

    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.rounded_rectangle(
        (box[0] + 6, box[1] + 10, box[2] + 6, box[3] + 10),
        radius=radius,
        fill=(0, 0, 0, 45),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    canvas.alpha_composite(shadow)

    border = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(border)
    bdraw.rounded_rectangle((0, 0, w + 7, h + 7), radius=radius + 2, outline=(*GOLD, 220), width=3)
    canvas.paste(border, (box[0] - 4, box[1] - 4), border)
    canvas.alpha_composite(fitted, (box[0], box[1]))


def draw_centered_multiline(
    draw: ImageDraw.ImageDraw,
    text: str,
    y_start: int,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    width: int,
) -> int:
    lines = text.split("\n")
    line_height = font.size + 8
    total_h = len(lines) * line_height
    y = y_start
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (width - tw) // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y_start + total_h


def create_seed_pocket(slug: str, label: str, photo_path: Path) -> Image.Image:
    bg = make_kraft_texture(WIDTH, HEIGHT).convert("RGBA")
    canvas = bg.copy()
    draw = ImageDraw.Draw(canvas)

    # Decorative top border line
    draw.line((60, 36, WIDTH - 60, 36), fill=(*GOLD, 180), width=2)

    # Plant name, centred in a fixed band so one- and two-line names
    # leave the photo in the same place
    name_font = load_font(54)
    name_band_top, name_band_height = 66, 148
    name_height = len(label.split("\n")) * (name_font.size + 8)
    name_y = name_band_top + (name_band_height - name_height) // 2
    draw_centered_multiline(draw, label, name_y, name_font, FOREST, WIDTH)

    # Divider flourish under the name
    mid_y = 234
    draw.line((WIDTH // 2 - 120, mid_y, WIDTH // 2 + 120, mid_y), fill=(*GOLD, 200), width=2)
    draw.ellipse((WIDTH // 2 - 5, mid_y - 5, WIDTH // 2 + 5, mid_y + 5), fill=FOREST)

    # Plant photo
    photo = Image.open(photo_path)
    photo_box = (90, 268, WIDTH - 90, 898)
    add_rounded_photo(canvas, photo, photo_box, radius=28)

    # Logo below the photo
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo_w = 470
    logo_h = int(logo.height * (logo_w / logo.width))
    logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
    canvas.alpha_composite(logo, ((WIDTH - logo_w) // 2, 940))

    # Footer tagline
    tag_font = load_font(22, bold=False)
    tag = "100% Organic · Grow Naturally"
    bbox = draw.textbbox((0, 0), tag, font=tag_font)
    tw = bbox[2] - bbox[0]
    draw.text(((WIDTH - tw) // 2, 1112), tag, font=tag_font, fill=(*KRAFT_DARK,))

    # Outer border
    draw.rounded_rectangle((24, 24, WIDTH - 24, HEIGHT - 24), radius=12, outline=(*GOLD, 160), width=3)

    return canvas.convert("RGB")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    missing = []
    for slug, label in PACKETS:
        photo = PLANT_PHOTOS_DIR / f"{slug}.png"
        if not photo.exists():
            missing.append(slug)
            continue
        packet = create_seed_pocket(slug, label, photo)
        out = OUTPUT_DIR / f"seed-pocket-{slug}.png"
        packet.save(out, "PNG", optimize=True)
        print(f"Created {out}")

    if missing:
        raise SystemExit(f"Missing plant photos: {', '.join(missing)}")


if __name__ == "__main__":
    main()
