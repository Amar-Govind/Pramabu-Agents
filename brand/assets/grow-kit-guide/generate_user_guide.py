#!/usr/bin/env python3
"""Generate Parambu Organics grow kit user guide poster."""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
LOGO_PATH = ROOT.parents[2] / "storefront" / "public" / "brand" / "logo-wordmark-transparent.png"
STEPS_DIR = ROOT / "steps"
OUTPUT_DIR = ROOT / "output"

CREAM = (247, 241, 228)
KRAFT_DARK = (196, 164, 124)
FOREST = (27, 67, 50)
GOLD = (214, 170, 132)
WHITE = (255, 255, 255)
TEXT_MUTED = (90, 110, 95)

# A landscape, three-panel accordion guide. Each panel is designed to be
# readable on its own when the sheet is folded along the two dotted seams.
WIDTH = 3000
HEIGHT = 2100
MARGIN = 84
PANEL_W = WIDTH // 3

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


def prepare_photo(image_path: Path, size: tuple[int, int], *, contain: bool = False) -> Image.Image:
    """Fit a photo into size. Use contain for packaging shots so nothing is cropped."""
    src = Image.open(image_path).convert("RGBA")
    w, h = size
    if contain:
        canvas = Image.new("RGBA", size, (*CREAM, 255))
        fitted = ImageOps.contain(src, (w - 12, h - 12), Image.Resampling.LANCZOS)
        canvas.alpha_composite(fitted, ((w - fitted.width) // 2, (h - fitted.height) // 2))
        photo = canvas
    else:
        photo = ImageOps.fit(src, size, Image.Resampling.LANCZOS)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w, h), radius=10, fill=255)
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


def draw_fold_line(draw: ImageDraw.ImageDraw, x: int) -> None:
    """Draw a deliberately visible, but print-friendly, accordion fold guide."""
    draw.line((x, 48, x, HEIGHT - 48), fill=(*GOLD, 155), width=3)
    for y in range(70, HEIGHT - 70, 28):
        draw.line((x - 12, y, x + 12, y), fill=(*GOLD, 220), width=3)
    tab_font = load_sans(17, bold=True)
    label = "FOLD HERE"
    draw.rounded_rectangle((x - 62, 16, x + 62, 48), radius=12, fill=(*CREAM, 235), outline=(*GOLD, 190), width=2)
    draw.text((x - text_width(draw, label, tab_font) // 2, 21), label, font=tab_font, fill=TEXT_MUTED)


def draw_panel_label(draw: ImageDraw.ImageDraw, panel: int, label: str) -> None:
    x = panel * PANEL_W + MARGIN
    font = load_sans(21, bold=True)
    draw.rounded_rectangle((x, 76, x + 180, 116), radius=20, fill=FOREST)
    draw.text((x + 20, 84), label.upper(), font=font, fill=WHITE)


def draw_fold_step(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    step_num: int,
    step: tuple[str | tuple[str, ...], str, str],
    *,
    photo_ratio: float = 0.54,
) -> None:
    """A compact step card that creates a visual path down each fold panel."""
    x1, y1, x2, y2 = box
    w, h = x2 - x1, y2 - y1
    photo_name, title, description = step
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle((2, 2, w - 3, h - 3), radius=26, fill=(*WHITE, 240), outline=(*GOLD, 180), width=3)

    photo_h = int(h * photo_ratio)
    photo = prepare_photo(resolve_photo(photo_name), (w - 32, photo_h), contain=step_num == 1)
    card.alpha_composite(photo, (16, 16))

    badge_y = 16 + photo_h
    draw_step_badge(draw, 44, badge_y + 30, step_num)
    title_font = load_font(30, bold=True)
    draw.text((86, badge_y + 8), title, font=title_font, fill=FOREST)

    desc_font = load_sans(19)
    y = badge_y + 55
    for line in wrap_text(draw, description, desc_font, w - 42):
        draw.text((22, y), line, font=desc_font, fill=TEXT_MUTED)
        y += 25
    canvas.alpha_composite(card, (x1, y1))


def draw_feature_strip(canvas: Image.Image, panel: int, y: int) -> None:
    draw = ImageDraw.Draw(canvas)
    panel_x = panel * PANEL_W
    spacing = (PANEL_W - 2 * MARGIN) // 2
    label_font = load_sans(16, bold=True)
    for i, (label, icon_key) in enumerate(FEATURES):
        col, row = i % 2, i // 2
        cx = panel_x + MARGIN + spacing // 2 + col * spacing
        cy = y + row * 128
        draw.ellipse((cx - 36, cy - 36, cx + 36, cy + 36), fill=(*WHITE, 180), outline=(*GOLD, 210), width=2)
        ICON_DRAWERS[icon_key](draw, cx, cy, size=18)
        lines = label.split("\n")
        text_y = cy + 46
        for line in lines:
            tw = text_width(draw, line, label_font)
            draw.text((cx - tw // 2, text_y), line, font=label_font, fill=FOREST)
            text_y += 19


def create_user_guide() -> Image.Image:
    canvas = make_background(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(canvas)

    # Alternating panel tints make the three folds feel intentional, while the
    # central planting panel remains the visual anchor.
    for panel, color in enumerate(((*WHITE, 80), (*FOREST, 16), (*WHITE, 80))):
        x = panel * PANEL_W + 20
        draw.rounded_rectangle((x, 34, x + PANEL_W - 40, HEIGHT - 34), radius=38, fill=color)

    draw_fold_line(draw, PANEL_W)
    draw_fold_line(draw, PANEL_W * 2)

    # Left panel: unbox and prepare.
    draw_panel_label(draw, 0, "Start")
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo_w = 470
    logo_h = int(logo.height * (logo_w / logo.width))
    logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
    canvas.alpha_composite(logo, ((PANEL_W - logo_w) // 2, 164))
    draw_centered(draw, "Your tiny garden", 330, load_font(50, bold=True), FOREST, PANEL_W)
    draw_centered(draw, "starts right here.", 390, load_font(34, italic=True), TEXT_MUTED, PANEL_W)
    draw_fold_step(canvas, (MARGIN, 510, PANEL_W - MARGIN, 1060), 1, STEPS[0])
    draw_fold_step(canvas, (MARGIN, 1100, PANEL_W - MARGIN, 1650), 2, STEPS[1])
    draw_centered(draw, "OPEN  •  HYDRATE  •  BEGIN", 1810, load_sans(18, bold=True), FOREST, PANEL_W)

    # Centre panel: the fold-out garden path.
    draw_panel_label(draw, 1, "Plant")
    centre_x = PANEL_W
    centre_title = "Follow the green path"
    centre_title_font = load_font(48, bold=True)
    draw.text((centre_x + (PANEL_W - text_width(draw, centre_title, centre_title_font)) // 2, 150), centre_title, font=centre_title_font, fill=WHITE)
    for i, (y1, y2) in enumerate(((290, 820), (870, 1400), (1450, 1980)), start=3):
        draw_fold_step(canvas, (centre_x + MARGIN, y1, centre_x + PANEL_W - MARGIN, y2), i, STEPS[i - 1])

    # Right panel: the harvest-facing finish and sustainable material message.
    draw_panel_label(draw, 2, "Grow")
    right_x = PANEL_W * 2
    title = "Grow Fresh Food"
    title_font = load_font(52, bold=True)
    draw.text((right_x + (PANEL_W - text_width(draw, title, title_font)) // 2, 154), title, font=title_font, fill=FOREST)
    subtitle = "in Just 7 Easy Steps"
    subtitle_font = load_font(31, italic=True)
    draw.text((right_x + (PANEL_W - text_width(draw, subtitle, subtitle_font)) // 2, 222), subtitle, font=subtitle_font, fill=TEXT_MUTED)
    draw_fold_step(canvas, (right_x + MARGIN, 330, right_x + PANEL_W - MARGIN, 910), 6, STEPS[5])
    draw_fold_step(canvas, (right_x + MARGIN, 950, right_x + PANEL_W - MARGIN, 1530), 7, STEPS[6])
    draw_feature_strip(canvas, 2, 1640)
    slogan = "Grow Naturally. Grow Sustainably."
    slogan_font = load_font(25, bold=True)
    draw.text((right_x + (PANEL_W - text_width(draw, slogan, slogan_font)) // 2, 1980), slogan, font=slogan_font, fill=FOREST)

    return canvas.convert("RGB")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    refresh_step_one_photo()
    guide = create_user_guide()
    out = OUTPUT_DIR / "grow-kit-user-guide.png"
    guide.save(out, "PNG", optimize=True, dpi=(300, 300))
    print(f"Created {out} ({guide.width}x{guide.height})")


if __name__ == "__main__":
    main()
