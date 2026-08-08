#!/usr/bin/env python3
"""Generate Parambu Organics grow kit user guide poster."""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
LOGO_PATH = ROOT.parents[2] / "storefront" / "public" / "brand" / "logo-stacked-transparent.png"
STEPS_DIR = ROOT / "steps"
OUTPUT_DIR = ROOT / "output"

CREAM = (247, 241, 228)
KRAFT_DARK = (196, 164, 124)
FOREST = (27, 67, 50)
GOLD = (214, 170, 132)
WHITE = (255, 255, 255)
TEXT_MUTED = (90, 110, 95)

WIDTH = 1600
HEIGHT = 2400
MARGIN = 56

STEPS = [
    (
        "step-01-open-kit.png",
        "Open the Kit",
        "Unbox your organic farming kit and get everything ready.",
    ),
    (
        "step-02-add-water.png",
        "Add Water to Cocopeat",
        "Pour water over the cocopeat disc and let it expand.",
    ),
    (
        "step-03-fill-pots.png",
        "Fill the Pots",
        "Fill the biodegradable pots with the expanded cocopeat.",
    ),
    (
        "step-04-sow-seeds.png",
        "Sow the Seeds",
        "Pick your favorite seeds and sow them in the soil.",
    ),
    (
        "step-05-water-gently.png",
        "Water Gently",
        "Water lightly and place the pots in a sunny spot.",
    ),
    (
        "step-06-watch-grow.png",
        "Watch Them Grow",
        "Nurture daily and enjoy fresh, homegrown vegetables.",
    ),
]

FEATURES = [
    ("100%\nORGANIC", "leaf"),
    ("PERFECT FOR\nHOME GARDENS", "home"),
    ("SAFE & NATURAL\nMATERIALS", "hands"),
    ("BETTER\nTOMORROW", "sprout"),
]


def load_font(size: int, bold: bool = True, italic: bool = False) -> ImageFont.FreeTypeFont:
    if italic:
        path = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
    elif bold:
        path = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
    else:
        path = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
    return ImageFont.truetype(path, size)


def load_sans(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    )
    return ImageFont.truetype(path, size)


def make_background(width: int, height: int) -> Image.Image:
    base = Image.new("RGB", (width, height), CREAM)
    pixels = base.load()
    rng = random.Random(7)
    for y in range(height):
        for x in range(width):
            noise = rng.randint(-10, 10)
            fiber = int(6 * math.sin(x / 21) * math.cos(y / 29))
            r = min(255, max(0, CREAM[0] + noise + fiber))
            g = min(255, max(0, CREAM[1] + noise + fiber - 3))
            b = min(255, max(0, CREAM[2] + noise + fiber - 6))
            pixels[x, y] = (r, g, b)

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for _ in range(80):
        x1, y1 = rng.randint(0, width), rng.randint(0, height)
        draw.line((x1, y1, x1 + rng.randint(-60, 60), y1 + rng.randint(-3, 3)), fill=(*KRAFT_DARK, 14), width=1)

    # Soft leaf shadow accents in corners
    for cx, cy, r in [(0, 0, 420), (width, 0, 380), (0, height, 360), (width, height, 400)]:
        shade = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        ImageDraw.Draw(shade).ellipse((cx - r, cy - r, cx + r, cy + r), fill=(27, 67, 50, 18))
        shade = shade.filter(ImageFilter.GaussianBlur(60))
        overlay = Image.alpha_composite(overlay, shade)

    return Image.alpha_composite(base.convert("RGBA"), overlay)


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def draw_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, ...],
    canvas_w: int,
) -> None:
    tw = text_width(draw, text, font)
    draw.text(((canvas_w - tw) // 2, y), text, font=font, fill=fill)


def draw_multiline_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, ...],
    canvas_w: int,
    line_gap: int = 6,
) -> int:
    lines = text.split("\n")
    lh = font.size + line_gap
    for line in lines:
        tw = text_width(draw, line, font)
        draw.text(((canvas_w - tw) // 2, y), line, font=font, fill=fill)
        y += lh
    return y


def draw_step_badge(draw: ImageDraw.ImageDraw, cx: int, cy: int, number: int) -> None:
    r = 28
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=FOREST)
    num_font = load_sans(26, bold=True)
    label = str(number)
    tw = text_width(draw, label, num_font)
    draw.text((cx - tw // 2, cy - 14), label, font=num_font, fill=WHITE)


def draw_leaf_icon(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int = 28) -> None:
    s = size
    draw.polygon(
        [(cx, cy - s), (cx + s * 0.55, cy - s * 0.1), (cx, cy + s * 0.75), (cx - s * 0.55, cy - s * 0.1)],
        fill=FOREST,
    )
    draw.line((cx, cy - s * 0.85, cx, cy + s * 0.6), fill=FOREST, width=2)


def draw_home_icon(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int = 28) -> None:
    s = size
    draw.polygon([(cx, cy - s), (cx + s, cy), (cx + s * 0.65, cy), (cx + s * 0.65, cy + s * 0.8), (cx - s * 0.65, cy + s * 0.8), (cx - s * 0.65, cy), (cx - s, cy)], outline=FOREST, width=3)
    draw_leaf_icon(draw, cx, cy + s * 0.15, size=12)


def draw_hands_icon(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int = 28) -> None:
    s = size
    draw.arc((cx - s, cy - s * 0.2, cx, cy + s * 0.9), 30, 210, fill=FOREST, width=3)
    draw.arc((cx, cy - s * 0.2, cx + s, cy + s * 0.9), 330, 150, fill=FOREST, width=3)
    draw_leaf_icon(draw, cx, cy + s * 0.15, size=14)


def draw_sprout_icon(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int = 28) -> None:
    s = size
    draw.ellipse((cx - s * 0.75, cy - s * 0.75, cx + s * 0.75, cy + s * 0.75), outline=FOREST, width=2)
    draw.line((cx, cy + s * 0.35, cx, cy - s * 0.15), fill=FOREST, width=2)
    draw.polygon([(cx, cy - s * 0.55), (cx + s * 0.35, cy - s * 0.05), (cx, cy + s * 0.05)], fill=FOREST)
    draw.polygon([(cx, cy - s * 0.55), (cx - s * 0.35, cy - s * 0.05), (cx, cy + s * 0.05)], fill=FOREST)


ICON_DRAWERS = {
    "leaf": draw_leaf_icon,
    "home": draw_home_icon,
    "hands": draw_hands_icon,
    "sprout": draw_sprout_icon,
}


def draw_step_card(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    step_num: int,
    title: str,
    image_path: Path,
    description: str,
) -> None:
    x1, y1, x2, y2 = box
    card = Image.new("RGBA", (x2 - x1, y2 - y1), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)

    # Card background
    draw.rounded_rectangle((0, 0, x2 - x1 - 1, y2 - y1 - 1), radius=14, fill=(*WHITE, 235), outline=(*GOLD, 180), width=2)

    # Step badge
    draw_step_badge(draw, 42, 42, step_num)

    # Title
    title_font = load_font(30, bold=True)
    draw.text((82, 24), title, font=title_font, fill=FOREST)

    # Photo area
    photo_top = 72
    photo_pad = 16
    photo_box = (photo_pad, photo_top, x2 - x1 - photo_pad, y2 - y1 - 110)
    photo_w = photo_box[2] - photo_box[0]
    photo_h = photo_box[3] - photo_box[1]
    photo = ImageOps.fit(Image.open(image_path).convert("RGBA"), (photo_w, photo_h), Image.Resampling.LANCZOS)
    mask = Image.new("L", (photo_w, photo_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, photo_w, photo_h), radius=10, fill=255)
    photo.putalpha(mask)
    card.alpha_composite(photo, (photo_pad, photo_top))

    # Description
    desc_font = load_sans(18)
    words = description.split()
    lines: list[str] = []
    current = ""
    max_w = x2 - x1 - 32
    for word in words:
        test = f"{current} {word}".strip()
        if text_width(draw, test, desc_font) <= max_w:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    desc_y = y2 - y1 - 88
    for line in lines:
        tw = text_width(draw, line, desc_font)
        draw.text(((x2 - x1 - tw) // 2, desc_y), line, font=desc_font, fill=TEXT_MUTED)
        desc_y += 24

    canvas.alpha_composite(card, (x1, y1))


def draw_footer_flourish(draw: ImageDraw.ImageDraw, y: int, canvas_w: int) -> None:
    cx = canvas_w // 2
    draw.line((MARGIN + 80, y, cx - 120, y), fill=(*GOLD, 200), width=2)
    draw.line((cx + 120, y, canvas_w - MARGIN - 80, y), fill=(*GOLD, 200), width=2)
    draw_leaf_icon(draw, cx - 100, y, size=10)
    draw_leaf_icon(draw, cx + 100, y, size=10)


def create_user_guide() -> Image.Image:
    canvas = make_background(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(canvas)

    # Logo
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo_w = 220
    logo_h = int(logo.height * (logo_w / logo.width))
    logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
    canvas.alpha_composite(logo, ((WIDTH - logo_w) // 2, 48))

    # Headlines
    title_font = load_font(72, bold=True)
    script_font = load_font(42, italic=True)
    draw_centered(draw, "Grow Fresh Food", 300, title_font, FOREST, WIDTH)
    draw_centered(draw, "in Just 6 Easy Steps", 390, script_font, FOREST, WIDTH)

    # Step grid 2 columns x 3 rows
    grid_top = 470
    col_gap = 28
    row_gap = 28
    card_w = (WIDTH - 2 * MARGIN - col_gap) // 2
    card_h = 520

    for i, (filename, title, description) in enumerate(STEPS):
        col = i % 2
        row = i // 2
        x1 = MARGIN + col * (card_w + col_gap)
        y1 = grid_top + row * (card_h + row_gap)
        draw_step_card(canvas, (x1, y1, x1 + card_w, y1 + card_h), i + 1, title, STEPS_DIR / filename, description)

    # Footer slogan
    footer_y = grid_top + 3 * (card_h + row_gap) + 24
    draw_footer_flourish(draw, footer_y, WIDTH)
    slogan_font = load_font(34, bold=True)
    draw_centered(draw, "Grow Naturally. Grow Sustainably.", footer_y + 24, slogan_font, FOREST, WIDTH)
    draw_footer_flourish(draw, footer_y + 84, WIDTH)

    # Feature icons row
    icon_y = footer_y + 130
    icon_spacing = (WIDTH - 2 * MARGIN) // 4
    label_font = load_sans(13, bold=True)
    for i, (label, icon_key) in enumerate(FEATURES):
        cx = MARGIN + icon_spacing // 2 + i * icon_spacing
        draw.ellipse((cx - 52, icon_y - 52, cx + 52, icon_y + 52), outline=(*GOLD, 200), width=2)
        ICON_DRAWERS[icon_key](draw, cx, icon_y, size=22)
        y = icon_y + 68
        for line in label.split("\n"):
            tw = text_width(draw, line, label_font)
            draw.text((cx - tw // 2, y), line, font=label_font, fill=FOREST)
            y += label_font.size + 2

    return canvas.convert("RGB")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    guide = create_user_guide()
    out = OUTPUT_DIR / "grow-kit-user-guide.png"
    guide.save(out, "PNG", optimize=True)
    print(f"Created {out} ({guide.width}x{guide.height})")


if __name__ == "__main__":
    main()
