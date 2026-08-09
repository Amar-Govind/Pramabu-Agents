#!/usr/bin/env python3
"""Generate the foldable "Unfold & Grow" concertina user guide.

The guide is a single strip of nine equal panels that accordion-folds down to
a pocket-size card: a forest cover, one panel per step (7), and a back cover.
A vine along the bottom of the strip grows one stage taller on every panel,
so the plant grows as the customer unfolds the guide.

Outputs (in output/):
  grow-kit-user-guide-foldable.png          full print strip with fold marks
  grow-kit-user-guide-foldable-preview.png  mockup of the folded concertina
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from generate_user_guide import (
    CREAM,
    FEATURES,
    FOREST,
    GOLD,
    ICON_DRAWERS,
    KRAFT_DARK,
    LOGO_PATH,
    STEPS,
    TEXT_MUTED,
    WHITE,
    load_font,
    load_sans,
    refresh_step_one_photo,
    resolve_photo,
    text_width,
    wrap_text,
)

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"

PANEL_W = 640
PANEL_H = 1600
NUM_PANELS = 9  # cover + 7 steps + back cover
STRIP_W = PANEL_W * NUM_PANELS

FOREST_DEEP = (20, 52, 39)
SAGE = (223, 231, 215)
SOIL = (110, 82, 58)

# Vine timeline geometry (shared across step panels)
VINE_TOP = PANEL_H - 330
GROUND_Y = PANEL_H - 150


# ---------------------------------------------------------------------------
# Background


def make_strip_background() -> Image.Image:
    """Paper texture for the whole strip, built at half size for speed."""
    w, h = STRIP_W // 2, PANEL_H // 2
    base = Image.new("RGB", (w, h), CREAM)
    px = base.load()
    rng = random.Random(11)
    for y in range(h):
        for x in range(w):
            noise = rng.randint(-9, 9)
            fiber = int(5 * math.sin(x / 23) * math.cos(y / 31))
            px[x, y] = (
                min(255, max(0, CREAM[0] + noise + fiber)),
                min(255, max(0, CREAM[1] + noise + fiber - 3)),
                min(255, max(0, CREAM[2] + noise + fiber - 6)),
            )
    base = base.resize((STRIP_W, PANEL_H), Image.Resampling.BILINEAR)

    overlay = Image.new("RGBA", (STRIP_W, PANEL_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for _ in range(260):
        x1, y1 = rng.randint(0, STRIP_W), rng.randint(0, PANEL_H)
        draw.line(
            (x1, y1, x1 + rng.randint(-60, 60), y1 + rng.randint(-3, 3)),
            fill=(*KRAFT_DARK, 12),
            width=1,
        )

    # Alternate a faint sage wash on every other step panel for fold rhythm.
    for i in range(1, NUM_PANELS - 1):
        if i % 2 == 0:
            draw.rectangle(
                (i * PANEL_W, 0, (i + 1) * PANEL_W - 1, PANEL_H),
                fill=(*SAGE, 70),
            )

    return Image.alpha_composite(base.convert("RGBA"), overlay)


# ---------------------------------------------------------------------------
# Small drawing helpers


def draw_centered_in_panel(
    draw: ImageDraw.ImageDraw,
    text: str,
    panel_x: int,
    y: int,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, ...],
) -> None:
    tw = text_width(draw, text, font)
    draw.text((panel_x + (PANEL_W - tw) // 2, y), text, font=font, fill=fill)


def draw_leaf_badge(draw: ImageDraw.ImageDraw, cx: int, cy: int, number: int) -> None:
    """Step number set inside a stylised leaf."""
    s = 46
    draw.polygon(
        [
            (cx, cy - s),
            (cx + s * 0.78, cy - s * 0.15),
            (cx, cy + s * 0.9),
            (cx - s * 0.78, cy - s * 0.15),
        ],
        fill=FOREST,
    )
    draw.line((cx, cy + s * 0.9, cx, cy + s * 1.25), fill=FOREST, width=4)
    font = load_sans(34, bold=True)
    label = str(number)
    tw = text_width(draw, label, font)
    draw.text((cx - tw // 2, cy - 20), label, font=font, fill=WHITE)


def arch_photo(image_path: Path, size: tuple[int, int], *, contain: bool = False) -> Image.Image:
    """Fit a photo into an arched greenhouse-window mask."""
    w, h = size
    src = Image.open(image_path).convert("RGBA")
    if contain:
        # Wide packaging shot: rest it on the arch sill and treat the dome
        # above as airy headroom with a small leaf motif.
        canvas = Image.new("RGBA", size, (*SAGE, 255))
        fitted = ImageOps.contain(src, (w - 24, h - 24), Image.Resampling.LANCZOS)
        canvas.alpha_composite(fitted, ((w - fitted.width) // 2, h - fitted.height - 20))
        deco = ImageDraw.Draw(canvas)
        leaf_cy = (h - fitted.height - 20) // 2
        deco.ellipse((w // 2 - 34, leaf_cy - 34, w // 2 + 34, leaf_cy + 34), outline=(*GOLD, 200), width=3)
        deco.polygon(
            [
                (w // 2, leaf_cy - 18),
                (w // 2 + 13, leaf_cy - 2),
                (w // 2, leaf_cy + 18),
                (w // 2 - 13, leaf_cy - 2),
            ],
            fill=FOREST,
        )
        photo = canvas
    else:
        photo = ImageOps.fit(src, size, Image.Resampling.LANCZOS)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, w - 1, h - 1),
        radius=w // 2 - 2,
        corners=(True, True, False, False),
        fill=255,
    )
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, h - 24, w - 1, h - 1), radius=10, corners=(False, False, True, True), fill=255
    )
    photo.putalpha(mask)
    return photo


def draw_arch_frame(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    w = x2 - x1
    draw.rounded_rectangle(
        (x1, y1, x2, y2),
        radius=w // 2 - 2,
        corners=(True, True, False, False),
        outline=(*GOLD, 230),
        width=4,
    )
    draw.rounded_rectangle(
        (x1, y2 - 24, x2, y2), radius=10, corners=(False, False, True, True),
        outline=(*GOLD, 230), width=4,
    )


def draw_vine_stage(draw: ImageDraw.ImageDraw, panel_x: int, stage: int) -> None:
    """One stage of the growing vine timeline; stage runs 0..6."""
    cx = panel_x + PANEL_W // 2

    # Soil mound
    draw.ellipse((cx - 70, GROUND_Y - 16, cx + 70, GROUND_Y + 22), fill=SOIL)
    draw.ellipse((cx - 70, GROUND_Y - 16, cx + 70, GROUND_Y + 22), outline=FOREST, width=2)

    if stage == 0:
        # A seed resting on the soil
        draw.ellipse((cx - 11, GROUND_Y - 12, cx + 11, GROUND_Y + 4), fill=FOREST)
        return

    stem_h = 28 + stage * 22
    top_y = GROUND_Y - 12 - stem_h
    draw.line((cx, GROUND_Y - 10, cx, top_y), fill=FOREST, width=5)

    # Leaves alternate sides as the plant matures
    for leaf in range(stage):
        ly = GROUND_Y - 26 - leaf * 20
        direction = 1 if leaf % 2 == 0 else -1
        size = 12 + leaf * 2
        draw.polygon(
            [
                (cx, ly),
                (cx + direction * size, ly - size * 0.55),
                (cx + direction * size * 1.5, ly - size * 0.1),
                (cx + direction * size * 0.6, ly + size * 0.35),
            ],
            fill=FOREST,
        )

    if stage >= 5:
        # A little fruit once the plant is mature
        draw.ellipse((cx + 10, top_y + 12, cx + 30, top_y + 32), fill=(178, 74, 54))
    if stage == 6:
        draw.ellipse((cx - 32, top_y + 26, cx - 14, top_y + 44), fill=(178, 74, 54))


def draw_timeline_base(draw: ImageDraw.ImageDraw) -> None:
    """Dotted ground line connecting the vine stages across the step panels."""
    y = GROUND_Y + 4
    x = PANEL_W + 26
    end = STRIP_W - PANEL_W - 26
    while x < end:
        draw.line((x, y, x + 12, y), fill=(*KRAFT_DARK, 170), width=3)
        x += 26


def draw_fold_marks(draw: ImageDraw.ImageDraw) -> None:
    """Dashed fold lines with alternating mountain/valley marks."""
    small = load_sans(15, bold=True)
    for i in range(1, NUM_PANELS):
        x = i * PANEL_W
        y = 26
        while y < PANEL_H - 26:
            draw.line((x, y, x, y + 14), fill=(*GOLD, 150), width=2)
            y += 30

        mountain = i % 2 == 1
        mark = [(x - 10, 20), (x + 10, 20), (x, 6)] if mountain else [(x - 10, 6), (x + 10, 6), (x, 20)]
        draw.polygon(mark, fill=FOREST)
        label = "fold" if mountain else "fold"
        tw = text_width(draw, label, small)
        draw.text((x - tw // 2, 26), label, font=small, fill=(*FOREST, 170))


def draw_flourish(draw: ImageDraw.ImageDraw, cx: int, y: int, half_w: int, color: tuple[int, ...]) -> None:
    draw.line((cx - half_w, y, cx - 24, y), fill=color, width=2)
    draw.line((cx + 24, y, cx + half_w, y), fill=color, width=2)
    draw.polygon([(cx, y - 9), (cx + 7, y), (cx, y + 9), (cx - 7, y)], fill=color)


# ---------------------------------------------------------------------------
# Panels


def draw_cover_panel(canvas: Image.Image) -> None:
    panel = Image.new("RGBA", (PANEL_W, PANEL_H), (*FOREST_DEEP, 255))
    draw = ImageDraw.Draw(panel)

    # Subtle radial glow behind the logo
    glow = Image.new("RGBA", (PANEL_W, PANEL_H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((PANEL_W // 2 - 260, 160, PANEL_W // 2 + 260, 680), fill=(214, 170, 132, 40))
    panel = Image.alpha_composite(panel, glow.filter(ImageFilter.GaussianBlur(80)))
    draw = ImageDraw.Draw(panel)

    # Double gold frame
    draw.rounded_rectangle((28, 28, PANEL_W - 28, PANEL_H - 28), radius=26, outline=(*GOLD, 235), width=3)
    draw.rounded_rectangle((44, 44, PANEL_W - 44, PANEL_H - 44), radius=18, outline=(*GOLD, 120), width=1)

    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo_w = 460
    logo_h = int(logo.height * (logo_w / logo.width))
    logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
    panel.alpha_composite(logo, ((PANEL_W - logo_w) // 2, 190))
    draw = ImageDraw.Draw(panel)

    title_font = load_font(64, bold=True)
    script_font = load_font(34, italic=True)
    y = 210 + logo_h + 110
    for line in ("Grow", "Fresh Food"):
        tw = text_width(draw, line, title_font)
        draw.text(((PANEL_W - tw) // 2, y), line, font=title_font, fill=(*CREAM, 255))
        y += 84
    tw = text_width(draw, "in Just 7 Easy Steps", script_font)
    draw.text(((PANEL_W - tw) // 2, y + 16), "in Just 7 Easy Steps", font=script_font, fill=(*GOLD, 255))

    draw_flourish(draw, PANEL_W // 2, y + 110, 170, (*GOLD, 220))

    # "Unfold & grow" ribbon
    ribbon_y = PANEL_H - 560
    draw.rounded_rectangle((90, ribbon_y, PANEL_W - 90, ribbon_y + 76), radius=38, fill=(*GOLD, 255))
    ribbon_font = load_sans(28, bold=True)
    label = "UNFOLD & GROW"
    tw = text_width(draw, label, ribbon_font)
    draw.text(((PANEL_W - tw) // 2, ribbon_y + 22), label, font=ribbon_font, fill=FOREST_DEEP)

    # Concertina zigzag glyph with an arrow, hinting how the guide opens
    zz_y = ribbon_y + 170
    zx = PANEL_W // 2 - 120
    points = []
    for k in range(7):
        points.append((zx + k * 40, zz_y + (0 if k % 2 == 0 else 44)))
    draw.line(points, fill=(*CREAM, 230), width=5, joint="curve")
    ax = points[-1]
    draw.polygon([(ax[0] + 34, ax[1]), (ax[0] + 6, ax[1] - 14), (ax[0] + 6, ax[1] + 14)], fill=(*CREAM, 230))

    hint_font = load_sans(20)
    hint = "a pocket guide that grows with you"
    tw = text_width(draw, hint, hint_font)
    draw.text(((PANEL_W - tw) // 2, zz_y + 110), hint, font=hint_font, fill=(*CREAM, 200))

    footer_font = load_sans(17, bold=True)
    footer = "9 PANELS · ACCORDION FOLD"
    tw = text_width(draw, footer, footer_font)
    draw.text(((PANEL_W - tw) // 2, PANEL_H - 108), footer, font=footer_font, fill=(*GOLD, 210))

    canvas.alpha_composite(panel, (0, 0))


def draw_step_panel(canvas: Image.Image, index: int) -> None:
    """index runs 0..6 over STEPS; the panel sits at position index + 1."""
    photo_candidates, title, description = STEPS[index]
    panel_x = (index + 1) * PANEL_W
    draw = ImageDraw.Draw(canvas)

    draw_leaf_badge(draw, panel_x + PANEL_W // 2, 118, index + 1)

    title_font = load_font(36, bold=True)
    ty = 220
    for line in wrap_text(draw, title, title_font, PANEL_W - 110):
        draw_centered_in_panel(draw, line, panel_x, ty, title_font, FOREST)
        ty += 48

    # Arched greenhouse-window photo
    frame_pad = 62
    frame_w = PANEL_W - frame_pad * 2
    frame_h = 690
    frame_top = 340
    photo = arch_photo(
        resolve_photo(photo_candidates),
        (frame_w, frame_h),
        contain=index == 0,
    )
    canvas.alpha_composite(photo, (panel_x + frame_pad, frame_top))
    draw_arch_frame(
        draw, (panel_x + frame_pad, frame_top, panel_x + PANEL_W - frame_pad, frame_top + frame_h)
    )

    desc_font = load_sans(21)
    dy = frame_top + frame_h + 46
    for line in wrap_text(draw, description, desc_font, PANEL_W - 120):
        draw_centered_in_panel(draw, line, panel_x, dy, desc_font, TEXT_MUTED)
        dy += 30

    if index == len(STEPS) - 1:
        note_font = load_sans(19, bold=True)
        for line in ("No transplant shock", "Zero plastic waste"):
            dy += 4
            draw_centered_in_panel(draw, line, panel_x, dy, note_font, FOREST)
            dy += 28

    draw_vine_stage(draw, panel_x, index)

    stage_font = load_sans(16)
    draw_centered_in_panel(
        draw, f"step {index + 1} of 7", panel_x, PANEL_H - 92, stage_font, (*KRAFT_DARK, 255)
    )


def draw_back_panel(canvas: Image.Image) -> None:
    panel_x = (NUM_PANELS - 1) * PANEL_W
    draw = ImageDraw.Draw(canvas)

    draw.rounded_rectangle(
        (panel_x + 30, 30, panel_x + PANEL_W - 30, PANEL_H - 30),
        radius=24,
        outline=(*GOLD, 200),
        width=3,
    )

    draw_flourish(draw, panel_x + PANEL_W // 2, 150, 170, (*GOLD, 220))

    slogan_font = load_font(38, bold=True)
    y = 210
    for line in ("Grow Naturally.", "Grow Sustainably."):
        draw_centered_in_panel(draw, line, panel_x, y, slogan_font, FOREST)
        y += 58

    # Feature medallions stacked down the panel
    y = 430
    label_font = load_sans(19, bold=True)
    for label, icon_key in FEATURES:
        cx = panel_x + PANEL_W // 2
        draw.ellipse((cx - 56, y - 56, cx + 56, y + 56), outline=(*GOLD, 210), width=3)
        ICON_DRAWERS[icon_key](draw, cx, y, size=26)
        ly = y + 72
        for line in label.split("\n"):
            tw = text_width(draw, line, label_font)
            draw.text((cx - tw // 2, ly), line, font=label_font, fill=FOREST)
            ly += label_font.size + 4
        y += 240

    footer_font = load_sans(18)
    draw_centered_in_panel(
        draw, "parambu organics · grow kit", panel_x, PANEL_H - 120, footer_font, (*KRAFT_DARK, 255)
    )
    draw_flourish(draw, panel_x + PANEL_W // 2, PANEL_H - 160, 150, (*GOLD, 200))


# ---------------------------------------------------------------------------
# Outputs


def create_strip() -> Image.Image:
    canvas = make_strip_background()

    draw_timeline_base(ImageDraw.Draw(canvas))
    draw_cover_panel(canvas)
    for index in range(len(STEPS)):
        draw_step_panel(canvas, index)
    draw_back_panel(canvas)
    draw_fold_marks(ImageDraw.Draw(canvas))

    return canvas.convert("RGB")


def create_folded_preview(strip: Image.Image) -> Image.Image:
    """Mock up the strip as a standing, partially opened concertina."""
    prev_w, prev_h = 1720, 980
    bg = Image.new("RGB", (prev_w, prev_h), (236, 229, 214))
    grad = Image.new("L", (1, prev_h))
    for y in range(prev_h):
        grad.putpixel((0, y), int(26 * (y / prev_h)))
    shade = Image.merge(
        "RGB",
        (
            grad.resize((prev_w, prev_h)),
            grad.resize((prev_w, prev_h)),
            grad.resize((prev_w, prev_h)),
        ),
    )
    bg = Image.composite(Image.new("RGB", (prev_w, prev_h), (210, 200, 182)), bg, shade.convert("L"))

    panel_h = 560
    panel_w = int(PANEL_W * (panel_h / PANEL_H))
    shear = 0.16
    step_x = int(panel_w * 0.86)
    total_w = step_x * (NUM_PANELS - 1) + panel_w
    x0 = (prev_w - total_w) // 2
    base_y = 170

    board = Image.new("RGBA", (prev_w, prev_h), (0, 0, 0, 0))

    # Floor shadow
    shadow = Image.new("RGBA", (prev_w, prev_h), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse(
        (x0 - 40, base_y + panel_h - 30, x0 + total_w + 40, base_y + panel_h + 60),
        fill=(60, 50, 40, 90),
    )
    board = Image.alpha_composite(board, shadow.filter(ImageFilter.GaussianBlur(24)))

    extra = int(panel_w * abs(shear)) + 2
    for i in range(NUM_PANELS):
        panel = strip.crop((i * PANEL_W, 0, (i + 1) * PANEL_W, PANEL_H)).resize(
            (panel_w, panel_h), Image.Resampling.LANCZOS
        )
        toward = i % 2 == 0
        if not toward:
            panel = ImageEnhance.Brightness(panel).enhance(0.78)
        s = shear if toward else -shear
        sheared = panel.convert("RGBA").transform(
            (panel_w, panel_h + extra),
            Image.AFFINE,
            # dest (x, y) -> src (x, y - s * x + offset)
            (1, 0, 0, -s, 1, -(extra if s > 0 else 0)),
            resample=Image.Resampling.BILINEAR,
        )
        board.alpha_composite(sheared, (x0 + i * step_x, base_y - (extra if s > 0 else extra) // 2))

    bg = Image.alpha_composite(bg.convert("RGBA"), board)
    draw = ImageDraw.Draw(bg)
    caption_font = load_sans(26, bold=True)
    caption = "Unfold & Grow — accordion-fold pocket guide (9 panels, single-side print)"
    tw = text_width(draw, caption, caption_font)
    draw.text(((prev_w - tw) // 2, prev_h - 90), caption, font=caption_font, fill=FOREST)
    return bg.convert("RGB")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    refresh_step_one_photo()
    strip = create_strip()
    strip_out = OUTPUT_DIR / "grow-kit-user-guide-foldable.png"
    strip.save(strip_out, "PNG", optimize=True)
    print(f"Created {strip_out} ({strip.width}x{strip.height})")

    preview = create_folded_preview(strip)
    preview_out = OUTPUT_DIR / "grow-kit-user-guide-foldable-preview.png"
    preview.save(preview_out, "PNG", optimize=True)
    print(f"Created {preview_out} ({preview.width}x{preview.height})")


if __name__ == "__main__":
    main()
