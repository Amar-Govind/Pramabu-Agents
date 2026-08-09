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

PANEL_WIDTH = 900
SIDE_WIDTH = PANEL_WIDTH * 4
SIDE_HEIGHT = 1400
MARGIN = 60

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


def draw_panel_frame(draw: ImageDraw.ImageDraw, panel_x: int, panel_index: int) -> None:
    """Give each accordion panel a distinct, connected chapter feel."""
    inset = 24
    tint = (255, 255, 255, 116) if panel_index % 2 == 0 else (232, 239, 222, 92)
    draw.rounded_rectangle(
        (panel_x + inset, inset, panel_x + PANEL_WIDTH - inset, SIDE_HEIGHT - inset),
        radius=34,
        fill=tint,
        outline=(*GOLD, 130),
        width=2,
    )


def draw_arch_photo(canvas: Image.Image, image_path: Path, x: int, y: int, *, contain: bool = False) -> None:
    """Place photography in a soft garden-arch window."""
    width, height = PANEL_WIDTH - 96, 650
    if contain:
        photo = prepare_photo(image_path, (width, height), contain=True)
    else:
        photo = ImageOps.fit(
            Image.open(image_path).convert("RGBA"),
            (width, height),
            Image.Resampling.LANCZOS,
        )
    mask = Image.new("L", (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((0, 76, width, height), radius=24, fill=255)
    mask_draw.ellipse((0, 0, width, 250), fill=255)
    photo.putalpha(mask)

    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        (x + 8, y + 10, x + width + 8, y + height + 10),
        radius=28,
        fill=(27, 67, 50, 28),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    canvas.alpha_composite(shadow)
    canvas.alpha_composite(photo, (x, y))


def draw_growing_vine(draw: ImageDraw.ImageDraw, phase: float = 0.0) -> None:
    """Run one continuous vine across all four panels."""
    points = []
    for x in range(0, SIDE_WIDTH + 1, 12):
        y = 1262 + int(24 * math.sin((x / 180) + phase))
        points.append((x, y))
    draw.line(points, fill=(*FOREST, 150), width=4)
    for x in range(120, SIDE_WIDTH, 210):
        y = 1262 + int(24 * math.sin((x / 180) + phase))
        direction = -1 if (x // 210) % 2 else 1
        draw.line((x, y, x + 18, y + direction * 34), fill=(*FOREST, 150), width=3)
        draw.ellipse(
            (x + 8, y + direction * 48 - 12, x + 48, y + direction * 48 + 12),
            fill=(*FOREST, 125),
        )


def draw_fold_guides(draw: ImageDraw.ImageDraw, reverse: bool = False) -> None:
    """Mark alternating mountain and valley folds without overpowering the art."""
    guide_font = load_sans(14, bold=True)
    for fold_index, x in enumerate(range(PANEL_WIDTH, SIDE_WIDTH, PANEL_WIDTH), start=1):
        for y in range(42, SIDE_HEIGHT - 42, 22):
            draw.line((x, y, x, y + 10), fill=(*GOLD, 145), width=2)
        is_mountain = (fold_index % 2 == 1) ^ reverse
        label = "MOUNTAIN FOLD" if is_mountain else "VALLEY FOLD"
        label_w = text_width(draw, label, guide_font) + 18
        draw.rounded_rectangle(
            (x - label_w // 2, SIDE_HEIGHT - 72, x + label_w // 2, SIDE_HEIGHT - 47),
            radius=8,
            fill=(*CREAM, 220),
        )
        draw.text(
            (x - label_w // 2 + 9, SIDE_HEIGHT - 68),
            label,
            font=guide_font,
            fill=(*FOREST, 165),
        )


def draw_cover_panel(canvas: Image.Image, panel_x: int) -> None:
    draw = ImageDraw.Draw(canvas)
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo_w = 660
    logo_h = int(logo.height * (logo_w / logo.width))
    logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
    canvas.alpha_composite(logo, (panel_x + (PANEL_WIDTH - logo_w) // 2, 100))

    title_font = load_font(66, bold=True)
    script_font = load_font(39, italic=True)
    title = "Grow Fresh Food"
    subtitle = "in Just 7 Easy Steps"
    draw.text(
        (panel_x + (PANEL_WIDTH - text_width(draw, title, title_font)) // 2, 365),
        title,
        font=title_font,
        fill=FOREST,
    )
    draw.text(
        (panel_x + (PANEL_WIDTH - text_width(draw, subtitle, script_font)) // 2, 458),
        subtitle,
        font=script_font,
        fill=FOREST,
    )

    draw_footer_flourish(draw, 548, PANEL_WIDTH)
    label_font = load_sans(17, bold=True)
    positions = [(250, 690), (650, 690), (250, 955), (650, 955)]
    for (label, icon_key), (local_x, icon_y) in zip(FEATURES, positions):
        cx = panel_x + local_x
        draw.ellipse((cx - 58, icon_y - 58, cx + 58, icon_y + 58), fill=(*WHITE, 160), outline=(*GOLD, 210), width=3)
        ICON_DRAWERS[icon_key](draw, cx, icon_y, size=28)
        label_y = icon_y + 76
        for line in label.split("\n"):
            tw = text_width(draw, line, label_font)
            draw.text((cx - tw // 2, label_y), line, font=label_font, fill=FOREST)
            label_y += 23

    slogan_font = load_font(27, bold=True)
    slogan = "Grow Naturally. Grow Sustainably."
    draw.text(
        (panel_x + (PANEL_WIDTH - text_width(draw, slogan, slogan_font)) // 2, 1168),
        slogan,
        font=slogan_font,
        fill=FOREST,
    )


def draw_step_panel(canvas: Image.Image, panel_x: int, step_index: int) -> None:
    draw = ImageDraw.Draw(canvas)
    photo, title, description = STEPS[step_index]
    step_num = step_index + 1

    draw_step_badge(draw, panel_x + 78, 92, step_num)
    eyebrow_font = load_sans(15, bold=True)
    draw.text((panel_x + 122, 68), f"GROWING GUIDE  /  STEP {step_num:02d}", font=eyebrow_font, fill=GOLD)

    title_font = load_font(43 if len(title) < 20 else 37, bold=True)
    title_lines = wrap_text(draw, title, title_font, PANEL_WIDTH - 96)
    title_y = 112
    for line in title_lines:
        draw.text((panel_x + 48, title_y), line, font=title_font, fill=FOREST)
        title_y += title_font.size + 3

    photo_y = 224 if len(title_lines) == 1 else 248
    draw_arch_photo(
        canvas,
        resolve_photo(photo),
        panel_x + 48,
        photo_y,
        contain=step_num == 1,
    )

    desc_font = load_sans(25)
    desc_lines = wrap_text(draw, description, desc_font, PANEL_WIDTH - 112)
    desc_y = 925
    for line in desc_lines:
        tw = text_width(draw, line, desc_font)
        draw.text((panel_x + (PANEL_WIDTH - tw) // 2, desc_y), line, font=desc_font, fill=TEXT_MUTED)
        desc_y += 37

    if step_num == 7:
        note_font = load_sans(20, bold=True)
        note = "No transplant shock · Zero plastic waste"
        draw.text(
            (panel_x + (PANEL_WIDTH - text_width(draw, note, note_font)) // 2, desc_y + 22),
            note,
            font=note_font,
            fill=FOREST,
        )


def create_guide_side(step_indices: list[int | None], *, reverse_folds: bool = False) -> Image.Image:
    canvas = make_background(SIDE_WIDTH, SIDE_HEIGHT)
    draw = ImageDraw.Draw(canvas)
    for panel_index in range(4):
        draw_panel_frame(draw, panel_index * PANEL_WIDTH, panel_index)
    draw_growing_vine(draw, phase=0.8 if reverse_folds else 0.0)

    for panel_index, step_index in enumerate(step_indices):
        panel_x = panel_index * PANEL_WIDTH
        if step_index is None:
            draw_cover_panel(canvas, panel_x)
        else:
            draw_step_panel(canvas, panel_x, step_index)

    draw_fold_guides(draw, reverse=reverse_folds)
    return canvas.convert("RGB")


def create_user_guide() -> tuple[Image.Image, Image.Image, Image.Image]:
    """Create two print sides plus one convenient review proof."""
    front = create_guide_side([None, 0, 1, 2])
    back = create_guide_side([3, 4, 5, 6], reverse_folds=True)

    separator = 130
    proof = Image.new("RGB", (SIDE_WIDTH, SIDE_HEIGHT * 2 + separator), CREAM)
    proof.paste(front, (0, 0))
    proof.paste(back, (0, SIDE_HEIGHT + separator))
    proof_draw = ImageDraw.Draw(proof)
    proof_font = load_sans(24, bold=True)
    front_label = "SIDE A  ·  COVER + STEPS 1–3"
    back_label = "SIDE B  ·  STEPS 4–7"
    proof_draw.text((60, SIDE_HEIGHT + 28), front_label, font=proof_font, fill=FOREST)
    proof_draw.text(
        (SIDE_WIDTH - 60 - text_width(proof_draw, back_label, proof_font), SIDE_HEIGHT + 28),
        back_label,
        font=proof_font,
        fill=FOREST,
    )
    proof_draw.line((60, SIDE_HEIGHT + 78, SIDE_WIDTH - 60, SIDE_HEIGHT + 78), fill=GOLD, width=2)
    return front, back, proof


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    refresh_step_one_photo()
    front, back, proof = create_user_guide()
    outputs = {
        "grow-kit-user-guide-front.png": front,
        "grow-kit-user-guide-back.png": back,
        "grow-kit-user-guide.png": proof,
    }
    for filename, image in outputs.items():
        out = OUTPUT_DIR / filename
        image.save(out, "PNG", optimize=True)
        print(f"Created {out} ({image.width}x{image.height})")


if __name__ == "__main__":
    main()
