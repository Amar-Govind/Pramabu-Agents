#!/usr/bin/env python3
"""Generate a foldable (accordion "grow trail") Parambu Organics user guide.

Instead of one flat poster, the guide unfolds like a trail map: two long
strips (front + back of a single scored card) with four panels each. Fold it
closed and the cover panel becomes a mini seed-packet-style tag; unfold it
zig-zag style and the seven steps reveal themselves in sequence along a
dotted "grow trail" that runs the length of every panel.

Panel order (accordion / zig-zag fold, read left to right on each sheet):
    Sheet A (front): [Cover] [Step 1] [Step 2] [Step 3]
    Sheet B (back):  [Step 4] [Step 5] [Step 6] [Step 7 + Back cover]

Also renders a small "folded" mockup so the concept reads at a glance.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from generate_user_guide import (  # noqa: E402
    FEATURES,
    FOREST,
    GOLD,
    ICON_DRAWERS,
    LOGO_PATH,
    STEPS,
    TEXT_MUTED,
    WHITE,
    draw_leaf_icon,
    load_font,
    load_sans,
    make_background,
    prepare_photo,
    refresh_step_one_photo,
    resolve_photo,
    text_width,
    wrap_text,
)

OUTPUT_DIR = ROOT / "output"

FOREST_DEEP = (18, 46, 34)
CREAM_SOFT = (250, 245, 234)
TRAIL_BROWN = (150, 112, 78)

# --- Panel geometry ------------------------------------------------------
PANEL_W = 620
PANEL_H = 1500
GUTTER = 96  # fold zone between adjacent panels
MARGIN = 70

SHEET_W = MARGIN * 2 + PANEL_W * 4 + GUTTER * 3
SHEET_H = MARGIN * 2 + PANEL_H

PANEL_X = [MARGIN + i * (PANEL_W + GUTTER) for i in range(4)]

# Panel assignment: index into STEPS (0-based) or a sentinel string.
FRONT_PANELS = ["cover", 0, 1, 2]
BACK_PANELS = [3, 4, 5, "step7+back"]


def rotated_text(text: str, font, fill, *, angle: int = 90) -> Image.Image:
    """Render text to a transparent image and rotate it (for gutter labels)."""
    tmp = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    draw = ImageDraw.Draw(tmp)
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0] + 4, bbox[3] - bbox[1] + 4
    label = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(label).text((2 - bbox[0], 2 - bbox[1]), text, font=font, fill=fill)
    return label.rotate(angle, expand=True, resample=Image.BICUBIC)


def draw_fold_chevrons(draw: ImageDraw.ImageDraw, cx: int, y: int, mountain: bool) -> None:
    """A tiny paper-fold pictogram: peak (mountain) or notch (valley)."""
    s = 12
    if mountain:
        pts = [(cx - s, y + s * 0.6), (cx, y - s * 0.7), (cx + s, y + s * 0.6)]
    else:
        pts = [(cx - s, y - s * 0.6), (cx, y + s * 0.7), (cx + s, y - s * 0.6)]
    draw.line(pts, fill=(*TRAIL_BROWN, 235), width=3, joint="curve")


def draw_fold_gutter(canvas: Image.Image, x_left: int, top: int, bottom: int, seq: int) -> None:
    """Dashed score line + fold-direction cues down the middle of a gutter."""
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx = x_left + GUTTER // 2

    dash, gap = 14, 10
    y = top + 10
    while y < bottom - 10:
        draw.line((cx, y, cx, min(y + dash, bottom - 10)), fill=(*TRAIL_BROWN, 190), width=2)
        y += dash + gap

    mountain = seq % 2 == 1
    for frac in (0.22, 0.5, 0.78):
        draw_fold_chevrons(draw, cx, int(top + (bottom - top) * frac), mountain)

    badge_r = 22
    badge_cy = top - 4
    draw.ellipse(
        (cx - badge_r, badge_cy - badge_r, cx + badge_r, badge_cy + badge_r),
        fill=(*CREAM_SOFT, 255),
        outline=(*TRAIL_BROWN, 255),
        width=2,
    )
    canvas.alpha_composite(overlay)

    num_font = load_sans(18, bold=True)
    label = f"F{seq}"
    d2 = ImageDraw.Draw(canvas)
    tw = text_width(d2, label, num_font)
    d2.text((cx - tw // 2, badge_cy - 11), label, font=num_font, fill=TRAIL_BROWN)

    fold_kind = "MOUNTAIN FOLD" if mountain else "VALLEY FOLD"
    tag = rotated_text(fold_kind, load_sans(13, bold=True), (*TRAIL_BROWN, 220))
    canvas.alpha_composite(tag, (cx - tag.width // 2, (top + bottom) // 2 - tag.height // 2))


def draw_seed_hole(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int = 11) -> None:
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*CREAM_SOFT, 255), outline=(*GOLD, 255), width=2)
    draw.ellipse((cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4), fill=(*FOREST_DEEP, 255))


def panel_card_base(w: int, h: int, *, dark: bool = False, arch: bool = False) -> tuple[Image.Image, ImageDraw.ImageDraw, int]:
    """Rounded card shape used for every panel; the cover panel gets a pennant arch."""
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    arch_h = 96 if arch else 0
    body_fill = (*FOREST_DEEP, 250) if dark else (*WHITE, 238)
    outline = (*GOLD, 220)
    draw.rounded_rectangle((0, arch_h, w - 1, h - 1), radius=26, fill=body_fill, outline=outline, width=3)
    if arch:
        flap_w = w * 0.42
        cx = w // 2
        draw.polygon(
            [(cx - flap_w / 2, arch_h + 6), (cx, 6), (cx + flap_w / 2, arch_h + 6)],
            fill=body_fill,
            outline=outline,
        )
        draw_seed_hole(draw, cx, 40)
    return card, draw, arch_h


def draw_progress_trail(draw: ImageDraw.ImageDraw, w: int, cy: int, current_step: int, total: int = 7) -> None:
    """A 'you are here' waypoint row echoing the cover's grow-trail motif."""
    gap = 34
    total_w = gap * (total - 1)
    start_x = (w - total_w) // 2
    for i in range(total):
        cx = start_x + i * gap
        step_num = i + 1
        if step_num < current_step:
            draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=GOLD)
        elif step_num == current_step:
            draw.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), outline=GOLD, width=2)
            draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=FOREST)
        else:
            draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), outline=(*TRAIL_BROWN, 180), width=2)
        if i < total - 1:
            lx0, lx1 = cx + 13, cx + gap - 13
            xx = lx0
            while xx < lx1:
                draw.line((xx, cy, min(xx + 4, lx1), cy), fill=(*TRAIL_BROWN, 150), width=2)
                xx += 8

    label_font = load_sans(14, bold=True)
    label = f"STEP {current_step} OF {total}"
    tw = draw.textbbox((0, 0), label, font=label_font)
    lw = tw[2] - tw[0]
    draw.text(((w - lw) // 2, cy + 22), label, font=label_font, fill=TRAIL_BROWN)


def draw_ghost_numeral(card: Image.Image, w: int, top: int, bottom: int, step_num: int) -> None:
    """A soft oversized numeral watermark that fills leftover panel space."""
    avail_h = bottom - top
    size = max(40, min(int(avail_h * 0.92), 320))
    font = load_font(size, bold=True)
    label = f"{step_num:02d}"
    tmp = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    bbox = ImageDraw.Draw(tmp).textbbox((0, 0), label, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    layer = Image.new("RGBA", (w, bottom - top), (0, 0, 0, 0))
    tx = (w - text_w) // 2 - bbox[0]
    ty = (avail_h - text_h) // 2 - bbox[1]
    ImageDraw.Draw(layer).text((tx, ty), label, font=font, fill=(*GOLD, 34))
    card.alpha_composite(layer, (0, top))


def draw_cover_panel(canvas: Image.Image, x0: int, y0: int, w: int, h: int) -> None:
    card, draw, arch_h = panel_card_base(w, h, dark=True, arch=True)

    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo_w = w - 200
    logo_h = int(logo.height * (logo_w / logo.width))
    logo_img = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
    chip_pad = 22
    chip = Image.new("RGBA", (logo_w + chip_pad * 2, logo_h + chip_pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(chip).rounded_rectangle(
        (0, 0, chip.width - 1, chip.height - 1), radius=18, fill=(*CREAM_SOFT, 255)
    )
    chip.alpha_composite(logo_img, (chip_pad, chip_pad))
    logo_y = arch_h + 56
    card.alpha_composite(chip, ((w - chip.width) // 2, logo_y))

    title_font = load_font(50, bold=True)
    script_font = load_font(27, italic=True)
    y = logo_y + chip.height + 46
    for line in ("Grow Fresh", "Food"):
        tw = text_width(draw, line, title_font)
        draw.text(((w - tw) // 2, y), line, font=title_font, fill=CREAM_SOFT)
        y += 62
    y += 6
    tw = text_width(draw, "A Fold-Out Grow Trail", script_font)
    draw.text(((w - tw) // 2, y), "A Fold-Out Grow Trail", font=script_font, fill=GOLD)
    y += 60

    # Seven dots = seven steps, styled like beads on the grow trail.
    dot_r, dot_gap = 9, 30
    total_w = dot_gap * 6
    start_x = (w - total_w) // 2
    dy = y + 20
    for i in range(7):
        cx = start_x + i * dot_gap
        draw.ellipse((cx - dot_r, dy - dot_r, cx + dot_r, dy + dot_r), fill=GOLD)
        num_font = load_sans(12, bold=True)
        label = str(i + 1)
        tw2 = text_width(draw, label, num_font)
        draw.text((cx - tw2 / 2, dy - 7), label, font=num_font, fill=FOREST_DEEP)
        if i < 6:
            mx0, mx1 = cx + dot_r + 3, cx + dot_gap - dot_r - 3
            my = dy
            step = 8
            xx = mx0
            while xx < mx1:
                draw.line((xx, my, min(xx + 4, mx1), my), fill=(*GOLD, 200), width=2)
                xx += step

    quote_font = load_sans(19)
    quote_lines = wrap_text(draw, "7 simple steps from seed to harvest \u2014 unfold panel by panel.", quote_font, w - 90)
    qy = dy + 46
    for line in quote_lines:
        tw3 = text_width(draw, line, quote_font)
        draw.text(((w - tw3) // 2, qy), line, font=quote_font, fill=(*CREAM_SOFT, 235))
        qy += 26

    # A mini trail-map legend previewing every stop ahead, styled like a
    # waypoint list running down the cover.
    legend_top = qy + 44
    heading_font = load_sans(14, bold=True)
    heading = "WHAT'S AHEAD"
    tw_h = text_width(draw, heading, heading_font)
    draw.text(((w - tw_h) // 2, legend_top), heading, font=heading_font, fill=(*GOLD, 235))

    item_font = load_sans(18)
    list_x = 74
    list_y = legend_top + 40
    row_h = 62
    marker_r = 11
    for i, (_, step_title, _) in enumerate(STEPS):
        mcy = list_y + i * row_h
        if i > 0:
            draw.line((list_x, mcy - row_h + marker_r + 4, list_x, mcy - marker_r - 4), fill=(*GOLD, 170), width=2)
        draw.ellipse(
            (list_x - marker_r, mcy - marker_r, list_x + marker_r, mcy + marker_r),
            fill=(*FOREST_DEEP, 255),
            outline=(*GOLD, 255),
            width=2,
        )
        num_font_small = load_sans(13, bold=True)
        num_label = str(i + 1)
        ntw = text_width(draw, num_label, num_font_small)
        draw.text((list_x - ntw / 2, mcy - 9), num_label, font=num_font_small, fill=GOLD)
        draw.text((list_x + marker_r + 16, mcy - 11), step_title, font=item_font, fill=(*CREAM_SOFT, 240))

    flourish_y = list_y + (len(STEPS) - 1) * row_h + 44
    draw.line((70, flourish_y, w - 70, flourish_y), fill=(*GOLD, 150), width=1)
    fs = 9
    fcx = w // 2
    draw.polygon(
        [
            (fcx, flourish_y - fs),
            (fcx + fs * 0.55, flourish_y - fs * 0.1),
            (fcx, flourish_y + fs * 0.75),
            (fcx - fs * 0.55, flourish_y - fs * 0.1),
        ],
        fill=GOLD,
    )

    cta_font = load_sans(21, bold=True)
    cta = "Unfold to begin \u2192"
    tw4 = text_width(draw, cta, cta_font)
    draw.text(((w - tw4) // 2, h - 76), cta, font=cta_font, fill=GOLD)

    canvas.alpha_composite(card, (x0, y0))


def draw_step_panel(canvas: Image.Image, x0: int, y0: int, w: int, h: int, step_num: int) -> None:
    photo_name, title, description = STEPS[step_num - 1]
    card, draw, _ = panel_card_base(w, h)

    badge_r = 30
    cx, cy = 56, 54
    draw.ellipse((cx - badge_r, cy - badge_r, cx + badge_r, cy + badge_r), fill=FOREST)
    num_font = load_sans(28, bold=True)
    label = str(step_num)
    tw = text_width(draw, label, num_font)
    draw.text((cx - tw / 2, cy - 17), label, font=num_font, fill=WHITE)

    title_font = load_font(30, bold=True)
    title_lines = wrap_text(draw, title, title_font, w - 130)
    ty = 30
    for line in title_lines:
        draw.text((cx + badge_r + 18, ty), line, font=title_font, fill=FOREST)
        ty += 36

    photo_top = max(ty + 8, 108)
    photo_pad = 22
    photo_w = w - photo_pad * 2
    photo_h = 460
    photo = prepare_photo(resolve_photo(photo_name), (photo_w, photo_h), contain=True)
    card.alpha_composite(photo, (photo_pad, photo_top))

    desc_font = load_sans(22)
    lines = wrap_text(draw, description, desc_font, w - 80)
    dy = photo_top + photo_h + 40
    for line in lines:
        tw2 = text_width(draw, line, desc_font)
        draw.text(((w - tw2) // 2, dy), line, font=desc_font, fill=TEXT_MUTED)
        dy += 30

    footer_line_y = h - 92
    draw_progress_trail(draw, w, dy + 56, step_num)

    ghost_top, ghost_bottom = dy + 100, footer_line_y - 30
    if ghost_bottom - ghost_top > 60:
        draw_ghost_numeral(card, w, ghost_top, ghost_bottom, step_num)

    draw.line((36, footer_line_y, w - 36, footer_line_y), fill=(*GOLD, 170), width=1)
    if step_num == 3:
        next_caption = "Flip the card \u2192 Step 4"
    else:
        next_caption = f"Next \u2192 {STEPS[step_num][1]}"
    next_font = load_sans(17, bold=True)
    tw3 = text_width(draw, next_caption, next_font)
    draw.text(((w - tw3) // 2, footer_line_y + 16), next_caption, font=next_font, fill=FOREST)

    canvas.alpha_composite(card, (x0, y0))


def draw_finale_panel(canvas: Image.Image, x0: int, y0: int, w: int, h: int) -> None:
    """Step 7 plus a condensed back cover, sharing the final panel."""
    step_num = 7
    photo_name, title, description = STEPS[step_num - 1]
    card, draw, _ = panel_card_base(w, h)

    badge_r = 30
    cx, cy = 56, 54
    draw.ellipse((cx - badge_r, cy - badge_r, cx + badge_r, cy + badge_r), fill=FOREST)
    num_font = load_sans(28, bold=True)
    label = str(step_num)
    tw = text_width(draw, label, num_font)
    draw.text((cx - tw / 2, cy - 17), label, font=num_font, fill=WHITE)

    title_font = load_font(28, bold=True)
    title_lines = wrap_text(draw, title, title_font, w - 130)
    ty = 32
    for line in title_lines:
        draw.text((cx + badge_r + 18, ty), line, font=title_font, fill=FOREST)
        ty += 34

    photo_top = max(ty + 6, 100)
    photo_pad = 22
    photo_w = w - photo_pad * 2
    photo_h = 380
    photo = prepare_photo(resolve_photo(photo_name), (photo_w, photo_h))
    card.alpha_composite(photo, (photo_pad, photo_top))

    desc_font = load_sans(18)
    lines = wrap_text(draw, description, desc_font, w - 80)
    dy = photo_top + photo_h + 22
    for line in lines:
        tw2 = text_width(draw, line, desc_font)
        draw.text(((w - tw2) // 2, dy), line, font=desc_font, fill=TEXT_MUTED)
        dy += 24

    note_font = load_sans(15, bold=True)
    note = "No transplant shock \u00b7 Zero plastic waste"
    tw3 = text_width(draw, note, note_font)
    draw.text(((w - tw3) // 2, dy + 6), note, font=note_font, fill=FOREST)

    # Divider into the condensed back-cover block.
    divider_y = dy + 44
    draw.line((36, divider_y, w - 36, divider_y), fill=(*GOLD, 200), width=2)
    draw_leaf_icon(draw, w // 2, divider_y, size=9)

    slogan_font = load_font(24, bold=True)
    sy = divider_y + 18
    tw4 = text_width(draw, "Grow Naturally.", slogan_font)
    draw.text(((w - tw4) // 2, sy), "Grow Naturally.", font=slogan_font, fill=FOREST)
    sy += 30
    tw5 = text_width(draw, "Grow Sustainably.", slogan_font)
    draw.text(((w - tw5) // 2, sy), "Grow Sustainably.", font=slogan_font, fill=FOREST)
    sy += 46

    icon_spacing = (w - 80) // 4
    label_font = load_sans(11, bold=True)
    icon_y = sy + 30
    for i, (feat_label, icon_key) in enumerate(FEATURES):
        icx = 40 + icon_spacing // 2 + i * icon_spacing
        draw.ellipse((icx - 26, icon_y - 26, icx + 26, icon_y + 26), outline=(*GOLD, 210), width=2)
        ICON_DRAWERS[icon_key](draw, icx, icon_y, size=13)
        fy = icon_y + 34
        for fl in feat_label.split("\n"):
            tw6 = text_width(draw, fl, label_font)
            draw.text((icx - tw6 // 2, fy), fl, font=label_font, fill=FOREST)
            fy += label_font.size + 2

    contact_font = load_sans(15, bold=True)
    contact = "parambu.in \u00b7 @parambuorganics"
    tw7 = text_width(draw, contact, contact_font)
    draw.text(((w - tw7) // 2, h - 44), contact, font=contact_font, fill=TEXT_MUTED)

    canvas.alpha_composite(card, (x0, y0))


def build_sheet(panel_defs: list) -> Image.Image:
    canvas = make_background(SHEET_W, SHEET_H)
    for i, x0 in enumerate(PANEL_X):
        entry = panel_defs[i]
        y0 = MARGIN
        if entry == "cover":
            draw_cover_panel(canvas, x0, y0, PANEL_W, PANEL_H)
        elif entry == "step7+back":
            draw_finale_panel(canvas, x0, y0, PANEL_W, PANEL_H)
        else:
            draw_step_panel(canvas, x0, y0, PANEL_W, PANEL_H, entry + 1)
        if i > 0:
            gutter_x = PANEL_X[i - 1] + PANEL_W
            draw_fold_gutter(canvas, gutter_x, MARGIN, MARGIN + PANEL_H, i)
    return canvas.convert("RGB")


def build_folded_mockup() -> Image.Image:
    """A small hero mockup of the guide closed shop, showing the accordion pleats."""
    w, h = 900, 1220
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bg = make_background(w, h)
    canvas.alpha_composite(bg)

    stack_w = 360
    stack_h = int(stack_w * PANEL_H / PANEL_W)
    cx, cy = w // 2, h // 2 + 90
    layers = 6
    offset = 16
    for i in range(layers, 0, -1):
        dx = (layers - i) * offset
        dy = (layers - i) * (offset * 0.55)
        shade = 235 - i * 10
        box = (
            cx - stack_w // 2 + dx,
            cy - stack_h // 2 + dy,
            cx + stack_w // 2 + dx,
            cy + stack_h // 2 + dy,
        )
        shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rounded_rectangle(
            (box[0] + 10, box[1] + 14, box[2] + 10, box[3] + 14), radius=24, fill=(20, 30, 20, 60)
        )
        canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(6)))
        ImageDraw.Draw(canvas).rounded_rectangle(
            box, radius=24, fill=(shade, shade - 6, shade - 20), outline=(*GOLD, 160), width=2
        )

    # Render the cover at full resolution, then scale down, so every detail
    # (logo, waypoint list, type) stays crisp and correctly proportioned.
    cover_full = Image.new("RGBA", (PANEL_W, PANEL_H), (0, 0, 0, 0))
    draw_cover_panel(cover_full, 0, 0, PANEL_W, PANEL_H)
    cover_card = cover_full.resize((stack_w, stack_h), Image.Resampling.LANCZOS)
    cover_box = (cx - stack_w // 2, cy - stack_h // 2, cx + stack_w // 2, cy + stack_h // 2)
    canvas.alpha_composite(cover_card, (int(cover_box[0]), int(cover_box[1])))

    title_font = load_font(40, bold=True)
    sub_font = load_sans(20)
    d = ImageDraw.Draw(canvas)
    ty = 60
    line1 = "Folds flat. Opens into a"
    line2 = "7-step grow trail."
    tw = text_width(d, line1, title_font)
    d.text(((w - tw) // 2, ty), line1, font=title_font, fill=FOREST)
    tw2 = text_width(d, line2, title_font)
    d.text(((w - tw2) // 2, ty + 50), line2, font=title_font, fill=FOREST)

    sub = "Pocket-size accordion card \u00b7 fits inside every kit"
    tw3 = text_width(d, sub, sub_font)
    d.text(((w - tw3) // 2, ty + 112), sub, font=sub_font, fill=TEXT_MUTED)

    footnote_font = load_sans(15)
    footnote = "8-panel zig-zag fold \u00b7 die-line finalized with print vendor"
    tw4 = text_width(d, footnote, footnote_font)
    d.text(((w - tw4) // 2, h - 46), footnote, font=footnote_font, fill=(*TEXT_MUTED, 220))

    return canvas.convert("RGB")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    refresh_step_one_photo()

    front = build_sheet(FRONT_PANELS)
    back = build_sheet(BACK_PANELS)
    mockup = build_folded_mockup()

    front_path = OUTPUT_DIR / "grow-kit-foldable-guide-front.png"
    back_path = OUTPUT_DIR / "grow-kit-foldable-guide-back.png"
    mockup_path = OUTPUT_DIR / "grow-kit-foldable-guide-folded-mockup.png"

    front.save(front_path, "PNG", optimize=True)
    back.save(back_path, "PNG", optimize=True)
    mockup.save(mockup_path, "PNG", optimize=True)

    print(f"Created {front_path} ({front.width}x{front.height})")
    print(f"Created {back_path} ({back.width}x{back.height})")
    print(f"Created {mockup_path} ({mockup.width}x{mockup.height})")


if __name__ == "__main__":
    main()
