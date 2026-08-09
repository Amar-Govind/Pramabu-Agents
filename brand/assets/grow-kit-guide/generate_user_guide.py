#!/usr/bin/env python3
"""Generate Parambu Organics foldable grow-kit user guide.

Produces an orihon-style concertina (accordion) leaflet designed to tuck into
the cylindrical kit canister. Same step content as the poster, laid out as a
five-panel garden-path fold:

  Cover | Steps 1–2 | Steps 3–4 | Steps 5–6 | Step 7 + values

Outputs:
  - grow-kit-user-guide.png         flat print-ready accordion
  - grow-kit-user-guide-folded.png  closed cover mockup with fold edges
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
LOGO_PATH = ROOT.parents[2] / "storefront" / "public" / "brand" / "logo-wordmark-transparent.png"
STEPS_DIR = ROOT / "steps"
OUTPUT_DIR = ROOT / "output"

# Brand bible palette
CREAM = (247, 241, 228)
KRAFT = (214, 186, 148)
KRAFT_DARK = (196, 164, 124)
FOREST = (27, 67, 50)
FOREST_DEEP = (18, 48, 36)
GOLD = (214, 170, 132)
WHITE = (255, 255, 255)
TEXT_MUTED = (78, 96, 82)
SOIL = (120, 88, 58)
VINE = (52, 98, 68)

# Concertina geometry — five tall panels, landscape strip when open
PANEL_W = 720
PANEL_H = 1880
PANEL_COUNT = 5
GUTTER = 0  # panels abut; fold marks drawn on the seams
WIDTH = PANEL_W * PANEL_COUNT
HEIGHT = PANEL_H
MARGIN = 36

# Step 1 kit shot source (packaging hero)
KIT_POSTER = "Kit-Poster3.jpeg"
KIT_POSTER_CROP = (30, 408, 1052, 978)
KIT_POSTER_TEXT_BOX = (352, 412, 698, 516)
STEP_ONE_PHOTO = "step-01-open-kit.png"

STEPS = [
    (
        (STEP_ONE_PHOTO,),
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
    (
        "step-07-transplant-grow-bag.png",
        "Move to a Grow Bag",
        "Slit the cup sides with a knife and place it straight into a bigger grow bag. The cup breaks down on its own.",
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


def erase_poster_subtitle(poster: Image.Image) -> None:
    """Paint out the poster subtitle by interpolating the background above and below it."""
    x0, y0, x1, y1 = KIT_POSTER_TEXT_BOX
    top, bottom = y0 - 6, y1 + 6
    px = poster.load()
    rng = random.Random(5)
    for x in range(x0, x1):
        above, below = px[x, top], px[x, bottom]
        for y in range(y0, y1):
            ratio = (y - top) / (bottom - top)
            grain = rng.randint(-2, 2)
            px[x, y] = tuple(
                max(0, min(255, int(above[i] * (1 - ratio) + below[i] * ratio) + grain))
                for i in range(3)
            )
    feathered = poster.crop((x0 - 8, y0 - 8, x1 + 8, y1 + 8)).filter(ImageFilter.GaussianBlur(1.0))
    poster.paste(feathered, (x0 - 8, y0 - 8))


def refresh_step_one_photo() -> None:
    """Re-cut the step 1 kit shot from the poster so it stays the source of truth."""
    source = STEPS_DIR / KIT_POSTER
    if not source.exists():
        return
    poster = Image.open(source).convert("RGB")
    erase_poster_subtitle(poster)
    poster.crop(KIT_POSTER_CROP).save(STEPS_DIR / STEP_ONE_PHOTO, "PNG", optimize=True)


def resolve_photo(candidates: str | tuple[str, ...]) -> Path:
    """Return the first candidate present in steps/, matched case-insensitively."""
    if isinstance(candidates, str):
        candidates = (candidates,)
    available = {path.name.lower(): path for path in STEPS_DIR.iterdir() if path.is_file()}
    for name in candidates:
        match = available.get(name.lower())
        if match is not None:
            return match
    raise FileNotFoundError(f"No photo in {STEPS_DIR} matching any of: {', '.join(candidates)}")


def make_paper(width: int, height: int, *, seed: int = 7, tint: tuple[int, int, int] = CREAM) -> Image.Image:
    """Handmade paper texture with soft fiber and corner leaf shadows."""
    base = Image.new("RGB", (width, height), tint)
    pixels = base.load()
    rng = random.Random(seed)
    for y in range(height):
        for x in range(width):
            noise = rng.randint(-10, 10)
            fiber = int(6 * math.sin(x / 21) * math.cos(y / 29))
            r = min(255, max(0, tint[0] + noise + fiber))
            g = min(255, max(0, tint[1] + noise + fiber - 3))
            b = min(255, max(0, tint[2] + noise + fiber - 6))
            pixels[x, y] = (r, g, b)

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for _ in range(max(40, width * height // 45000)):
        x1, y1 = rng.randint(0, width), rng.randint(0, height)
        draw.line(
            (x1, y1, x1 + rng.randint(-60, 60), y1 + rng.randint(-3, 3)),
            fill=(*KRAFT_DARK, 14),
            width=1,
        )

    for cx, cy, r in [(0, 0, 320), (width, 0, 280), (0, height, 260), (width, height, 300)]:
        shade = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        ImageDraw.Draw(shade).ellipse((cx - r, cy - r, cx + r, cy + r), fill=(27, 67, 50, 16))
        shade = shade.filter(ImageFilter.GaussianBlur(50))
        overlay = Image.alpha_composite(overlay, shade)

    return Image.alpha_composite(base.convert("RGBA"), overlay)


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def text_height(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[3] - bbox[1]


def draw_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, ...],
    canvas_w: int,
    x0: int = 0,
) -> None:
    tw = text_width(draw, text, font)
    draw.text((x0 + (canvas_w - tw) // 2, y), text, font=font, fill=fill)


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if text_width(draw, candidate, font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_leaf_icon(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int = 28, fill=FOREST) -> None:
    s = size
    draw.polygon(
        [(cx, cy - s), (cx + s * 0.55, cy - s * 0.1), (cx, cy + s * 0.75), (cx - s * 0.55, cy - s * 0.1)],
        fill=fill,
    )
    draw.line((cx, cy - s * 0.85, cx, cy + s * 0.6), fill=fill, width=2)


def draw_home_icon(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int = 28) -> None:
    s = size
    draw.polygon(
        [
            (cx, cy - s),
            (cx + s, cy),
            (cx + s * 0.65, cy),
            (cx + s * 0.65, cy + s * 0.8),
            (cx - s * 0.65, cy + s * 0.8),
            (cx - s * 0.65, cy),
            (cx - s, cy),
        ],
        outline=FOREST,
        width=3,
    )
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


def arch_mask(size: tuple[int, int], radius: int = 28) -> Image.Image:
    """Soft greenhouse-arch photo window (rounded rect with taller top radius)."""
    w, h = size
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    # Arch: semicircle top + rectangle body
    arch_r = min(w // 2, h // 3)
    d.ellipse((0, 0, w - 1, arch_r * 2), fill=255)
    d.rectangle((0, arch_r, w - 1, h - 1), fill=255)
    # Soften lower corners slightly
    corner = Image.new("L", size, 255)
    cd = ImageDraw.Draw(corner)
    cd.rectangle((0, 0, w, h), fill=255)
    cd.pieslice((0, h - radius * 2, radius * 2, h), 90, 180, fill=0)
    cd.pieslice((w - radius * 2, h - radius * 2, w, h), 0, 90, fill=0)
    # Keep arch; only round bottom via multiply of lower region
    out = Image.composite(mask, Image.new("L", size, 0), mask)
    return out


def prepare_photo(
    image_path: Path,
    size: tuple[int, int],
    *,
    contain: bool = False,
    arched: bool = True,
) -> Image.Image:
    src = Image.open(image_path).convert("RGBA")
    w, h = size
    if contain:
        canvas = Image.new("RGBA", size, (*CREAM, 255))
        fitted = ImageOps.contain(src, (w - 16, h - 16), Image.Resampling.LANCZOS)
        canvas.alpha_composite(fitted, ((w - fitted.width) // 2, (h - fitted.height) // 2))
        photo = canvas
    else:
        photo = ImageOps.fit(src, size, Image.Resampling.LANCZOS)

    if arched:
        mask = arch_mask(size)
    else:
        mask = Image.new("L", size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius=18, fill=255)
    photo.putalpha(mask)
    return photo


def draw_fold_seam(draw: ImageDraw.ImageDraw, x: int, height: int) -> None:
    """Dashed fold mark with tiny leaf cut indicators at top and bottom."""
    for y in range(48, height - 48, 14):
        draw.line((x, y, x, y + 7), fill=(*KRAFT_DARK, 90), width=2)
    # Cut marks
    for cy in (28, height - 28):
        draw_leaf_icon(draw, x, cy, size=8, fill=(*GOLD, 220))
        draw.line((x - 10, cy, x + 10, cy), fill=(*GOLD, 160), width=1)


def draw_growth_path(
    overlay: Image.Image,
    points: list[tuple[int, int]],
) -> None:
    """Meandering vine that threads the concertina panels together."""
    if len(points) < 2:
        return
    draw = ImageDraw.Draw(overlay)

    def quad_points(p0: tuple[int, int], p1: tuple[int, int], p2: tuple[int, int], steps: int = 24) -> list[tuple[int, int]]:
        pts = []
        for i in range(steps + 1):
            t = i / steps
            x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t**2 * p2[0]
            y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t**2 * p2[1]
            pts.append((int(x), int(y)))
        return pts

    curve: list[tuple[int, int]] = [points[0]]
    for i in range(len(points) - 1):
        a, b = points[i], points[i + 1]
        ctrl = ((a[0] + b[0]) // 2, (a[1] + b[1]) // 2 + (40 if i % 2 else -40))
        curve.extend(quad_points(a, ctrl, b)[1:])

    # Soft under-glow
    if len(curve) > 1:
        draw.line(curve, fill=(52, 98, 68, 36), width=9)
        draw.line(curve, fill=(*VINE, 150), width=2)

    # Seed nodes + side leaves along the path
    for i, (x, y) in enumerate(curve):
        if i % 18 == 0:
            draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(*GOLD, 160))
        if i % 36 == 18:
            side = 1 if (i // 36) % 2 == 0 else -1
            draw_leaf_icon(draw, x + side * 14, y - 4, size=9, fill=(*VINE, 170))


def draw_step_badge(draw: ImageDraw.ImageDraw, cx: int, cy: int, number: int, r: int = 26) -> None:
    draw.ellipse((cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3), outline=(*GOLD, 210), width=2)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=FOREST)
    num_font = load_sans(24, bold=True)
    label = str(number)
    tw = text_width(draw, label, num_font)
    draw.text((cx - tw // 2, cy - 13), label, font=num_font, fill=WHITE)


def draw_panel_rail(draw: ImageDraw.ImageDraw, x0: int, label: str) -> None:
    """Top kraft ticket rail that reads like a foldable map legend."""
    draw.rectangle((x0, 0, x0 + PANEL_W, 54), fill=(*FOREST, 235))
    # Stitch perforations under the rail
    for x in range(x0 + 8, x0 + PANEL_W - 4, 10):
        draw.ellipse((x, 56, x + 3, 59), fill=(*GOLD, 140))
    font = load_sans(16, bold=True)
    tw = text_width(draw, label, font)
    draw.text((x0 + (PANEL_W - tw) // 2, 16), label, font=font, fill=GOLD)


def draw_step_block(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    step_num: int,
    title: str,
    image_path: Path,
    description: str,
    *,
    mirror: bool = False,
) -> tuple[int, int]:
    """Draw one step as an arched photo + caption. Returns vine anchor point."""
    x1, y1, x2, y2 = box
    w, h = x2 - x1, y2 - y1
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)

    # Subtle soil wash behind each step (not a heavy card)
    wash = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(wash).rounded_rectangle((0, 0, w - 1, h - 1), radius=22, fill=(255, 255, 255, 110))
    card.alpha_composite(wash)

    pad = 18
    photo_h = int(h * 0.58)
    photo_w = w - pad * 2
    contain = step_num == 1
    photo = prepare_photo(image_path, (photo_w, photo_h), contain=contain, arched=True)

    # Zigzag: photo shifts slightly left/right by panel rhythm
    shift = 8 if mirror else -8
    photo_x = pad + shift
    photo_y = 16
    # Gold arch ring
    ring = Image.new("RGBA", (photo_w + 10, photo_h + 10), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    arch_r = min(photo_w // 2, photo_h // 3)
    rd.arc((2, 2, photo_w + 6, arch_r * 2 + 4), 180, 0, fill=(*GOLD, 200), width=3)
    rd.line((2, arch_r + 2, 2, photo_h + 4), fill=(*GOLD, 160), width=2)
    rd.line((photo_w + 6, arch_r + 2, photo_w + 6, photo_h + 4), fill=(*GOLD, 160), width=2)
    card.alpha_composite(ring, (photo_x - 5, photo_y - 5))
    card.alpha_composite(photo, (photo_x, photo_y))

    badge_cx = photo_x + 34
    badge_cy = photo_y + 34
    draw_step_badge(draw, badge_cx, badge_cy, step_num)

    title_font = load_font(28, bold=True)
    desc_font = load_sans(17)
    text_top = photo_y + photo_h + 18
    draw.text((pad, text_top), title, font=title_font, fill=FOREST)

    lines = wrap_text(draw, description, desc_font, w - pad * 2)
    ty = text_top + 40
    for line in lines:
        draw.text((pad, ty), line, font=desc_font, fill=TEXT_MUTED)
        ty += 24

    canvas.alpha_composite(card, (x1, y1))
    # Vine anchor near the photo arch peak
    return (x1 + w // 2, y1 + photo_y + 8)


def draw_cover_panel(canvas: Image.Image, x0: int) -> tuple[int, int]:
    """Panel 1 — closed cover: brand-first, kit hero, unfold cue."""
    panel = Image.new("RGBA", (PANEL_W, PANEL_H), (0, 0, 0, 0))
    # Deep forest wash for cover drama
    paper = make_paper(PANEL_W, PANEL_H, seed=11, tint=(236, 228, 210))
    # Gradient forest band — stronger in the upper two-thirds, soft soil at base
    band = Image.new("RGBA", (PANEL_W, PANEL_H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    for y in range(PANEL_H):
        t = y / PANEL_H
        if t < 0.72:
            alpha = int(230 * (1 - t / 0.72) ** 1.15)
            bd.line((0, y, PANEL_W, y), fill=(*FOREST_DEEP, alpha))
        else:
            # Warm soil fade into the journey strip
            u = (t - 0.72) / 0.28
            bd.line((0, y, PANEL_W, y), fill=(SOIL[0], SOIL[1], SOIL[2], int(28 + 50 * u)))
    paper = Image.alpha_composite(paper, band)
    panel.alpha_composite(paper, (0, 0))
    draw = ImageDraw.Draw(panel)

    draw_panel_rail(draw, 0, "GROW KIT  ·  FOLDABLE GUIDE")

    # Logo
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo_w = 440
    logo_h = int(logo.height * (logo_w / logo.width))
    logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
    panel.alpha_composite(logo, ((PANEL_W - logo_w) // 2, 78))

    title_font = load_font(52, bold=True)
    script_font = load_font(30, italic=True)
    draw_centered(draw, "Grow Fresh Food", 250, title_font, CREAM, PANEL_W)
    draw_centered(draw, "in Just 7 Easy Steps", 318, script_font, GOLD, PANEL_W)

    # Decorative rule
    cx = PANEL_W // 2
    draw.line((80, 372, cx - 40, 372), fill=(*GOLD, 180), width=2)
    draw_leaf_icon(draw, cx, 372, size=12, fill=(*GOLD, 220))
    draw.line((cx + 40, 372, PANEL_W - 80, 372), fill=(*GOLD, 180), width=2)

    # Hero kit photo in arched window
    hero_path = resolve_photo((STEP_ONE_PHOTO,))
    hero_w, hero_h = PANEL_W - 88, 780
    hero = prepare_photo(hero_path, (hero_w, hero_h), contain=True, arched=True)
    hx, hy = 44, 400
    shadow = Image.new("RGBA", (hero_w + 30, hero_h + 30), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse((10, hero_h - 40, hero_w + 20, hero_h + 24), fill=(0, 0, 0, 50))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    panel.alpha_composite(shadow, (hx - 10, hy - 10))
    panel.alpha_composite(hero, (hx, hy))

    # Unfold cue along the right fold edge
    cue_font = load_sans(15, bold=True)
    for i, ch in enumerate("UNFOLD"):
        draw.text((PANEL_W - 34, 560 + i * 22), ch, font=cue_font, fill=(*GOLD, 230))
    for i, yy in enumerate(range(720, 860, 28)):
        draw.polygon(
            [(PANEL_W - 48, yy), (PANEL_W - 28, yy + 10), (PANEL_W - 48, yy + 20)],
            outline=(*GOLD, 200),
        )

    # Journey strip — seven seed dots previewing the path inside
    journey_y = hy + hero_h + 36
    journey_font = load_sans(14, bold=True)
    draw_centered(draw, "YOUR 7-STEP GROWING PATH", journey_y, journey_font, FOREST, PANEL_W)

    step_labels = ["Open", "Soak", "Fill", "Sow", "Mist", "Grow", "Move"]
    dot_font = load_sans(13, bold=True)
    label_font = load_sans(12)
    left, right = 56, PANEL_W - 56
    span = right - left
    dots_y = journey_y + 48
    for i in range(7):
        dx = left + int(span * i / 6)
        r = 16
        draw.ellipse((dx - r - 2, dots_y - r - 2, dx + r + 2, dots_y + r + 2), outline=(*GOLD, 200), width=2)
        draw.ellipse((dx - r, dots_y - r, dx + r, dots_y + r), fill=FOREST)
        num = str(i + 1)
        tw = text_width(draw, num, dot_font)
        draw.text((dx - tw // 2, dots_y - 8), num, font=dot_font, fill=WHITE)
        lw = text_width(draw, step_labels[i], label_font)
        draw.text((dx - lw // 2, dots_y + 26), step_labels[i], font=label_font, fill=TEXT_MUTED)
        if i < 6:
            nx = left + int(span * (i + 1) / 6)
            draw.line((dx + r + 4, dots_y, nx - r - 4, dots_y), fill=(*VINE, 160), width=2)

    # Footer tip on soil band
    tip_font = load_sans(17)
    tip2_font = load_font(22, italic=True)
    draw_centered(draw, "A pocket concertina for your kit canister", PANEL_H - 110, tip_font, FOREST, PANEL_W)
    draw_centered(draw, "Follow the vine →", PANEL_H - 72, tip2_font, (*SOIL, 220), PANEL_W)

    canvas.alpha_composite(panel, (x0, 0))
    return (x0 + PANEL_W - 40, hy + hero_h // 2)


def draw_pair_panel(
    canvas: Image.Image,
    x0: int,
    panel_index: int,
    step_a: int,
    step_b: int,
) -> list[tuple[int, int]]:
    """Interior panel holding two steps stacked along the path."""
    panel = Image.new("RGBA", (PANEL_W, PANEL_H), (0, 0, 0, 0))
    paper = make_paper(PANEL_W, PANEL_H, seed=20 + panel_index)
    panel.alpha_composite(paper, (0, 0))
    draw = ImageDraw.Draw(panel)

    labels = {
        1: "START HERE  ·  STEPS 1–2",
        2: "SOW & SETTLE  ·  STEPS 3–4",
        3: "TEND DAILY  ·  STEPS 5–6",
    }
    draw_panel_rail(draw, 0, labels[panel_index])

    # Large watermark step range
    mark_font = load_font(120, bold=True)
    mark = f"{step_a}–{step_b}"
    tw = text_width(draw, mark, mark_font)
    draw.text(((PANEL_W - tw) // 2, 90), mark, font=mark_font, fill=(*FOREST, 28))

    anchors: list[tuple[int, int]] = []
    blocks = [
        (72, 0.42, step_a, False),
        (PANEL_H // 2 + 10, 0.42, step_b, True),
    ]
    for top, frac, step_i, mirror in blocks:
        photo, title, description = STEPS[step_i - 1]
        box_h = int((PANEL_H - 100) * frac)
        ax, ay = draw_step_block(
            panel,
            (28, top, PANEL_W - 28, top + box_h),
            step_i,
            title,
            resolve_photo(photo),
            description,
            mirror=mirror,
        )
        anchors.append((x0 + ax, ay))

    # Small panel footer
    foot = load_sans(14, bold=True)
    draw_centered(draw, f"PANEL {panel_index + 1} OF {PANEL_COUNT}", PANEL_H - 42, foot, (*SOIL, 160), PANEL_W)

    canvas.alpha_composite(panel, (x0, 0))
    return anchors


def draw_finale_panel(canvas: Image.Image, x0: int) -> list[tuple[int, int]]:
    """Final panel — transplant step + brand values + slogan."""
    panel = Image.new("RGBA", (PANEL_W, PANEL_H), (0, 0, 0, 0))
    paper = make_paper(PANEL_W, PANEL_H, seed=44)
    panel.alpha_composite(paper, (0, 0))
    draw = ImageDraw.Draw(panel)

    draw_panel_rail(draw, 0, "TRANSPLANT  ·  STEP 7")

    photo, title, description = STEPS[6]
    photo_path = resolve_photo(photo)

    # Featured wide arched photo
    pw, ph = PANEL_W - 64, 520
    hero = prepare_photo(photo_path, (pw, ph), contain=False, arched=True)
    hx, hy = 32, 88
    panel.alpha_composite(hero, (hx, hy))
    draw_step_badge(draw, hx + 36, hy + 36, 7, r=28)

    title_font = load_font(34, bold=True)
    draw.text((40, hy + ph + 22), title, font=title_font, fill=FOREST)

    desc_font = load_sans(18)
    y = hy + ph + 70
    for line in wrap_text(draw, description, desc_font, PANEL_W - 80):
        draw.text((40, y), line, font=desc_font, fill=TEXT_MUTED)
        y += 26

    note_font = load_sans(17, bold=True)
    note = "No transplant shock  ·  Zero plastic waste"
    # Pill-free underline emphasis
    draw.text((40, y + 14), note, font=note_font, fill=FOREST)
    nw = text_width(draw, note, note_font)
    draw.line((40, y + 42, 40 + nw, y + 42), fill=(*GOLD, 200), width=2)

    # Slogan band
    band_y = y + 70
    draw.rectangle((0, band_y, PANEL_W, band_y + 70), fill=(*FOREST, 230))
    slogan_font = load_font(24, bold=True)
    draw_centered(draw, "Grow Naturally. Grow Sustainably.", band_y + 20, slogan_font, CREAM, PANEL_W)

    # Feature seals in 2×2
    seal_top = band_y + 100
    label_font = load_sans(13, bold=True)
    cols = 2
    cell_w = (PANEL_W - 80) // cols
    cell_h = 150
    for i, (label, icon_key) in enumerate(FEATURES):
        col, row = i % cols, i // cols
        cx = 40 + col * cell_w + cell_w // 2
        cy = seal_top + row * cell_h + 48
        draw.ellipse((cx - 40, cy - 40, cx + 40, cy + 40), outline=(*GOLD, 210), width=3)
        ICON_DRAWERS[icon_key](draw, cx, cy, size=22)
        ly = cy + 52
        for line in label.split("\n"):
            tw = text_width(draw, line, label_font)
            draw.text((cx - tw // 2, ly), line, font=label_font, fill=FOREST)
            ly += 16

    # Closing mark
    end_font = load_font(20, italic=True)
    draw_centered(draw, "parambu.in", PANEL_H - 56, end_font, (*SOIL, 180), PANEL_W)

    canvas.alpha_composite(panel, (x0, 0))
    return [(x0 + PANEL_W // 2, hy + 20)]


def create_foldable_guide() -> Image.Image:
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), (*CREAM, 255))
    # Base paper across the whole strip so seams feel continuous
    canvas.alpha_composite(make_paper(WIDTH, HEIGHT, seed=3), (0, 0))

    vine_points: list[tuple[int, int]] = []
    vine_points.append(draw_cover_panel(canvas, 0))
    for panel_i, (a, b) in enumerate([(1, 2), (3, 4), (5, 6)], start=1):
        vine_points.extend(draw_pair_panel(canvas, panel_i * PANEL_W, panel_i, a, b))
    vine_points.extend(draw_finale_panel(canvas, 4 * PANEL_W))

    # Vine path on top of panels (under fold marks)
    path_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw_growth_path(path_layer, vine_points)
    canvas = Image.alpha_composite(canvas, path_layer)

    # Fold seams
    seam_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    sd = ImageDraw.Draw(seam_layer)
    for i in range(1, PANEL_COUNT):
        draw_fold_seam(sd, i * PANEL_W, HEIGHT)
    canvas = Image.alpha_composite(canvas, seam_layer)

    # Outer trim rule
    border = ImageDraw.Draw(canvas)
    border.rectangle((2, 2, WIDTH - 3, HEIGHT - 3), outline=(*GOLD, 120), width=3)

    return canvas.convert("RGB")


def create_folded_mockup(flat: Image.Image) -> Image.Image:
    """Closed concertina mockup: cover facing out with stacked fold edges."""
    cover = flat.crop((0, 0, PANEL_W, PANEL_H))
    edge_w = 18
    stack = PANEL_COUNT - 1
    mock_w = PANEL_W + stack * edge_w + 80
    mock_h = PANEL_H + 80
    bg = make_paper(mock_w, mock_h, seed=99, tint=(232, 224, 208)).convert("RGB")

    # Drop shadow
    shadow = Image.new("RGBA", (PANEL_W + 40, PANEL_H + 40), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((0, 0, PANEL_W + 30, PANEL_H + 20), radius=8, fill=(0, 0, 0, 60))
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    bg = bg.convert("RGBA")
    ox, oy = 40, 30
    bg.alpha_composite(shadow, (ox + stack * edge_w - 8, oy + 18))

    # Fold edges peeking from behind (kraft stripes)
    for i in range(stack, 0, -1):
        edge = Image.new("RGBA", (edge_w + 4, PANEL_H), (0, 0, 0, 0))
        ed = ImageDraw.Draw(edge)
        tone = 196 - i * 8
        ed.rectangle((0, 0, edge_w, PANEL_H), fill=(tone, tone - 24, tone - 48, 255))
        # Paper fiber lines
        for y in range(0, PANEL_H, 12):
            ed.line((2, y, edge_w - 2, y + 4), fill=(80, 60, 40, 30), width=1)
        bg.alpha_composite(edge, (ox + i * edge_w, oy + i * 2))

    bg.alpha_composite(cover.convert("RGBA"), (ox, oy))

    # Caption
    draw = ImageDraw.Draw(bg)
    cap = load_sans(18, bold=True)
    label = "FOLDED  ·  TUCKS INTO KIT CANISTER"
    tw = text_width(draw, label, cap)
    draw.text(((mock_w - tw) // 2, mock_h - 36), label, font=cap, fill=FOREST)

    return bg.convert("RGB")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    refresh_step_one_photo()
    guide = create_foldable_guide()
    out = OUTPUT_DIR / "grow-kit-user-guide.png"
    guide.save(out, "PNG", optimize=True)
    print(f"Created {out} ({guide.width}x{guide.height})")

    folded = create_folded_mockup(guide)
    folded_out = OUTPUT_DIR / "grow-kit-user-guide-folded.png"
    folded.save(folded_out, "PNG", optimize=True)
    print(f"Created {folded_out} ({folded.width}x{folded.height})")


if __name__ == "__main__":
    main()
