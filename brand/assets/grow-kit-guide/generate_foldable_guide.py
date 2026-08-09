#!/usr/bin/env python3
"""Generate the Parambu Organics grow kit user guide as a foldable leaflet.

Format
------
One A4 landscape sheet (297 x 210 mm) printed both sides and creased into a
four panel concertina of 74.25 x 210 mm panels.

    outside, left to right:  back cover | grow diary | what's in the kit | cover
    inside,  left to right:  1 + 5      | 2 + 6      | 3 + 7            | 4 + harvest

Print at 100% on A4 landscape, double sided, flipping on the short edge. That
mirroring puts the cover behind inside panel 1, so creasing the folds as
valley / mountain / valley closes the leaflet cover up and it opens straight
into step 1.

Design idea
-----------
Panels are laid out so nothing but the vine crosses a crease: every fold state
shows whole steps, and the vine threading through the gutters and sweeping back
across the middle of the inside is what carries the eye from panel to panel.
Photos sit in seed packet arches, step numbers are wax seal medallions, and the
outside carries a grow diary the gardener writes on.
"""

from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

from guide_common import (
    CREAM,
    FEATURES,
    FOREST,
    GOLD,
    KIT_CONTENTS,
    KIT_HERO_PHOTO,
    KIT_NAME,
    KIT_SUBTITLE,
    KIT_UNBOXED_PHOTO,
    KRAFT,
    KRAFT_DARK,
    LOGO_PATH,
    OUTPUT_DIR,
    STEP_SEVEN_NOTE,
    STEPS,
    TAGLINE,
    TEXT_MUTED,
    WEBSITE,
    load_sans,
    load_serif,
    refresh_foldable_photos,
    refresh_step_one_photo,
    resolve_photo,
    wrap_text,
)

DPI = 300


def mm(value: float) -> int:
    return int(round(value * DPI / 25.4))


TRIM_W, TRIM_H = mm(297), mm(210)
BLEED = mm(3)
SHEET_W, SHEET_H = TRIM_W + 2 * BLEED, TRIM_H + 2 * BLEED
PANEL_COUNT = 4
PANEL_W = TRIM_W // PANEL_COUNT
PANEL_PAD = mm(7)
CONTENT_W = PANEL_W - 2 * PANEL_PAD

# Inside sheet bands, measured down from the trim edge
EYEBROW_Y = 58
EYEBROW_RULE_Y = 132
ROW1_TOP = 196
PHOTO_H = 500
ARCH_RADIUS = mm(24)
MID_CENTER = 1160
ROW2_TOP = 1300
FOOTER_RULE_Y = 2206
FEATURE_CY = 2302
FEATURE_LABEL_Y = 2374

MEASURE = ImageDraw.Draw(Image.new("RGB", (4, 4)))

INSIDE_EYEBROWS = (
    "ORGANIC FARMING KIT",
    "GROW FRESH FOOD",
    "IN JUST 7 EASY STEPS",
    "PARAMBU ORGANICS",
)
INSIDE_PANEL_LABELS = ("STEPS 1 & 5", "STEPS 2 & 6", "STEPS 3 & 7", "STEP 4 & HARVEST")
OUTSIDE_PANEL_LABELS = ("BACK COVER", "GROW DIARY", "WHAT'S IN THE KIT", "COVER")

HARVEST_TITLE = "Harvest & Grow Again"
HARVEST_TEXT = "Pick what you need, keep the pot watered, and start your next round with a fresh seed pocket."

CONTENTS_CAPTION = "Everything you need to start your organic garden."
BEFORE_YOU_BEGIN = (
    "Pick a bright spot that gets four to six hours of sun.",
    "Keep the spray bottle filled with clean water.",
    "Write each seed name on the pencil-marked cup.",
)

DIARY_ROWS = ("Seeds sown on", "First sprout on", "Moved to grow bag on", "First harvest on")
TRACKER_DAYS = ("M", "T", "W", "T", "F", "S", "S")
CARE_NOTES = (
    "Water when the top layer of cocopeat feels dry.",
    "Morning sun is gentler than afternoon heat.",
    "Thin crowded seedlings so the strongest one thrives.",
    "Feed the soil with compost, never chemicals.",
)
REFOLD_NOTE = "Refold along the creases and slip this guide back into your kit."


def panel_x(index: int) -> int:
    return BLEED + index * PANEL_W


def panel_center(index: int) -> int:
    return panel_x(index) + PANEL_W // 2


def content_left(index: int) -> int:
    return panel_x(index) + PANEL_PAD


def ty(y: float) -> int:
    """Trim space y to sheet y."""
    return int(round(BLEED + y))


def rgba(color: tuple[int, int, int], alpha: int) -> tuple[int, int, int, int]:
    return (*color, alpha)


def rotate(point: tuple[float, float], angle: float, origin: tuple[float, float]) -> tuple[float, float]:
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    x, y = point
    return (origin[0] + x * cos_a - y * sin_a, origin[1] + x * sin_a + y * cos_a)


def quad_bezier(p0, p1, p2, samples: int = 24) -> list[tuple[float, float]]:
    points = []
    for i in range(samples + 1):
        t = i / samples
        u = 1 - t
        points.append(
            (
                u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1],
            )
        )
    return points


class Pen:
    """Vector layer drawn above output resolution and downsampled when flattened.

    Coordinates and stroke widths are given in output pixels; scaling them up
    keeps arches, vines, and hairlines smooth at print size.
    """

    def __init__(self, size: tuple[int, int], scale: int) -> None:
        self.size = size
        self.scale = scale
        self.layer = Image.new("RGBA", (size[0] * scale, size[1] * scale), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.layer)

    def _points(self, xy):
        s = self.scale
        if xy and isinstance(xy[0], (tuple, list)):
            return [(x * s, y * s) for x, y in xy]
        return [v * s for v in xy]

    def _width(self, width: float) -> int:
        return max(1, int(round(width * self.scale)))

    def line(self, xy, fill, width: float = 1, joint: str | None = "curve") -> None:
        self.draw.line(self._points(xy), fill=fill, width=self._width(width), joint=joint)

    def polygon(self, xy, fill=None, outline=None, width: float = 1) -> None:
        self.draw.polygon(self._points(xy), fill=fill, outline=outline, width=self._width(width))

    def ellipse(self, box, fill=None, outline=None, width: float = 1) -> None:
        self.draw.ellipse(self._points(box), fill=fill, outline=outline, width=self._width(width))

    def arc(self, box, start: float, end: float, fill, width: float = 1) -> None:
        self.draw.arc(self._points(box), start, end, fill=fill, width=self._width(width))

    def rectangle(self, box, fill=None, outline=None, width: float = 1) -> None:
        self.draw.rectangle(self._points(box), fill=fill, outline=outline, width=self._width(width))

    def rounded_rectangle(
        self, box, radius: float, fill=None, outline=None, width: float = 1, corners=None
    ) -> None:
        self.draw.rounded_rectangle(
            self._points(box),
            radius=radius * self.scale,
            fill=fill,
            outline=outline,
            width=self._width(width),
            corners=corners,
        )

    def flatten(self) -> Image.Image:
        return self.layer.resize(self.size, Image.Resampling.LANCZOS)


class Sheet:
    """One side of the leaflet: kraft paper, photos, a vector pen, and deferred type."""

    def __init__(self, name: str, scale: int, seed: int) -> None:
        self.name = name
        self.scale = scale
        self.paper = kraft_paper((SHEET_W, SHEET_H), seed)
        self.pen = Pen((SHEET_W, SHEET_H), scale)
        self._type_ops: list = []

    # -- images (composited under the vector layer) ---------------------------
    def paste(self, image: Image.Image, position: tuple[int, int]) -> None:
        self.paper.alpha_composite(image, position)

    def drop_shadow(
        self,
        mask: Image.Image,
        position: tuple[int, int],
        *,
        blur: int = 16,
        strength: float = 0.34,
        offset: tuple[int, int] = (0, 14),
    ) -> None:
        pad = blur * 2
        spread = Image.new("L", (mask.width + pad * 2, mask.height + pad * 2), 0)
        spread.paste(mask, (pad, pad))
        spread = spread.filter(ImageFilter.GaussianBlur(blur)).point(lambda p: int(p * strength))
        shadow = Image.new("RGBA", spread.size, (58, 44, 28, 0))
        shadow.putalpha(spread)
        self.paste(shadow, (position[0] - pad + offset[0], position[1] - pad + offset[1]))

    # -- type (drawn last, on top of everything) ------------------------------
    def text(self, xy, string: str, font: ImageFont.FreeTypeFont, fill, anchor: str = "ma") -> None:
        self._type_ops.append(lambda d: d.text(xy, string, font=font, fill=fill, anchor=anchor))

    def paragraph(
        self,
        x: float,
        y: float,
        string: str,
        font: ImageFont.FreeTypeFont,
        fill,
        max_width: int,
        line_height: int,
        anchor: str = "ma",
    ) -> float:
        for line in wrap_text(MEASURE, string, font, max_width):
            self.text((x, y), line, font, fill, anchor=anchor)
            y += line_height
        return y

    def tracked(
        self,
        x: float,
        y: float,
        string: str,
        font: ImageFont.FreeTypeFont,
        fill,
        tracking: float,
        centered: bool = True,
    ) -> None:
        start = x - tracked_width(string, font, tracking) / 2 if centered else x
        placements = []
        for char in string:
            placements.append((start, char))
            start += MEASURE.textlength(char, font=font) + tracking
        self._type_ops.append(
            lambda d: [d.text((px, y), char, font=font, fill=fill, anchor="la") for px, char in placements]
        )

    def render(self) -> Image.Image:
        flat = Image.alpha_composite(self.paper, self.pen.flatten())
        draw = ImageDraw.Draw(flat)
        for op in self._type_ops:
            op(draw)
        return flat.convert("RGB")


def tracked_width(string: str, font: ImageFont.FreeTypeFont, tracking: float) -> float:
    if not string:
        return 0.0
    return sum(MEASURE.textlength(c, font=font) for c in string) + tracking * (len(string) - 1)


def fit_serif(
    string: str, max_width: int, size: int, *, bold: bool = True, italic: bool = False, minimum: int = 18
) -> ImageFont.FreeTypeFont:
    while size > minimum:
        font = load_serif(size, bold=bold, italic=italic)
        if MEASURE.textlength(string, font=font) <= max_width:
            return font
        size -= 2
    return load_serif(minimum, bold=bold, italic=italic)


# ---------------------------------------------------------------------------
# Kraft paper
# ---------------------------------------------------------------------------


def _noise(size: tuple[int, int], rng: random.Random, spread: int) -> Image.Image:
    count = size[0] * size[1]
    return Image.frombytes("L", size, bytes(128 + rng.randint(-spread, spread) for _ in range(count)))


def kraft_paper(size: tuple[int, int], seed: int) -> Image.Image:
    """Deterministic kraft stock: soft mottling, fine grain, fibres, warm corners."""
    width, height = size
    rng = random.Random(seed)

    mottle = _noise((width // 8, height // 8), rng, 70)
    mottle = mottle.filter(ImageFilter.GaussianBlur(2.4)).resize(size, Image.Resampling.BICUBIC)
    tile = _noise((512, 512), rng, 10)
    grain = Image.new("L", size)
    for y in range(0, height, 512):
        for x in range(0, width, 512):
            grain.paste(tile, (x, y))
    shade = ImageChops.blend(mottle, grain, 0.5)

    def channel(base: int, strength: float) -> Image.Image:
        return shade.point(lambda p: max(0, min(255, int(base + (p - 128) * strength))))

    paper = Image.merge("RGB", (channel(CREAM[0], 0.30), channel(CREAM[1], 0.29), channel(CREAM[2], 0.25)))
    paper = paper.convert("RGBA")

    fibres = Image.new("RGBA", size, (0, 0, 0, 0))
    fibre_draw = ImageDraw.Draw(fibres)
    for _ in range(900):
        x, y = rng.randint(0, width), rng.randint(0, height)
        fibre_draw.line(
            (x, y, x + rng.randint(-90, 90), y + rng.randint(-4, 4)),
            fill=rgba(KRAFT_DARK, 16),
            width=rng.choice((1, 1, 2)),
        )
    paper.alpha_composite(fibres.filter(ImageFilter.GaussianBlur(0.7)))

    # Warm shading in the corners, built small then scaled up
    small = (width // 6, height // 6)
    corner_mask = Image.new("L", small, 0)
    corner_draw = ImageDraw.Draw(corner_mask)
    radius = small[1] // 2
    for cx, cy in ((0, 0), (small[0], 0), (0, small[1]), (small[0], small[1])):
        corner_draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=90)
    corner_mask = corner_mask.filter(ImageFilter.GaussianBlur(radius / 4)).resize(size, Image.Resampling.BICUBIC)
    warmth = Image.new("RGBA", size, rgba(KRAFT_DARK, 0))
    warmth.putalpha(corner_mask)
    paper.alpha_composite(warmth)
    return paper


# ---------------------------------------------------------------------------
# Botanical primitives
# ---------------------------------------------------------------------------


def draw_leaf(
    pen: Pen,
    base: tuple[float, float],
    length: float,
    angle: float,
    fill,
    *,
    curl: float = 0.22,
    slim: float = 0.28,
    vein: bool = True,
    vein_fill=None,
) -> None:
    """A pointed leaf growing from `base` along `angle` (radians, screen space)."""
    upper, lower, spine = [], [], []
    for i in range(19):
        t = i / 18
        along = t * length
        half = math.sin(math.pi * t**0.85) * length * slim
        bow = -curl * length * math.sin(math.pi * t) * 0.6
        spine.append((along, bow))
        upper.append((along, bow - half))
        lower.append((along, bow + half))
    pen.polygon([rotate(p, angle, base) for p in upper + lower[::-1]], fill=fill)
    if vein and length >= 46:
        pen.line(
            [rotate(p, angle, base) for p in spine],
            fill=vein_fill or rgba(CREAM, 90),
            width=max(1.2, length * 0.03),
        )


def draw_stem(pen: Pen, points: list[tuple[float, float]], width_start: float, width_end: float, fill) -> None:
    steps = len(points) - 1
    for i in range(steps):
        width = width_start + (width_end - width_start) * i / steps
        pen.line([points[i], points[i + 1]], fill=fill, width=width)


def draw_chevron(pen: Pen, center: tuple[float, float], size: float, angle: float, fill, width: float = 4) -> None:
    points = [(-size * 0.45, -size * 0.55), (size * 0.45, 0.0), (-size * 0.45, size * 0.55)]
    pen.line([rotate(p, angle, center) for p in points], fill=fill, width=width)


def draw_vine(
    pen: Pen,
    start: tuple[float, float],
    end: tuple[float, float],
    amplitude: float,
    cycles: float,
    *,
    width_start: float,
    width_end: float,
    leaf_count: int,
    leaf_length: float,
    chevrons: tuple[float, ...] = (),
    samples: int = 220,
) -> list[tuple[float, float]]:
    points = []
    for i in range(samples + 1):
        t = i / samples
        x = start[0] + (end[0] - start[0]) * t
        y = start[1] + (end[1] - start[1]) * t + amplitude * math.sin(t * math.pi * 2 * cycles)
        points.append((x, y))
    draw_stem(pen, points, width_start, width_end, rgba(FOREST, 235))

    def tangent(index: int) -> float:
        a = points[max(0, index - 2)]
        b = points[min(len(points) - 1, index + 2)]
        return math.atan2(b[1] - a[1], b[0] - a[0])

    for i in range(leaf_count):
        t = (i + 0.5) / leaf_count
        index = int(t * samples)
        side = -1 if i % 2 == 0 else 1
        grow = 0.78 + 0.44 * math.sin(math.pi * t)
        draw_leaf(
            pen,
            points[index],
            leaf_length * grow,
            tangent(index) + side * math.radians(52),
            rgba(FOREST, 225),
        )
    for t in chevrons:
        index = int(t * samples)
        draw_chevron(pen, points[index], leaf_length * 0.55, tangent(index), rgba(GOLD, 235), width=5)
    return points


def draw_palm_fan(pen: Pen, base: tuple[float, float], size: float, fill) -> None:
    """The palmyra fan from the Parambu mark, drawn as tapering blades."""
    blades = 29
    for i in range(blades):
        t = i / (blades - 1)
        angle = math.radians(-172 + 164 * t)
        length = size * (0.76 + 0.24 * math.sin(math.pi * t))
        tip = (base[0] + math.cos(angle) * length, base[1] + math.sin(angle) * length)
        lean = math.radians(8 if t < 0.5 else -8)
        control = (
            base[0] + math.cos(angle + lean) * length * 0.55,
            base[1] + math.sin(angle + lean) * length * 0.55,
        )
        draw_stem(pen, quad_bezier(base, control, tip, 20), size * 0.07, size * 0.038, fill)
    draw_stem(pen, [base, (base[0], base[1] + size * 0.36)], size * 0.055, size * 0.032, fill)


def draw_leaf_wreath(pen: Pen, center: tuple[float, float], radius: float, fill, leaves: int = 7) -> None:
    """Laurel style ring: mirrored arcs of leaves sweeping up towards the top."""
    cx, cy = center
    for i in range(leaves):
        t = i / (leaves - 1)
        arc_angle = math.radians(66 - 128 * t)
        for side in (1, -1):
            position = arc_angle if side == 1 else math.pi - arc_angle
            base = (cx + math.cos(position) * radius, cy + math.sin(position) * radius)
            draw_leaf(
                pen,
                base,
                radius * 0.44,
                position - side * math.radians(84),
                fill,
                curl=0.26,
                slim=0.17,
                vein=False,
            )


def draw_sprout_row(pen: Pen, cx: float, ground_y: float, width: float) -> None:
    """Three sprouts of rising height above a dotted soil line."""
    dotted_line(pen, (cx - width / 2, ground_y), (cx + width / 2, ground_y), rgba(KRAFT_DARK, 190), dash=9, gap=13, width=3)
    for offset, height in ((-150, 76), (0, 118), (150, 158)):
        base = (cx + offset, ground_y - 4)
        top = (cx + offset + height * 0.12, ground_y - height)
        stem = quad_bezier(base, (cx + offset - height * 0.16, ground_y - height * 0.55), top, 14)
        draw_stem(pen, stem, 7, 4, rgba(FOREST, 230))
        draw_leaf(pen, stem[-1], height * 0.46, math.radians(-152), rgba(FOREST, 225))
        draw_leaf(pen, stem[-1], height * 0.46, math.radians(-24), rgba(FOREST, 225))
        if height > 100:
            middle = stem[len(stem) // 2]
            draw_leaf(pen, middle, height * 0.34, math.radians(-38), rgba(FOREST, 210))


def dotted_line(
    pen: Pen,
    start: tuple[float, float],
    end: tuple[float, float],
    fill,
    *,
    dash: float = 14,
    gap: float = 16,
    width: float = 3,
) -> None:
    length = math.hypot(end[0] - start[0], end[1] - start[1])
    if length <= 0:
        return
    ux, uy = (end[0] - start[0]) / length, (end[1] - start[1]) / length
    position = 0.0
    while position < length:
        run = min(dash, length - position)
        pen.line(
            [
                (start[0] + ux * position, start[1] + uy * position),
                (start[0] + ux * (position + run), start[1] + uy * (position + run)),
            ],
            fill=fill,
            width=width,
        )
        position += dash + gap


def draw_flourish(pen: Pen, cx: float, y: float, width: float, *, leaf: float = 22) -> None:
    half = width / 2
    inner = leaf * 1.6
    pen.line([(cx - half, y), (cx - inner, y)], fill=rgba(GOLD, 215), width=2)
    pen.line([(cx + inner, y), (cx + half, y)], fill=rgba(GOLD, 215), width=2)
    draw_leaf(pen, (cx - inner + 2, y), leaf, math.radians(180), rgba(GOLD, 225), vein=False)
    draw_leaf(pen, (cx + inner - 2, y), leaf, 0.0, rgba(GOLD, 225), vein=False)
    pen.ellipse((cx - 5, y - 5, cx + 5, y + 5), fill=rgba(FOREST, 230))


def draw_arrow(pen: Pen, cx: float, y: float, length: float, fill) -> None:
    pen.line([(cx - length / 2, y), (cx + length / 2 - 6, y)], fill=fill, width=4)
    draw_chevron(pen, (cx + length / 2 - 10, y), 26, 0.0, fill, width=5)


def draw_fold_diagram(pen: Pen, cx: float, y: float, width: float = 208, height: float = 60) -> None:
    """Side view of the concertina: four panels, alternating creases."""
    half_w, half_h = width / 2, height / 2
    points = [
        (cx - half_w, y + half_h),
        (cx - half_w / 2, y - half_h),
        (cx, y + half_h),
        (cx + half_w / 2, y - half_h),
        (cx + half_w, y + half_h),
    ]
    pen.line(points, fill=rgba(KRAFT_DARK, 235), width=4)
    for point in points:
        pen.ellipse((point[0] - 5, point[1] - 5, point[0] + 5, point[1] + 5), fill=rgba(GOLD, 235))


# ---------------------------------------------------------------------------
# Iconography
# ---------------------------------------------------------------------------


def icon_leaf(pen: Pen, cx: float, cy: float, size: float) -> None:
    draw_leaf(pen, (cx, cy + size * 0.8), size * 1.6, math.radians(-90), rgba(FOREST, 240), curl=0.16, vein=False)


def icon_home(pen: Pen, cx: float, cy: float, size: float) -> None:
    s = size
    pen.line(
        [(cx - s, cy - s * 0.1), (cx, cy - s), (cx + s, cy - s * 0.1)],
        fill=rgba(FOREST, 240),
        width=size * 0.14,
    )
    pen.line(
        [
            (cx - s * 0.72, cy - s * 0.05),
            (cx - s * 0.72, cy + s * 0.8),
            (cx + s * 0.72, cy + s * 0.8),
            (cx + s * 0.72, cy - s * 0.05),
        ],
        fill=rgba(FOREST, 240),
        width=size * 0.14,
    )
    draw_leaf(pen, (cx, cy + s * 0.72), s * 0.8, math.radians(-90), rgba(FOREST, 235), curl=0.18, vein=False)


def icon_hands(pen: Pen, cx: float, cy: float, size: float) -> None:
    s = size
    pen.arc((cx - s * 1.05, cy - s * 0.25, cx + s * 0.05, cy + s * 0.95), 20, 200, rgba(FOREST, 240), width=s * 0.14)
    pen.arc((cx - s * 0.05, cy - s * 0.25, cx + s * 1.05, cy + s * 0.95), 340, 160, rgba(FOREST, 240), width=s * 0.14)
    draw_leaf(pen, (cx, cy + s * 0.2), s * 0.95, math.radians(-90), rgba(FOREST, 235), curl=0.18, vein=False)


def icon_sprout(pen: Pen, cx: float, cy: float, size: float) -> None:
    s = size
    pen.arc(
        (cx - s * 0.95, cy - s * 0.55, cx + s * 0.95, cy + s * 1.15),
        200,
        340,
        rgba(FOREST, 210),
        width=s * 0.12,
    )
    pen.line([(cx, cy + s * 0.55), (cx, cy - s * 0.15)], fill=rgba(FOREST, 240), width=s * 0.12)
    draw_leaf(pen, (cx, cy - s * 0.1), s * 0.8, math.radians(-152), rgba(FOREST, 235), vein=False)
    draw_leaf(pen, (cx, cy - s * 0.1), s * 0.8, math.radians(-28), rgba(FOREST, 235), vein=False)


FEATURE_ICONS = {"leaf": icon_leaf, "home": icon_home, "hands": icon_hands, "sprout": icon_sprout}


def icon_cup(pen: Pen, cx: float, cy: float, s: float) -> None:
    ink = rgba(FOREST, 235)
    pen.line(
        [
            (cx - s * 0.42, cy - s * 0.36),
            (cx - s * 0.26, cy + s * 0.44),
            (cx + s * 0.26, cy + s * 0.44),
            (cx + s * 0.42, cy - s * 0.36),
        ],
        fill=ink,
        width=s * 0.075,
    )
    pen.line([(cx - s * 0.46, cy - s * 0.36), (cx + s * 0.46, cy - s * 0.36)], fill=ink, width=s * 0.075)
    pen.line([(cx - s * 0.37, cy - s * 0.16), (cx + s * 0.37, cy - s * 0.16)], fill=rgba(FOREST, 130), width=s * 0.045)


def icon_seeds(pen: Pen, cx: float, cy: float, s: float) -> None:
    ink = rgba(FOREST, 235)
    for offset, lift in ((-0.28, 0.05), (0.0, -0.04), (0.28, 0.06)):
        left, right = cx + s * offset - s * 0.17, cx + s * offset + s * 0.17
        top, bottom = cy - s * 0.4 + s * lift, cy + s * 0.42 + s * lift
        pen.rectangle((left, top, right, bottom), outline=ink, width=s * 0.06)
        pen.line([(left, top + s * 0.13), (right, top + s * 0.13)], fill=rgba(FOREST, 150), width=s * 0.05)


def icon_bottle(pen: Pen, cx: float, cy: float, s: float) -> None:
    ink = rgba(FOREST, 235)
    pen.rounded_rectangle(
        (cx - s * 0.28, cy - s * 0.04, cx + s * 0.28, cy + s * 0.48), radius=s * 0.09, outline=ink, width=s * 0.07
    )
    pen.rectangle((cx - s * 0.12, cy - s * 0.24, cx + s * 0.12, cy - s * 0.04), outline=ink, width=s * 0.06)
    pen.line([(cx - s * 0.12, cy - s * 0.26), (cx - s * 0.44, cy - s * 0.36)], fill=ink, width=s * 0.07)
    pen.line([(cx, cy - s * 0.3), (cx + s * 0.14, cy - s * 0.42)], fill=ink, width=s * 0.06)
    for i, (dx, dy) in enumerate(((-0.6, -0.48), (-0.66, -0.28), (-0.48, -0.18))):
        pen.ellipse(
            (cx + s * dx - s * 0.05, cy + s * dy - s * 0.05, cx + s * dx + s * 0.05, cy + s * dy + s * 0.05),
            fill=rgba(FOREST, 150 + i * 20),
        )


def icon_disc(pen: Pen, cx: float, cy: float, s: float) -> None:
    ink = rgba(FOREST, 235)
    pen.ellipse((cx - s * 0.46, cy - s * 0.46, cx + s * 0.46, cy + s * 0.46), outline=ink, width=s * 0.075)
    pen.ellipse((cx - s * 0.19, cy - s * 0.19, cx + s * 0.19, cy + s * 0.19), outline=ink, width=s * 0.055)
    for angle in range(0, 360, 45):
        a = math.radians(angle)
        pen.line(
            [
                (cx + math.cos(a) * s * 0.25, cy + math.sin(a) * s * 0.25),
                (cx + math.cos(a) * s * 0.4, cy + math.sin(a) * s * 0.4),
            ],
            fill=ink,
            width=s * 0.05,
        )


def icon_sticks(pen: Pen, cx: float, cy: float, s: float) -> None:
    ink = rgba(FOREST, 235)
    for angle, offset in ((-24, -s * 0.12), (20, s * 0.12)):
        a = math.radians(angle)
        half = s * 0.44
        start = (cx - math.cos(a) * half + offset, cy - math.sin(a) * half)
        end = (cx + math.cos(a) * half + offset, cy + math.sin(a) * half)
        pen.line([start, end], fill=ink, width=s * 0.11)
        pen.ellipse((start[0] - s * 0.07, start[1] - s * 0.07, start[0] + s * 0.07, start[1] + s * 0.07), fill=ink)
        pen.ellipse((end[0] - s * 0.07, end[1] - s * 0.07, end[0] + s * 0.07, end[1] + s * 0.07), fill=ink)


def icon_pencil(pen: Pen, cx: float, cy: float, s: float) -> None:
    ink = rgba(FOREST, 235)
    pen.line([(cx - s * 0.3, cy + s * 0.36), (cx + s * 0.22, cy - s * 0.32)], fill=ink, width=s * 0.16)
    pen.polygon(
        [(cx - s * 0.44, cy + s * 0.46), (cx - s * 0.3, cy + s * 0.2), (cx - s * 0.12, cy + s * 0.44)],
        fill=ink,
    )
    pen.line([(cx + s * 0.2, cy - s * 0.34), (cx + s * 0.4, cy - s * 0.44)], fill=rgba(FOREST, 160), width=s * 0.12)


CONTENT_ICONS = {
    "cup": icon_cup,
    "seeds": icon_seeds,
    "bottle": icon_bottle,
    "disc": icon_disc,
    "sticks": icon_sticks,
    "pencil": icon_pencil,
}


# ---------------------------------------------------------------------------
# Photo furniture
# ---------------------------------------------------------------------------


def arch_mask(size: tuple[int, int], radius: int, scale: int) -> Image.Image:
    w, h = size
    mask = Image.new("L", (w * scale, h * scale), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, w * scale - 1, h * scale - 1),
        radius=radius * scale,
        fill=255,
        corners=(True, True, False, False),
    )
    return mask.resize(size, Image.Resampling.LANCZOS)


def draw_arch_frame(pen: Pen, box: tuple[int, int, int, int], radius: int) -> None:
    x0, y0, x1, y1 = box
    pen.rounded_rectangle(box, radius=radius, outline=rgba(GOLD, 240), width=4, corners=(True, True, False, False))
    pen.rounded_rectangle(
        (x0 + 11, y0 + 11, x1 - 11, y1 - 11),
        radius=max(4, radius - 11),
        outline=rgba(CREAM, 150),
        width=2,
        corners=(True, True, False, False),
    )


def place_arch_photo(
    sheet: Sheet,
    box: tuple[int, int, int, int],
    photo_path: Path,
    *,
    radius: int = ARCH_RADIUS,
    centering: tuple[float, float] = (0.5, 0.5),
) -> None:
    """Fill an arch with a photo, cropping to the arch shape."""
    x0, y0, x1, y1 = box
    size = (x1 - x0, y1 - y0)
    mask = arch_mask(size, radius, sheet.scale)
    sheet.drop_shadow(mask, (x0, y0))
    photo = ImageOps.fit(
        Image.open(photo_path).convert("RGBA"), size, Image.Resampling.LANCZOS, centering=centering
    )
    photo.putalpha(mask)
    sheet.paste(photo, (x0, y0))
    draw_arch_frame(sheet.pen, box, radius)


def place_logo(sheet: Sheet, cx: int, top: int, width: int) -> int:
    logo = Image.open(LOGO_PATH).convert("RGBA")
    height = int(round(logo.height * width / logo.width))
    sheet.paste(logo.resize((width, height), Image.Resampling.LANCZOS), (cx - width // 2, top))
    return top + height


def draw_seal(sheet: Sheet, center: tuple[int, int], label: str, radius: int = 48) -> None:
    pen = sheet.pen
    cx, cy = center
    pen.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=rgba(FOREST, 255))
    pen.ellipse(
        (cx - radius + 7, cy - radius + 7, cx + radius - 7, cy + radius - 7),
        outline=rgba(GOLD, 200),
        width=3,
    )
    sheet.text((cx, cy), label, load_serif(46, bold=True), CREAM, anchor="mm")


def draw_finale_seal(pen: Pen, center: tuple[int, int], radius: int = 48) -> None:
    cx, cy = center
    pen.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=rgba(FOREST, 255))
    pen.ellipse(
        (cx - radius + 7, cy - radius + 7, cx + radius - 7, cy + radius - 7),
        outline=rgba(GOLD, 200),
        width=3,
    )
    draw_palm_fan(pen, (cx, cy + radius * 0.42), radius * 1.02, rgba(GOLD, 245))


def draw_organic_seal(sheet: Sheet, center: tuple[int, int], radius: int = 92, matted: bool = False) -> None:
    cx, cy = center
    pen = sheet.pen
    if matted:
        pen.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=rgba(CREAM, 238))
    pen.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=rgba(GOLD, 240), width=4)
    pen.ellipse((cx - radius + 12, cy - radius + 12, cx + radius - 12, cy + radius - 12), outline=rgba(GOLD, 130), width=2)
    draw_leaf(pen, (cx - 3, cy - radius * 0.28), radius * 0.46, math.radians(-126), rgba(FOREST, 220), vein=False)
    draw_leaf(pen, (cx + 3, cy - radius * 0.28), radius * 0.46, math.radians(-54), rgba(FOREST, 220), vein=False)
    sheet.text((cx, cy + radius * 0.03), "100%", load_serif(int(radius * 0.44), bold=True), FOREST)
    sheet.tracked(cx, cy + radius * 0.56, "ORGANIC", load_sans(int(radius * 0.26), bold=True), FOREST, 3.0)


# ---------------------------------------------------------------------------
# Inside sheet
# ---------------------------------------------------------------------------


def draw_step_cell(
    sheet: Sheet,
    panel: int,
    row_top: int,
    number: int | None,
    title: str,
    description: str,
    *,
    photo_path: Path | None = None,
    centering: tuple[float, float] = (0.5, 0.5),
    note: str | None = None,
) -> None:
    cx = panel_center(panel)
    x0 = content_left(panel)
    box = (x0, ty(row_top), x0 + CONTENT_W, ty(row_top + PHOTO_H))

    if photo_path is None:
        draw_harvest_scene(sheet, box)
        draw_finale_seal(sheet.pen, (cx, box[3]))
    else:
        place_arch_photo(sheet, box, photo_path, centering=centering)
        draw_seal(sheet, (cx, box[3]), str(number))

    y = box[3] + 66
    title_font = fit_serif(title, CONTENT_W, 46)
    for line in wrap_text(MEASURE, title, title_font, CONTENT_W):
        sheet.text((cx, y), line, title_font, FOREST)
        y += 54
    y = sheet.paragraph(cx, y + 12, description, load_sans(29), TEXT_MUTED, CONTENT_W - 20, 40)

    if note:
        y += 18
        pill_font = load_sans(23, bold=True)
        width = tracked_width(note, pill_font, 2.2) + 56
        sheet.pen.rounded_rectangle(
            (cx - width / 2, y, cx + width / 2, y + 50), radius=25, fill=rgba(GOLD, 55), outline=rgba(GOLD, 200), width=2
        )
        sheet.tracked(cx, y + 13, note, pill_font, FOREST, 2.2)


def draw_harvest_scene(sheet: Sheet, box: tuple[int, int, int, int]) -> None:
    """Line art finale for the eighth cell: a cropping plant in its grow bag."""
    pen = sheet.pen
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    ink = rgba(FOREST, 235)

    pen.rounded_rectangle(box, radius=ARCH_RADIUS, fill=rgba(KRAFT, 62), corners=(True, True, False, False))

    sun = (x1 - 112, y0 + 102)
    pen.ellipse((sun[0] - 42, sun[1] - 42, sun[0] + 42, sun[1] + 42), outline=rgba(GOLD, 235), width=4)
    for angle in range(0, 360, 45):
        a = math.radians(angle)
        pen.line(
            [
                (sun[0] + math.cos(a) * 58, sun[1] + math.sin(a) * 58),
                (sun[0] + math.cos(a) * 80, sun[1] + math.sin(a) * 80),
            ],
            fill=rgba(GOLD, 220),
            width=4,
        )

    bag_top, bag_bottom = y0 + 306, y0 + 438
    pen.line(
        [(cx - 186, bag_top), (cx - 158, bag_bottom), (cx + 158, bag_bottom), (cx + 186, bag_top)],
        fill=ink,
        width=7,
    )
    pen.arc((cx - 186, bag_top - 26, cx + 186, bag_top + 26), 0, 180, ink, width=7)
    pen.arc((cx - 186, bag_top - 26, cx + 186, bag_top + 26), 180, 360, rgba(FOREST, 110), width=5)
    pen.rounded_rectangle((cx + 106, bag_top + 44, cx + 154, bag_top + 92), radius=12, outline=rgba(FOREST, 170), width=5)
    for dx in (-84, -28, 34, 88):
        pen.ellipse((cx + dx - 7, bag_top + 4, cx + dx + 7, bag_top + 18), fill=rgba(FOREST, 120))

    stem = quad_bezier((cx - 6, bag_top - 8), (cx - 62, y0 + 176), (cx + 20, y0 + 48), 28)
    draw_stem(pen, stem, 13, 5, ink)
    for i, t in enumerate((0.12, 0.28, 0.44, 0.6, 0.76, 0.92)):
        index = int(t * (len(stem) - 1))
        side = -1 if i % 2 == 0 else 1
        draw_leaf(pen, stem[index], 132 - i * 10, math.radians(-90 + side * 60), rgba(FOREST, 230))

    # Fruit hangs outside the leaf canopy so it stays readable at print size
    for offset_x, offset_y, radius in ((146, -58, 31), (-144, -106, 27), (116, -188, 23)):
        fruit = (cx + offset_x, bag_top + offset_y)
        anchor = min(stem, key=lambda point: abs(point[1] - (fruit[1] - 44)))
        draw_stem(
            pen,
            quad_bezier(anchor, ((anchor[0] + fruit[0]) / 2, fruit[1] - 62), (fruit[0], fruit[1] - radius), 12),
            5,
            3,
            ink,
        )
        pen.ellipse(
            (fruit[0] - radius, fruit[1] - radius, fruit[0] + radius, fruit[1] + radius),
            fill=rgba(GOLD, 215),
            outline=ink,
            width=3,
        )
        for side in (-1, 1):
            draw_leaf(
                pen,
                (fruit[0], fruit[1] - radius + 3),
                radius * 0.62,
                math.radians(-90 + side * 62),
                rgba(FOREST, 225),
                vein=False,
            )


def draw_gutter_link(sheet: Sheet, crease_index: int, y: int) -> None:
    """The short vine that threads across a crease, tying two panels together."""
    x = panel_x(crease_index)
    points = draw_vine(
        sheet.pen,
        (x - 74, y),
        (x + 74, y),
        amplitude=13,
        cycles=1.0,
        width_start=6,
        width_end=6,
        leaf_count=2,
        leaf_length=44,
        samples=60,
    )
    draw_chevron(sheet.pen, (points[-1][0] + 16, points[-1][1]), 26, 0.0, rgba(GOLD, 235), width=5)


def draw_midband(sheet: Sheet) -> None:
    """The turn-around vine: it leaves step 4 and sweeps back to step 5 below."""
    pen = sheet.pen
    y = ty(MID_CENTER)
    right = BLEED + TRIM_W - PANEL_PAD
    left = BLEED + PANEL_PAD
    points = draw_vine(
        pen,
        (right, y),
        (left, y),
        amplitude=34,
        cycles=2.5,
        width_start=11,
        width_end=5,
        leaf_count=16,
        leaf_length=62,
        chevrons=(0.2, 0.5, 0.8),
    )
    curl_up = quad_bezier(points[0], (right + 26, y - 58), (right - 26, y - 104), 18)
    draw_stem(pen, curl_up, 10, 4, rgba(FOREST, 225))
    curl_down = quad_bezier(points[-1], (left - 24, y + 62), (left + 30, y + 112), 18)
    draw_stem(pen, curl_down, 6, 3, rgba(FOREST, 225))
    draw_leaf(pen, curl_down[-1], 52, math.radians(74), rgba(FOREST, 225))

    sheet.text(
        (panel_center(3), ty(MID_CENTER + 58)),
        "…the vine carries on below",
        load_serif(33, italic=True),
        rgba(FOREST, 200),
    )


def draw_panel_eyebrow(sheet: Sheet, panel: int, label: str) -> None:
    cx = panel_center(panel)
    font = load_sans(25, bold=True)
    sheet.tracked(cx, ty(EYEBROW_Y), label, font, rgba(KRAFT_DARK, 255), 5.5)
    width = tracked_width(label, font, 5.5)
    pen = sheet.pen
    y = ty(EYEBROW_RULE_Y)
    edge = CONTENT_W / 2
    pen.line([(cx - edge, y), (cx - width / 2 - 26, y)], fill=rgba(GOLD, 190), width=2)
    pen.line([(cx + width / 2 + 26, y), (cx + edge, y)], fill=rgba(GOLD, 190), width=2)
    draw_leaf(pen, (cx - 16, y), 32, 0.0, rgba(GOLD, 220), vein=False)
    draw_leaf(pen, (cx + 16, y), 32, math.radians(180), rgba(GOLD, 220), vein=False)


def draw_feature_chip(sheet: Sheet, panel: int, label: str, icon_key: str) -> None:
    cx = panel_center(panel)
    cy = ty(FEATURE_CY)
    pen = sheet.pen
    pen.ellipse((cx - 62, cy - 62, cx + 62, cy + 62), outline=rgba(GOLD, 225), width=4)
    pen.ellipse((cx - 53, cy - 53, cx + 53, cy + 53), outline=rgba(GOLD, 110), width=2)
    FEATURE_ICONS[icon_key](pen, cx, cy, 30)
    y = ty(FEATURE_LABEL_Y)
    for line in label.split("\n"):
        sheet.tracked(cx, y, line, load_sans(24, bold=True), FOREST, 3.0)
        y += 34


def build_inside(scale: int) -> Sheet:
    sheet = Sheet("inside", scale, seed=1101)
    draw_creases(sheet)
    draw_trim_marks(sheet.pen)

    for panel, label in enumerate(INSIDE_EYEBROWS):
        draw_panel_eyebrow(sheet, panel, label)

    for crease in (1, 2, 3):
        draw_gutter_link(sheet, crease, ty(ROW1_TOP + PHOTO_H * 0.52))
        draw_gutter_link(sheet, crease, ty(ROW2_TOP + PHOTO_H * 0.52))

    draw_midband(sheet)

    for panel in range(4):
        photo, title, description = STEPS[panel]
        # Step 1 uses the canister-free cut of the kit spread: it fills the arch
        # without slicing through the packaging, and the canister leads the cover.
        draw_step_cell(
            sheet,
            panel,
            ROW1_TOP,
            panel + 1,
            title,
            description,
            photo_path=resolve_photo(KIT_UNBOXED_PHOTO if panel == 0 else photo),
        )

    for offset in range(3):
        photo, title, description = STEPS[4 + offset]
        draw_step_cell(
            sheet,
            offset,
            ROW2_TOP,
            5 + offset,
            title,
            description,
            photo_path=resolve_photo(photo),
            note=STEP_SEVEN_NOTE if offset == 2 else None,
        )
    draw_step_cell(sheet, 3, ROW2_TOP, None, HARVEST_TITLE, HARVEST_TEXT)

    for panel in range(4):
        cx = panel_center(panel)
        sheet.pen.line(
            (cx - CONTENT_W / 2, ty(FOOTER_RULE_Y), cx + CONTENT_W / 2, ty(FOOTER_RULE_Y)),
            fill=rgba(GOLD, 150),
            width=2,
        )
        label, icon_key = FEATURES[panel]
        draw_feature_chip(sheet, panel, label, icon_key)

    draw_slug(sheet, "INSIDE", INSIDE_PANEL_LABELS)
    return sheet


# ---------------------------------------------------------------------------
# Outside sheet
# ---------------------------------------------------------------------------


def draw_panel_frame(sheet: Sheet, panel: int) -> None:
    pen = sheet.pen
    x0, x1 = panel_x(panel) + mm(5), panel_x(panel) + PANEL_W - mm(5)
    y0, y1 = ty(mm(5)), ty(TRIM_H - mm(5))
    pen.rounded_rectangle((x0, y0, x1, y1), radius=mm(3), outline=rgba(GOLD, 205), width=3)
    pen.rounded_rectangle((x0 + 11, y0 + 11, x1 - 11, y1 - 11), radius=mm(2.4), outline=rgba(GOLD, 105), width=2)
    for cx, cy, angle in (
        (x0 + 26, y0 + 26, 45),
        (x1 - 26, y0 + 26, 135),
        (x1 - 26, y1 - 26, 225),
        (x0 + 26, y1 - 26, 315),
    ):
        draw_leaf(pen, (cx, cy), 40, math.radians(angle), rgba(GOLD, 215), vein=False)


def panel_cover(sheet: Sheet, panel: int) -> None:
    cx = panel_center(panel)
    x0 = content_left(panel)
    pen = sheet.pen

    place_logo(sheet, cx, ty(170), 600)
    draw_flourish(pen, cx, ty(400), 300)
    sheet.tracked(cx, ty(440), KIT_NAME.upper(), load_sans(29, bold=True), rgba(KRAFT_DARK, 255), 6.0)

    head_font = fit_serif("Fresh Food", CONTENT_W, 88)
    sheet.text((cx, ty(520)), "Grow", head_font, FOREST)
    sheet.text((cx, ty(620)), "Fresh Food", head_font, FOREST)
    sheet.text((cx, ty(748)), "in Just 7 Easy Steps", load_serif(48, italic=True), FOREST)

    arch = (x0, ty(846), x0 + CONTENT_W, ty(1686))
    place_arch_photo(sheet, arch, resolve_photo(KIT_HERO_PHOTO), radius=mm(30))
    draw_organic_seal(sheet, (x0 + 104, ty(1592)), radius=86, matted=True)

    draw_flourish(pen, cx, ty(1760), 260, leaf=18)
    sheet.tracked(cx, ty(1800), "USER GUIDE", load_sans(31, bold=True), FOREST, 7.0)
    sheet.text((cx, ty(1876)), "Unfold to see every step", load_serif(37, italic=True), TEXT_MUTED)
    draw_arrow(pen, cx, ty(1962), 132, rgba(GOLD, 235))

    pen.line((x0 + 40, ty(2116), x0 + CONTENT_W - 40, ty(2116)), fill=rgba(GOLD, 160), width=2)
    sheet.tracked(cx, ty(2154), KIT_SUBTITLE.upper(), load_sans(25, bold=True), rgba(KRAFT_DARK, 255), 5.0)
    sheet.text((cx, ty(2226)), WEBSITE, load_serif(42, bold=True), GOLD)
    sheet.text((cx, ty(2304)), TAGLINE, load_serif(33, italic=True), TEXT_MUTED)


def panel_kit_contents(sheet: Sheet, panel: int) -> None:
    cx = panel_center(panel)
    x0 = content_left(panel)
    pen = sheet.pen

    sheet.tracked(cx, ty(196), "STEP ZERO", load_sans(26, bold=True), rgba(KRAFT_DARK, 255), 6.0)
    sheet.text((cx, ty(252)), "What's in the Kit", fit_serif("What's in the Kit", CONTENT_W, 58), FOREST)
    draw_flourish(pen, cx, ty(360), 240, leaf=18)

    name_font = load_serif(32, bold=False)
    sub_font = load_sans(24)
    y = ty(424)
    for icon_key, name, detail in KIT_CONTENTS:
        CONTENT_ICONS[icon_key](pen, x0 + 44, y + 40, 76)
        sheet.text((x0 + 108, y), name, name_font, FOREST, anchor="la")
        sheet.paragraph(x0 + 108, y + 46, detail, sub_font, TEXT_MUTED, CONTENT_W - 168, 32, anchor="la")
        box_right = x0 + CONTENT_W
        pen.rounded_rectangle(
            (box_right - 38, y + 12, box_right, y + 50), radius=6, outline=rgba(KRAFT_DARK, 220), width=3
        )
        dotted_line(
            pen,
            (x0 + 116 + MEASURE.textlength(name, font=name_font), y + 30),
            (box_right - 54, y + 30),
            rgba(KRAFT_DARK, 150),
            dash=5,
            gap=12,
            width=3,
        )
        y += 172

    pen.line((x0, y - 4, x0 + CONTENT_W, y - 4), fill=rgba(GOLD, 150), width=2)
    y += 44
    sheet.tracked(cx, y, "BEFORE YOU BEGIN", load_sans(26, bold=True), FOREST, 5.0)
    y += 74
    body = load_sans(28)
    for tip in BEFORE_YOU_BEGIN:
        draw_leaf(pen, (x0 + 6, y + 18), 34, math.radians(-30), rgba(GOLD, 235))
        y = sheet.paragraph(x0 + 56, y, tip, body, TEXT_MUTED, CONTENT_W - 56, 40, anchor="la") + 24

    y += 26
    dotted_line(pen, (x0, y), (x0 + CONTENT_W, y), rgba(KRAFT_DARK, 150), dash=8, gap=12, width=2)
    sheet.paragraph(cx, y + 30, CONTENTS_CAPTION, load_serif(30, italic=True), TEXT_MUTED, CONTENT_W, 40)
    draw_sprout_row(pen, cx, ty(2246), CONTENT_W - 40)
    draw_panel_footer(sheet, panel)


def panel_grow_diary(sheet: Sheet, panel: int) -> None:
    cx = panel_center(panel)
    x0 = content_left(panel)
    pen = sheet.pen

    sheet.tracked(cx, ty(196), "MY RECORD", load_sans(26, bold=True), rgba(KRAFT_DARK, 255), 6.0)
    sheet.text((cx, ty(252)), "Grow Diary", fit_serif("Grow Diary", CONTENT_W, 66), FOREST)
    draw_flourish(pen, cx, ty(372), 240, leaf=18)

    y = ty(440)
    sheet.tracked(cx, y, "DATES TO REMEMBER", load_sans(26, bold=True), FOREST, 5.0)
    y += 76
    for label in DIARY_ROWS:
        sheet.text((x0, y), label, load_sans(26), TEXT_MUTED, anchor="la")
        dotted_line(pen, (x0, y + 62), (x0 + CONTENT_W, y + 62), rgba(KRAFT_DARK, 190), dash=7, gap=11, width=3)
        y += 112

    y += 24
    pen.line((x0, y, x0 + CONTENT_W, y), fill=rgba(GOLD, 150), width=2)
    y += 50
    sheet.tracked(cx, y, "WATER TRACKER", load_sans(26, bold=True), FOREST, 5.0)
    y += 78

    label_col = 104
    column = (CONTENT_W - label_col) / len(TRACKER_DAYS)
    for i, day in enumerate(TRACKER_DAYS):
        sheet.text((x0 + label_col + column * (i + 0.5), y), day, load_sans(25, bold=True), rgba(GOLD, 255))
    y += 52
    for week in range(4):
        row_y = y + week * 92 + 24
        sheet.text((x0, row_y - 12), f"WK {week + 1}", load_sans(23, bold=True), rgba(KRAFT_DARK, 255), anchor="la")
        for i in range(len(TRACKER_DAYS)):
            column_cx = x0 + label_col + column * (i + 0.5)
            pen.ellipse(
                (column_cx - 25, row_y - 25, column_cx + 25, row_y + 25), outline=rgba(KRAFT_DARK, 215), width=3
            )
    y += 4 * 92 + 30

    sheet.text((cx, y), "Tick a circle each time you water.", load_serif(28, italic=True), TEXT_MUTED)
    y += 70
    pen.line((x0, y, x0 + CONTENT_W, y), fill=rgba(GOLD, 150), width=2)
    y += 50
    sheet.tracked(cx, y, "EVERYDAY CARE", load_sans(26, bold=True), FOREST, 5.0)
    y += 76
    body = load_sans(28)
    for note in CARE_NOTES:
        draw_leaf(pen, (x0 + 6, y + 18), 34, math.radians(-30), rgba(GOLD, 235))
        y = sheet.paragraph(x0 + 56, y, note, body, TEXT_MUTED, CONTENT_W - 56, 40, anchor="la") + 24
    draw_panel_footer(sheet, panel)


def panel_back_cover(sheet: Sheet, panel: int) -> None:
    cx = panel_center(panel)
    x0 = content_left(panel)
    pen = sheet.pen

    place_logo(sheet, cx, ty(226), 520)
    draw_flourish(pen, cx, ty(500), 300)

    slogan_font = fit_serif("Grow Sustainably.", CONTENT_W, 58)
    sheet.text((cx, ty(566)), "Grow Naturally.", slogan_font, FOREST)
    sheet.text((cx, ty(646)), "Grow Sustainably.", slogan_font, FOREST)
    draw_flourish(pen, cx, ty(756), 300)
    sheet.text((cx, ty(800)), TAGLINE, load_serif(40, italic=True), TEXT_MUTED)

    medallion = (cx, ty(1214))
    pen.ellipse(
        (medallion[0] - 238, medallion[1] - 238, medallion[0] + 238, medallion[1] + 238),
        outline=rgba(GOLD, 120),
        width=2,
    )
    draw_leaf_wreath(pen, medallion, 202, rgba(GOLD, 215))
    draw_palm_fan(pen, (medallion[0], medallion[1] + 116), 216, rgba(GOLD, 245))

    sheet.tracked(cx, ty(1546), "GROW MORE WITH US", load_sans(26, bold=True), rgba(KRAFT_DARK, 255), 5.0)
    sheet.text((cx, ty(1608)), "Oils · Soap · Gardening", load_serif(40, bold=False), FOREST)
    sheet.text((cx, ty(1704)), WEBSITE, load_serif(48, bold=True), GOLD)

    dotted_line(pen, (x0, ty(1808)), (x0 + CONTENT_W, ty(1808)), rgba(KRAFT_DARK, 160), dash=8, gap=12, width=2)
    sheet.paragraph(cx, ty(1848), REFOLD_NOTE, load_serif(30, italic=True), TEXT_MUTED, CONTENT_W, 42)

    draw_fold_diagram(pen, cx, ty(2064))
    sheet.tracked(cx, ty(2136), "FOUR PANEL CONCERTINA", load_sans(23, bold=True), rgba(KRAFT_DARK, 255), 4.0)
    draw_panel_footer(sheet, panel)


def draw_panel_footer(sheet: Sheet, panel: int) -> None:
    cx = panel_center(panel)
    draw_flourish(sheet.pen, cx, ty(2320), 200, leaf=16)
    sheet.tracked(cx, ty(2352), WEBSITE.upper(), load_sans(23, bold=True), rgba(KRAFT_DARK, 255), 4.0)


def build_outside(scale: int) -> Sheet:
    sheet = Sheet("outside", scale, seed=2202)
    draw_creases(sheet)
    draw_trim_marks(sheet.pen)
    for panel in range(4):
        draw_panel_frame(sheet, panel)
    panel_back_cover(sheet, 0)
    panel_grow_diary(sheet, 1)
    panel_kit_contents(sheet, 2)
    panel_cover(sheet, 3)
    draw_slug(sheet, "OUTSIDE", OUTSIDE_PANEL_LABELS)
    return sheet


# ---------------------------------------------------------------------------
# Folding and trimming furniture
# ---------------------------------------------------------------------------


def draw_creases(sheet: Sheet) -> None:
    pen = sheet.pen
    for crease in (1, 2, 3):
        x = panel_x(crease)
        dotted_line(pen, (x, ty(mm(3))), (x, ty(TRIM_H - mm(3))), rgba(GOLD, 120), dash=15, gap=17, width=3)
        pen.line([(x, 0), (x, BLEED - 5)], fill=rgba(KRAFT_DARK, 255), width=3)
        pen.line([(x, SHEET_H - BLEED + 5), (x, SHEET_H)], fill=rgba(KRAFT_DARK, 255), width=3)
        draw_leaf(pen, (x, ty(mm(3)) + 4), 30, math.radians(90), rgba(GOLD, 200), vein=False)
        draw_leaf(pen, (x, ty(TRIM_H - mm(3)) - 4), 30, math.radians(-90), rgba(GOLD, 200), vein=False)


def draw_trim_marks(pen: Pen) -> None:
    length = BLEED - 6
    for x in (BLEED, SHEET_W - BLEED):
        for y in (BLEED, SHEET_H - BLEED):
            outward_x = -1 if x == BLEED else 1
            outward_y = -1 if y == BLEED else 1
            pen.line([(x, y + outward_y * 6), (x, y + outward_y * (6 + length))], fill=rgba(KRAFT_DARK, 255), width=3)
            pen.line([(x + outward_x * 6, y), (x + outward_x * (6 + length), y)], fill=rgba(KRAFT_DARK, 255), width=3)


def draw_slug(sheet: Sheet, side: str, panel_labels: tuple[str, ...]) -> None:
    slug = (
        f"PARAMBU ORGANICS · {KIT_NAME.upper()} · USER GUIDE · {side} · A4 LANDSCAPE 297 × 210 MM · "
        "PRINT AT 100% · DOUBLE SIDED, FLIP ON SHORT EDGE · FOLD ON THE DOTTED CREASES"
    )
    font = load_sans(19, bold=True)
    sheet.tracked(SHEET_W // 2, 8, slug, font, rgba(KRAFT_DARK, 255), 1.6)
    for panel, label in enumerate(panel_labels):
        sheet.tracked(panel_center(panel), SHEET_H - BLEED + 9, label, font, rgba(KRAFT_DARK, 255), 2.0)


# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the foldable grow kit user guide.")
    parser.add_argument(
        "--supersample",
        type=int,
        default=3,
        help="resolution multiplier for the vector layer (use 1 for quick drafts)",
    )
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    refresh_step_one_photo()
    refresh_foldable_photos()

    for name, builder in (("inside", build_inside), ("outside", build_outside)):
        sheet = builder(args.supersample)
        image = sheet.render()
        out = args.output_dir / f"grow-kit-user-guide-{name}.png"
        image.save(out, "PNG", optimize=True, dpi=(DPI, DPI))
        print(f"Created {out} ({image.width}x{image.height} px, {DPI} dpi)")


if __name__ == "__main__":
    main()
