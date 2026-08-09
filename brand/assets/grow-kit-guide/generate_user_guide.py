#!/usr/bin/env python3
"""Generate Parambu Organics grow kit foldable user guide."""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
LOGO_PATH = ROOT.parents[2] / "storefront" / "public" / "brand" / "logo-wordmark-transparent.png"
COVER_LOGO_PATH = ROOT.parents[2] / "storefront" / "public" / "brand" / "logo-wordmark.png"
STEPS_DIR = ROOT / "steps"
OUTPUT_DIR = ROOT / "output"

CREAM = (247, 241, 228)
KRAFT_DARK = (196, 164, 124)
FOREST = (27, 67, 50)
GOLD = (214, 170, 132)
WHITE = (255, 255, 255)
TEXT_MUTED = (90, 110, 95)

WIDTH = 1800
HEIGHT = 2560
MARGIN = 60

# Foldable accordion layout — 8 vertical panels (cover + 7 steps), z-fold.
FOLD_PANEL_W = 1080
FOLD_PANEL_H = 620
FOLD_PANEL_COUNT = 8
FOLD_PANEL_GAP = 44
FOLD_BLEED = 24
FOLD_VINE_X = 54
FOLD_INNER_PAD = 20
PHOTO_ZOOM = 0.86
PHOTO_PAD = 28

# Step 1 is rebuilt from the kit poster product band: erase the poster subtitle
# and green "What's Inside" banner, restore the branded pencil, then crop the
# full kit spread (cups, discs, seeds, spray, canister, sticks, pencil).
KIT_POSTER = "Kit-Poster3.jpeg"
# Crop through the pencil; extra sand margin is appended after wipe/restore.
KIT_POSTER_CROP = (4, 395, 1086, 1024)
KIT_POSTER_TEXT_BOX = (300, 405, 780, 520)
KIT_POSTER_BANNER_BOX = (260, 978, 1086, 1040)
KIT_POSTER_PENCIL_BOX = (470, 960, 1086, 1010)
KIT_POSTER_SAND_SAMPLE = (620, 940, 780, 970)
KIT_POSTER_BOTTOM_MARGIN = 48
KIT_POSTER_SIDE_MARGIN = 28
STEP_ONE_PHOTO = "step-01-open-kit.png"
STEP_ONE_PHOTO_ZOOM = 0.97
STEP_ONE_PHOTO_PAD = 8

# Cards per row; the final row holds the single transplanting step, centred.
ROW_LAYOUT = [3, 3, 1]

# Each step lists its photo candidates in priority order, so a real product
# photo dropped into steps/ is preferred over the generated placeholder.
STEPS = [
    (
        (STEP_ONE_PHOTO, KIT_POSTER),
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


def _sample_mean_color(image: Image.Image, box: tuple[int, int, int, int]) -> tuple[float, float, float]:
    patch = image.crop(box).convert("RGB")
    px = patch.load()
    total = [0.0, 0.0, 0.0]
    count = 0
    for y in range(patch.height):
        for x in range(patch.width):
            r, g, b = px[x, y]
            total[0] += r
            total[1] += g
            total[2] += b
            count += 1
    count = max(1, count)
    return total[0] / count, total[1] / count, total[2] / count


def _pencil_mask(size: tuple[int, int], origin: tuple[int, int]) -> Image.Image:
    """Opaque mask covering the branded pencil tip + barrel in poster coordinates."""
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    ox, oy = origin
    # Barrel (rounded capsule) and tip, mapped into the local patch.
    draw.rounded_rectangle((690 - ox, 968 - oy, 1084 - ox, 1008 - oy), radius=16, fill=255)
    # Sharpened tip tapering left.
    tip = [
        (470 - ox, 988 - oy),
        (700 - ox, 968 - oy),
        (700 - ox, 1008 - oy),
    ]
    draw.polygon(tip, fill=255)
    return mask.filter(ImageFilter.GaussianBlur(0.8))


def erase_poster_banner(poster: Image.Image) -> None:
    """Paint out the green What's Inside banner, then put the pencil back on top."""
    x0, y0, x1, y1 = KIT_POSTER_BANNER_BOX
    x1 = min(x1, poster.width)
    y1 = min(y1, poster.height)
    sand = _sample_mean_color(poster, KIT_POSTER_SAND_SAMPLE)
    source = poster.copy()
    src = source.load()
    px = poster.load()
    rng = random.Random(21)

    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - 1 - y0)
        edge = min(1.0, (y - y0) / 6.0)
        for x in range(x0, x1):
            base = src[x, max(0, y0 - 8)]
            filled = tuple(
                max(0, min(255, int(base[i] * (1 - 0.35 * t) + sand[i] * (0.35 * t) + rng.randint(-5, 5))))
                for i in range(3)
            )
            if edge < 1.0:
                px[x, y] = tuple(int(src[x, y][i] * (1 - edge) + filled[i] * edge) for i in range(3))
            else:
                px[x, y] = filled

    px0, py0, px1, py1 = KIT_POSTER_PENCIL_BOX
    px1 = min(px1, poster.width)
    py1 = min(py1, poster.height)
    patch = source.crop((px0, py0, px1, py1)).convert("RGBA")
    mask = _pencil_mask(patch.size, (px0, py0))
    # Keep green banner pixels out of the restored pencil patch.
    pp = patch.load()
    mp = mask.load()
    for y in range(patch.height):
        for x in range(patch.width):
            r, g, b, _a = pp[x, y]
            if g > r + 10 and g > b + 10 and r < 110:
                mp[x, y] = 0
    patch.putalpha(mask)
    composed = poster.convert("RGBA")
    composed.alpha_composite(patch, (px0, py0))
    poster.paste(composed.convert("RGB"))


def load_cover_logo(width: int) -> Image.Image:
    """Load the wordmark with black keyed out for a clean overlay on forest green."""
    logo = Image.open(COVER_LOGO_PATH).convert("RGBA")
    pixels = logo.load()
    for y in range(logo.height):
        for x in range(logo.width):
            r, g, b, a = pixels[x, y]
            if a < 120 or (r < 45 and g < 45 and b < 45):
                pixels[x, y] = (0, 0, 0, 0)
            else:
                pixels[x, y] = (r, g, b, 255)
    bbox = logo.split()[-1].getbbox()
    if bbox:
        logo = logo.crop(bbox)
    logo_h = int(logo.height * (width / logo.width))
    return logo.resize((width, logo_h), Image.Resampling.LANCZOS)


def _make_sand_margin(width: int, height: int, sand: tuple[float, float, float]) -> Image.Image:
    """Build a quiet sand strip so the pencil isn't flush with the frame edge."""
    margin = Image.new("RGB", (width, height), tuple(int(c) for c in sand))
    px = margin.load()
    rng = random.Random(33)
    for y in range(height):
        for x in range(width):
            grain = rng.randint(-6, 6)
            px[x, y] = tuple(max(0, min(255, int(sand[i]) + grain)) for i in range(3))
    return margin.filter(ImageFilter.GaussianBlur(0.4))


def refresh_step_one_photo() -> None:
    """Rebuild the step 1 photo from Kit-Poster3 so the kit spread stays current."""
    source = STEPS_DIR / KIT_POSTER
    if not source.exists():
        return
    poster = Image.open(source).convert("RGB")
    erase_poster_subtitle(poster)
    erase_poster_banner(poster)
    crop = poster.crop(KIT_POSTER_CROP)
    sand = _sample_mean_color(poster, KIT_POSTER_SAND_SAMPLE)
    bottom = _make_sand_margin(crop.width, KIT_POSTER_BOTTOM_MARGIN, sand)
    side = KIT_POSTER_SIDE_MARGIN
    framed = Image.new(
        "RGB",
        (crop.width + side * 2, crop.height + KIT_POSTER_BOTTOM_MARGIN),
        tuple(int(c) for c in sand),
    )
    # Quiet side margins so the pencil tip/end aren't flush with the frame.
    left = _make_sand_margin(side, framed.height, sand)
    right = _make_sand_margin(side, framed.height, sand)
    framed.paste(left, (0, 0))
    framed.paste(right, (framed.width - side, 0))
    framed.paste(crop, (side, 0))
    framed.paste(bottom, (side, crop.height))
    framed.save(STEPS_DIR / STEP_ONE_PHOTO, "PNG", optimize=True)


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


def prepare_photo(
    image_path: Path,
    size: tuple[int, int],
    *,
    contain: bool = False,
    zoom: float = 1.0,
    pad: int = 12,
    bg: tuple[int, int, int] = CREAM,
    corner_radius: int = 10,
) -> Image.Image:
    """Fit a photo into size. Use contain to letterbox; zoom scales down within the box."""
    src = Image.open(image_path).convert("RGBA")
    w, h = size
    fit_w = max(1, int(w * zoom) - pad * 2)
    fit_h = max(1, int(h * zoom) - pad * 2)
    if contain:
        canvas = Image.new("RGBA", size, (*bg, 255))
        fitted = ImageOps.contain(src, (fit_w, fit_h), Image.Resampling.LANCZOS)
        canvas.alpha_composite(fitted, ((w - fitted.width) // 2, (h - fitted.height) // 2))
        photo = canvas
    else:
        photo = ImageOps.fit(src, (fit_w, fit_h), Image.Resampling.LANCZOS)
        if fit_w < w or fit_h < h:
            canvas = Image.new("RGBA", size, (*bg, 255))
            canvas.alpha_composite(photo, ((w - photo.width) // 2, (h - photo.height) // 2))
            photo = canvas
    if corner_radius > 0:
        mask = Image.new("L", size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, w, h), radius=corner_radius, fill=255)
        photo.putalpha(mask)
    return photo


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

    # Photo area — step 1 uses the original kit packaging photo without cropping
    photo_top = 72
    photo_pad = 16
    photo_w = (x2 - x1) - photo_pad * 2
    photo_h = (y2 - y1) - photo_top - 110
    # The kit spread is wider than the card, so letterbox it rather than crop
    contain = step_num == 1
    photo = prepare_photo(image_path, (photo_w, photo_h), contain=contain)
    card.alpha_composite(photo, (photo_pad, photo_top))

    # Description
    desc_font = load_sans(18)
    lines = wrap_text(draw, description, desc_font, x2 - x1 - 32)

    desc_y = y2 - y1 - 88
    for line in lines:
        tw = text_width(draw, line, desc_font)
        draw.text(((x2 - x1 - tw) // 2, desc_y), line, font=desc_font, fill=TEXT_MUTED)
        desc_y += 24

    canvas.alpha_composite(card, (x1, y1))


def draw_wide_step_card(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    step_num: int,
    title: str,
    image_path: Path,
    description: str,
) -> None:
    """Final step rendered as a wide card with the photo beside the copy."""
    x1, y1, x2, y2 = box
    w, h = x2 - x1, y2 - y1
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)

    draw.rounded_rectangle((0, 0, w - 1, h - 1), radius=14, fill=(*WHITE, 240), outline=(*GOLD, 200), width=2)

    pad = 18
    photo_w = (w - pad * 3) // 2
    photo_h = h - pad * 2
    photo = ImageOps.fit(Image.open(image_path).convert("RGBA"), (photo_w, photo_h), Image.Resampling.LANCZOS)
    mask = Image.new("L", (photo_w, photo_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, photo_w, photo_h), radius=10, fill=255)
    photo.putalpha(mask)
    card.alpha_composite(photo, (pad, pad))

    text_x = pad * 2 + photo_w
    text_w = w - text_x - pad
    badge_cx = text_x + 30
    badge_cy = pad + 42
    draw_step_badge(draw, badge_cx, badge_cy, step_num)

    title_font = load_font(32, bold=True)
    draw.text((badge_cx + 44, badge_cy - 20), title, font=title_font, fill=FOREST)

    desc_font = load_sans(19)
    y = badge_cy + 62
    for line in wrap_text(draw, description, desc_font, text_w):
        draw.text((text_x, y), line, font=desc_font, fill=TEXT_MUTED)
        y += 30

    note_font = load_sans(17, bold=True)
    draw.text((text_x, y + 16), "No transplant shock · Zero plastic waste", font=note_font, fill=FOREST)

    canvas.alpha_composite(card, (x1, y1))


def draw_footer_flourish(draw: ImageDraw.ImageDraw, y: int, canvas_w: int) -> None:
    cx = canvas_w // 2
    draw.line((MARGIN + 80, y, cx - 120, y), fill=(*GOLD, 200), width=2)
    draw.line((cx + 120, y, canvas_w - MARGIN - 80, y), fill=(*GOLD, 200), width=2)
    draw_leaf_icon(draw, cx - 100, y, size=10)
    draw_leaf_icon(draw, cx + 100, y, size=10)


def draw_simple_flourish(draw: ImageDraw.ImageDraw, y: int, canvas_w: int, *, inset: int = 100) -> None:
    """Horizontal divider without centre leaf markers (avoids overlapping footer text)."""
    cx = canvas_w // 2
    draw.line((inset, y, cx - 90, y), fill=(*GOLD, 200), width=2)
    draw.line((cx + 90, y, canvas_w - inset, y), fill=(*GOLD, 200), width=2)


def draw_cover_border(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
    """Double-line botanical frame for the accordion cover panel."""
    outer, inner = 22, 40
    gold = (*GOLD, 210)
    soft = (*CREAM, 90)

    draw.rounded_rectangle((outer, outer, w - outer, h - outer), radius=24, outline=gold, width=2)
    draw.rounded_rectangle((inner, inner, w - inner, h - inner), radius=18, outline=soft, width=1)

    # Leaf accents at corners
    for cx, cy in (
        (inner + 14, inner + 14),
        (w - inner - 14, inner + 14),
        (inner + 14, h - inner - 14),
        (w - inner - 14, h - inner - 14),
    ):
        draw_leaf_icon(draw, cx, cy, size=11)

    # Gold diamonds at top and bottom centre
    for cy in (outer + 14, h - outer - 14):
        draw.polygon(
            [(w // 2, cy - 7), (w // 2 + 7, cy), (w // 2, cy + 7), (w // 2 - 7, cy)],
            fill=gold,
        )


def draw_vine_stem(
    draw: ImageDraw.ImageDraw,
    x: int,
    y_start: int,
    y_end: int,
    *,
    leaf_count: int = 4,
    leaf_size: int = 16,
) -> None:
    """Curved vine stem with alternating leaves along a vertical span."""
    points: list[tuple[int, int]] = []
    span = y_end - y_start
    for i in range(0, span + 1, 8):
        sway = int(10 * math.sin(i / 42))
        points.append((x + sway, y_start + i))
    if len(points) > 1:
        draw.line(points, fill=(*FOREST, 180), width=4, joint="curve")

    for i in range(leaf_count):
        t = (i + 1) / (leaf_count + 1)
        py = y_start + int(span * t)
        sway = int(10 * math.sin((py - y_start) / 42))
        side = 1 if i % 2 == 0 else -1
        draw_leaf_icon(draw, x + sway + side * 22, py, size=leaf_size)


def draw_fold_crease(
    draw: ImageDraw.ImageDraw,
    gap_top: int,
    gap_bottom: int,
    width: int,
) -> None:
    """Dashed accordion fold line drawn inside the inter-panel gap only."""
    y = (gap_top + gap_bottom) // 2
    margin = 70
    dash, gap = 14, 10
    x = margin
    while x < width - margin:
        draw.line((x, y, min(x + dash, width - margin), y), fill=(*GOLD, 170), width=2)
        x += dash + gap
    draw_leaf_icon(draw, margin - 18, y, size=9)
    draw_leaf_icon(draw, width - margin + 18, y, size=9)


def draw_crop_marks(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    """Light printer crop marks around the flat accordion sheet."""
    mark = 18
    inset = 10
    corners = [
        ((inset, inset), (inset + mark, inset), (inset, inset + mark)),
        ((width - inset, inset), (width - inset - mark, inset), (width - inset, inset + mark)),
        ((inset, height - inset), (inset + mark, height - inset), (inset, height - inset - mark)),
        ((width - inset, height - inset), (width - inset - mark, height - inset), (width - inset, height - inset - mark)),
    ]
    for a, b, c in corners:
        draw.line((a, b), fill=(*KRAFT_DARK, 120), width=1)
        draw.line((a, c), fill=(*KRAFT_DARK, 120), width=1)


def draw_cover_panel(panel: Image.Image) -> None:
    """Forest-green front cover shown when the accordion is folded shut."""
    w, h = panel.size
    draw = ImageDraw.Draw(panel)

    # Deep forest gradient wash
    for y in range(h):
        ratio = y / h
        shade = int(8 * math.sin(ratio * math.pi))
        row = Image.new("RGBA", (w, 1), (FOREST[0] - shade, FOREST[1] + shade // 2, FOREST[2] - shade // 3, 255))
        panel.paste(row, (0, y))

    draw_cover_border(draw, w, h)

    logo_w = 460
    logo = load_cover_logo(logo_w)
    panel.alpha_composite(logo, ((w - logo_w) // 2, 58))

    title_font = load_font(58, bold=True)
    script_font = load_font(34, italic=True)
    draw_centered(draw, "Grow Fresh Food", 250, title_font, CREAM, w)
    draw_centered(draw, "in Just 7 Easy Steps", 322, script_font, GOLD, w)

    # Unfold cue
    cue_y = h - 170
    draw.line((w // 2 - 90, cue_y, w // 2 + 90, cue_y), fill=(*GOLD, 180), width=2)
    cue_font = load_sans(20, bold=True)
    draw_centered(draw, "Unfold Your Garden Journey", cue_y + 16, cue_font, CREAM, w)

    # Down arrows
    arrow_font = load_sans(28, bold=True)
    draw_centered(draw, "▼  ▼  ▼", cue_y + 52, arrow_font, GOLD, w)

    draw_vine_stem(draw, FOLD_VINE_X, 120, h - 90, leaf_count=3, leaf_size=14)


def draw_accordion_step_panel(
    panel: Image.Image,
    step_num: int,
    title: str,
    image_path: Path,
    description: str,
    *,
    tint: tuple[int, int, int] = CREAM,
) -> None:
    """Single accordion panel for steps 1–6."""
    w, h = panel.size
    pad = FOLD_INNER_PAD

    base = Image.new("RGB", (w, h), tint)
    panel.paste(base, (0, 0))
    draw = ImageDraw.Draw(panel)

    # Vine rail
    draw.rounded_rectangle((pad, pad, 78, h - pad), radius=12, fill=(*WHITE, 230), outline=(*GOLD, 140), width=2)
    draw_vine_stem(draw, FOLD_VINE_X, pad + 24, h - pad - 24, leaf_count=2, leaf_size=10 + step_num)

    content_x = 92
    content_w = w - content_x - pad
    draw_step_badge(draw, FOLD_VINE_X, pad + 36, step_num)

    title_font = load_font(30, bold=True)
    title_y = pad + 18
    draw.text((content_x, title_y), title, font=title_font, fill=FOREST)

    desc_font = load_sans(17)
    lines = wrap_text(draw, description, desc_font, content_w)
    line_h = 23
    desc_block_h = len(lines) * line_h + pad
    desc_y = h - pad - desc_block_h + pad // 2

    title_bottom = title_y + title_font.size + 10
    photo_top = title_bottom
    photo_h = max(180, desc_y - photo_top - 12)
    photo_zoom = STEP_ONE_PHOTO_ZOOM if step_num == 1 else PHOTO_ZOOM
    photo_pad = STEP_ONE_PHOTO_PAD if step_num == 1 else PHOTO_PAD
    # Keep square corners on step 1 so the bottom-right pencil isn't clipped.
    corner_radius = 0 if step_num == 1 else 10
    photo = prepare_photo(
        image_path,
        (content_w, photo_h),
        contain=True,
        zoom=photo_zoom,
        pad=photo_pad,
        bg=tint,
        corner_radius=corner_radius,
    )
    panel.alpha_composite(photo, (content_x, photo_top))

    for i, line in enumerate(lines):
        draw.text((content_x, desc_y + i * line_h), line, font=desc_font, fill=TEXT_MUTED)

    tab_font = load_sans(13, bold=True)
    draw.text((w - pad - 36, pad + 2), f"0{step_num}", font=tab_font, fill=(*GOLD, 200))


def draw_finale_panel(
    panel: Image.Image,
    image_path: Path,
    title: str,
    description: str,
) -> None:
    """Final accordion panel: step 7, slogan, and feature icons."""
    w, h = panel.size
    pad = FOLD_INNER_PAD

    base = make_background(w, h)
    panel.paste(base, (0, 0))
    draw = ImageDraw.Draw(panel)

    draw_vine_stem(draw, FOLD_VINE_X, pad, h - pad, leaf_count=4, leaf_size=16)

    card_top = pad
    card_x = 84
    card_w = w - card_x - pad
    title_font = load_font(28, bold=True)
    desc_font = load_sans(16)
    note_font = load_sans(14, bold=True)

    body_top = card_top + 58
    photo_w = int(card_w * 0.42)
    photo_h = 200
    text_x = card_x + photo_w + 18
    text_w = card_x + card_w - text_x
    lines = wrap_text(draw, description, desc_font, text_w)
    note_h = note_font.size + 8
    text_block_h = len(lines) * 22 + note_h
    card_h = max(photo_h, text_block_h) + 66

    draw.rounded_rectangle((card_x, card_top, card_x + card_w, card_top + card_h), radius=14, fill=(*WHITE, 240), outline=(*GOLD, 180), width=2)

    draw_step_badge(draw, card_x + 30, card_top + 34, 7)
    draw.text((card_x + 78, card_top + 16), title, font=title_font, fill=FOREST)

    photo = prepare_photo(image_path, (photo_w, photo_h), contain=True, zoom=PHOTO_ZOOM, pad=16, bg=WHITE)
    panel.alpha_composite(photo, (card_x + 14, body_top))

    y = body_top + 4
    for line in lines:
        draw.text((text_x, y), line, font=desc_font, fill=TEXT_MUTED)
        y += 22
    draw.text((text_x, y + 6), "No transplant shock · Zero plastic waste", font=note_font, fill=FOREST)

    footer_y = card_top + card_h + 12
    slogan_font = load_font(22, bold=True)
    slogan_y = footer_y + 8
    draw_centered(draw, "Grow Naturally. Grow Sustainably.", slogan_y, slogan_font, FOREST, w)

    flourish_y = footer_y + 40
    draw_simple_flourish(draw, flourish_y, w, inset=pad + 60)

    icon_y = footer_y + 100
    icon_spacing = (w - 2 * pad) // 4
    label_font = load_sans(11, bold=True)
    for i, (label, icon_key) in enumerate(FEATURES):
        cx = pad + icon_spacing // 2 + i * icon_spacing
        draw.ellipse((cx - 30, icon_y - 30, cx + 30, icon_y + 30), outline=(*GOLD, 210), width=2)
        ICON_DRAWERS[icon_key](draw, cx, icon_y, size=14)
        ly = icon_y + 38
        for line in label.split("\n"):
            tw = text_width(draw, line, label_font)
            draw.text((cx - tw // 2, ly), line, font=label_font, fill=FOREST)
            ly += label_font.size + 1

    site_font = load_sans(15, bold=True)
    draw_centered(draw, "parambu.in", h - pad - 4, site_font, FOREST, w)

    tab_font = load_sans(13, bold=True)
    draw.text((w - pad - 36, pad + 2), "07", font=tab_font, fill=(*GOLD, 200))


def create_foldable_guide() -> Image.Image:
    """Flat print layout for an 8-panel vertical accordion fold."""
    bleed = FOLD_BLEED
    gap = FOLD_PANEL_GAP
    w = FOLD_PANEL_W + bleed * 2
    h = FOLD_PANEL_COUNT * FOLD_PANEL_H + bleed * 2 + (FOLD_PANEL_COUNT - 1) * gap

    canvas = Image.new("RGBA", (w, h), (*CREAM, 255))

    for i in range(FOLD_PANEL_COUNT):
        y = bleed + i * (FOLD_PANEL_H + gap)
        panel = Image.new("RGBA", (FOLD_PANEL_W, FOLD_PANEL_H), (0, 0, 0, 0))

        if i == 0:
            draw_cover_panel(panel)
        elif i == FOLD_PANEL_COUNT - 1:
            photo, title, description = STEPS[6]
            draw_finale_panel(panel, resolve_photo(photo), title, description)
        else:
            photo, title, description = STEPS[i - 1]
            tint = CREAM if i % 2 == 1 else WHITE
            draw_accordion_step_panel(
                panel,
                i,
                title,
                resolve_photo(photo),
                description,
                tint=tint,
            )

        canvas.alpha_composite(panel, (bleed, y))

        if i < FOLD_PANEL_COUNT - 1:
            gap_top = y + FOLD_PANEL_H
            gap_bottom = gap_top + gap
            draw_fold_crease(ImageDraw.Draw(canvas), gap_top, gap_bottom, w)

    draw = ImageDraw.Draw(canvas)
    draw_crop_marks(draw, w, h)

    # Print legend
    legend_font = load_sans(15)
    legend = "Print flat · Accordion-fold along dashed lines · Finished size ≈ 108 × 230 mm"
    tw = text_width(draw, legend, legend_font)
    draw.text(((w - tw) // 2, h - bleed + 4), legend, font=legend_font, fill=TEXT_MUTED)

    return canvas.convert("RGB")


def create_foldable_mockup(flat: Image.Image) -> Image.Image:
    """Preview of the folded accordion cover as it sits inside the kit."""
    cover_h = FOLD_PANEL_H
    cover = flat.crop((FOLD_BLEED, FOLD_BLEED, FOLD_BLEED + FOLD_PANEL_W, FOLD_BLEED + cover_h))

    mock_w, mock_h = 900, 1100
    mock = Image.new("RGBA", (mock_w, mock_h), (235, 228, 215, 255))

    # Soft tabletop shadow
    shadow = Image.new("RGBA", mock.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.ellipse((mock_w // 2 - 260, mock_h - 180, mock_w // 2 + 260, mock_h - 40), fill=(0, 0, 0, 35))
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    mock = Image.alpha_composite(mock, shadow)

    # Stack slivers peeking beneath the cover (accordion depth)
    for depth, offset in enumerate([18, 10, 4], start=1):
        sliver = Image.new("RGBA", (FOLD_PANEL_W, 14), (*CREAM, 255))
        sdraw = ImageDraw.Draw(sliver)
        sdraw.line((40, 0, FOLD_PANEL_W - 40, 0), fill=(*GOLD, 140), width=2)
        sx = (mock_w - FOLD_PANEL_W) // 2
        sy = (mock_h - cover_h) // 2 + offset
        mock.alpha_composite(sliver, (sx, sy))

    # Cover card with slight lift shadow
    card_shadow = Image.new("RGBA", (FOLD_PANEL_W + 40, cover_h + 40), (0, 0, 0, 0))
    ImageDraw.Draw(card_shadow).rounded_rectangle((12, 12, FOLD_PANEL_W + 28, cover_h + 28), radius=16, fill=(0, 0, 0, 55))
    card_shadow = card_shadow.filter(ImageFilter.GaussianBlur(16))
    cx = (mock_w - FOLD_PANEL_W) // 2
    cy = (mock_h - cover_h) // 2 - 10
    mock.alpha_composite(card_shadow, (cx - 12, cy - 6))
    mock.alpha_composite(cover.convert("RGBA"), (cx, cy))

    draw = ImageDraw.Draw(mock)
    label_font = load_sans(22, bold=True)
    draw_centered(draw, "Folded Accordion View", 48, label_font, FOREST, mock_w)
    sub_font = load_sans(16)
    draw_centered(draw, "Front cover · unfolds vertically inside the grow kit", 82, sub_font, TEXT_MUTED, mock_w)

    return mock.convert("RGB")


def create_user_guide() -> Image.Image:
    canvas = make_background(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(canvas)

    # Logo
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo_w = 620
    logo_h = int(logo.height * (logo_w / logo.width))
    logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
    canvas.alpha_composite(logo, ((WIDTH - logo_w) // 2, 62))

    # Headlines
    title_font = load_font(78, bold=True)
    script_font = load_font(46, italic=True)
    draw_centered(draw, "Grow Fresh Food", 300, title_font, FOREST, WIDTH)
    draw_centered(draw, "in Just 7 Easy Steps", 398, script_font, FOREST, WIDTH)

    # Step grid: rows of 3, 3, and a single wide finale card
    grid_top = 500
    col_gap = 24
    row_gap = 28
    card_w = (WIDTH - 2 * MARGIN - 2 * col_gap) // 3
    card_h = 560
    wide_card_h = 420

    step_index = 0
    y = grid_top
    for count in ROW_LAYOUT:
        if count == 1:
            photo, title, description = STEPS[step_index]
            wide_w = 2 * card_w + col_gap
            x1 = (WIDTH - wide_w) // 2
            draw_wide_step_card(
                canvas,
                (x1, y, x1 + wide_w, y + wide_card_h),
                step_index + 1,
                title,
                resolve_photo(photo),
                description,
            )
            step_index += 1
            y += wide_card_h + row_gap
            continue

        row_w = count * card_w + (count - 1) * col_gap
        x_start = (WIDTH - row_w) // 2
        for col in range(count):
            photo, title, description = STEPS[step_index]
            x1 = x_start + col * (card_w + col_gap)
            draw_step_card(
                canvas,
                (x1, y, x1 + card_w, y + card_h),
                step_index + 1,
                title,
                resolve_photo(photo),
                description,
            )
            step_index += 1
        y += card_h + row_gap

    # Footer slogan
    footer_y = y + 6
    draw_footer_flourish(draw, footer_y, WIDTH)
    slogan_font = load_font(34, bold=True)
    draw_centered(draw, "Grow Naturally. Grow Sustainably.", footer_y + 24, slogan_font, FOREST, WIDTH)
    draw_footer_flourish(draw, footer_y + 84, WIDTH)

    # Feature icons row
    icon_y = footer_y + 150
    icon_spacing = (WIDTH - 2 * MARGIN) // 4
    label_font = load_sans(19, bold=True)
    for i, (label, icon_key) in enumerate(FEATURES):
        cx = MARGIN + icon_spacing // 2 + i * icon_spacing
        draw.ellipse((cx - 58, icon_y - 58, cx + 58, icon_y + 58), outline=(*GOLD, 210), width=3)
        ICON_DRAWERS[icon_key](draw, cx, icon_y, size=28)
        y = icon_y + 78
        for line in label.split("\n"):
            tw = text_width(draw, line, label_font)
            draw.text((cx - tw // 2, y), line, font=label_font, fill=FOREST)
            y += label_font.size + 4

    return canvas.convert("RGB")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    refresh_step_one_photo()

    foldable = create_foldable_guide()
    flat_out = OUTPUT_DIR / "grow-kit-user-guide.png"
    foldable.save(flat_out, "PNG", optimize=True)
    print(f"Created {flat_out} ({foldable.width}x{foldable.height})")

    mockup = create_foldable_mockup(foldable)
    mock_out = OUTPUT_DIR / "grow-kit-user-guide-folded-preview.png"
    mockup.save(mock_out, "PNG", optimize=True)
    print(f"Created {mock_out} ({mockup.width}x{mockup.height})")


if __name__ == "__main__":
    main()
