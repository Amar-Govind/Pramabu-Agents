#!/usr/bin/env python3
"""Palette, typography, and grow kit copy shared by the guide generators.

`generate_user_guide.py` (single sheet poster) and `generate_foldable_guide.py`
(four panel concertina) both read colours, fonts, and step copy from here so the
two pieces never drift apart.
"""

from __future__ import annotations

import random
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
BRAND_DIR = ROOT.parents[2] / "storefront" / "public" / "brand"
LOGO_PATH = BRAND_DIR / "logo-wordmark-transparent.png"
STEPS_DIR = ROOT / "steps"
OUTPUT_DIR = ROOT / "output"

# Kraft paper palette from the Parambu brand bible
CREAM = (247, 241, 228)
KRAFT = (214, 186, 148)
KRAFT_DARK = (196, 164, 124)
FOREST = (27, 67, 50)
GOLD = (214, 170, 132)
WHITE = (255, 255, 255)
TEXT_MUTED = (90, 110, 95)

WEBSITE = "parambu.in"
TAGLINE = "Everyday Pure & Natural"
SLOGAN = "Grow Naturally. Grow Sustainably."
KIT_NAME = "Organic Farming Kit"
KIT_SUBTITLE = "Self Sufficient Farming"

# Step 1 reuses the kit hero shot from the reference poster, cropped around the
# canister so the packaging stays legible at card size. The poster's subtitle
# sits beside the canister, so it is painted out before cropping.
KIT_POSTER = "Kit-Poster3.jpeg"
# Whole product spread: canister, cups, cocopeat discs, seed packets, spray
# bottle and stirrers. The lower bound stops just above the poster's
# "What's Inside" banner.
KIT_POSTER_CROP = (30, 408, 1052, 978)
KIT_POSTER_TEXT_BOX = (352, 412, 698, 516)
STEP_ONE_PHOTO = "step-01-open-kit.png"

# Each step lists its photo candidates in priority order, so a real product
# photo dropped into steps/ is preferred over the generated placeholder.
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

STEP_SEVEN_NOTE = "No transplant shock · Zero plastic waste"

FEATURES = [
    ("100%\nORGANIC", "leaf"),
    ("PERFECT FOR\nHOME GARDENS", "home"),
    ("SAFE & NATURAL\nMATERIALS", "hands"),
    ("BETTER\nTOMORROW", "sprout"),
]

SERIF_BOLD_FILES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "/usr/share/fonts/truetype/croscore/Tinos-Bold.ttf",
)
SERIF_FILES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    "/usr/share/fonts/truetype/croscore/Tinos-Regular.ttf",
)
SERIF_ITALIC_FILES = (
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
    "/usr/share/fonts/truetype/croscore/Tinos-Italic.ttf",
)
SANS_BOLD_FILES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
)
SANS_FILES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
)


@lru_cache(maxsize=None)
def _first_available(paths: tuple[str, ...]) -> str:
    for path in paths:
        if Path(path).exists():
            return path
    raise FileNotFoundError(f"None of these fonts are installed: {', '.join(paths)}")


@lru_cache(maxsize=None)
def load_serif(size: int, bold: bool = True, italic: bool = False) -> ImageFont.FreeTypeFont:
    if italic:
        files = SERIF_ITALIC_FILES
    elif bold:
        files = SERIF_BOLD_FILES
    else:
        files = SERIF_FILES
    return ImageFont.truetype(_first_available(files), size)


@lru_cache(maxsize=None)
def load_sans(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(_first_available(SANS_BOLD_FILES if bold else SANS_FILES), size)


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
