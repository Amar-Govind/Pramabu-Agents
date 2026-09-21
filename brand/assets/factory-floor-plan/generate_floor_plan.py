#!/usr/bin/env python3
"""Generate Parambu Organics detailed factory floor plan (PNG + 2-page PDF)."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from typing import Literal

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[2]
OUTPUT_PNG = REPO_ROOT / "floor-plan.png"
OUTPUT_PDF = REPO_ROOT / "floor-plan.pdf"

BUILDING_EW = 36.0
BUILDING_NS = 70.0
WEST_W = 16.0
PATH_W = 4.0
EAST_W = 16.0
PANEL = 2.0 / 12.0

WEST_X = 0.0
PATH_X = WEST_W
EAST_X = WEST_W + PATH_W

# Colours
BG = (252, 250, 246)
WALL = (35, 35, 35)
PANEL_COLOR = (80, 80, 80)
PVC_COLOR = (160, 90, 170)
TEXT = (25, 45, 35)
DIM = (100, 100, 100)
ACCENT = (27, 67, 50)
GOLD = (180, 140, 100)
DOOR = (190, 70, 50)

ZONE_COLORS = {
    "pvc_store": (235, 225, 210),
    "production": (244, 236, 228),
    "open_packing": (240, 244, 228),
    "office_lab": (232, 236, 244),
    "finished": (228, 240, 228),
    "circulation": (235, 230, 220),
    "soap": (244, 232, 228),
}

PX_PER_FT = 22
MARGIN = 100
TITLE_H = 175


@dataclass(frozen=True)
class Zone:
    code: str
    title: str
    subtitle: str
    size: str
    area: str
    x: float
    y: float
    w: float
    h: float
    zone_type: str
    partition_north: Literal["exterior", "pvc", "panel", "none"] = "panel"
    equipment: tuple[str, ...] = field(default_factory=tuple)


def ft(v: float) -> float:
    return v * PX_PER_FT


def load_fonts() -> dict:
    bold_p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    reg_p = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    fallback = ImageFont.load_default()
    if not Path(bold_p).exists():
        return {k: fallback for k in ("title", "subtitle", "room", "equip", "tiny", "dim", "code")}
    return {
        "title": ImageFont.truetype(bold_p, 30),
        "subtitle": ImageFont.truetype(reg_p, 15),
        "room": ImageFont.truetype(bold_p, 13),
        "equip": ImageFont.truetype(reg_p, 10),
        "tiny": ImageFont.truetype(reg_p, 9),
        "dim": ImageFont.truetype(reg_p, 11),
        "code": ImageFont.truetype(bold_p, 14),
    }


def build_zones() -> list[Zone]:
    """Zones in building coordinates: x east, y north from south wall."""
    soap_h = 20.0 + 2.0 / 12.0
    pack_h = 33.0 + 8.0 / 12.0
    oil_h = 19.0 + 4.0 / 12.0

    y = 0.0
    w6 = Zone("W6", "OFFICE", "records · owner seat faces east", "10'-0\" × 16'-0\"", "160 sq ft",
              WEST_X, y, WEST_W, 10, "office_lab", "panel",
              ("DESK", "VISITOR", "RECORD CABINET"))
    y += 10 + PANEL
    w5 = Zone("W5", "QUALITY CONTROL LAB", "testing · retained samples", "10'-0\" × 16'-0\"", "160 sq ft",
              WEST_X, y, WEST_W, 10, "office_lab", "panel",
              ("LAB BENCH", "SINK & WASH", "INSTRUMENTS", "SAMPLE CUPBOARD"))
    y += 10 + PANEL
    w4 = Zone("W4", "OIL MAKING, STORAGE & FILLING", "press · 5 tanks · filling line",
              "19'-4\" × 16'-0\"", "309 sq ft", WEST_X, y, WEST_W, oil_h, "production", "panel",
              ("COLD PRESS", "FILTER PRESS", "COLLECTION TANK", "T1 T2 T3 T4 T5",
               "FILLING / CAPPING / LABELLING", "TRANSFER PUMP · SEED FEED · CAKE BIN"))
    y += oil_h + PANEL
    w3 = Zone("W3", "FACEPACK & POWDER MAKING", "mixer · mill · filling", "10'-0\" × 16'-0\"", "160 sq ft",
              WEST_X, y, WEST_W, 10, "production", "panel",
              ("MIXER", "POWDER MILL", "SIFTER", "FILLING / JARS"))
    y += 10 + PANEL
    w2 = Zone("W2", "PACKING ITEM STORE", "PVC screen · not a closed room", "10'-0\" × 16'-0\"", "160 sq ft",
              WEST_X, y, WEST_W, 10, "pvc_store", "pvc",
              ("BOTTLES", "CARTONS", "LABELS", "CAPS & LINERS"))
    y += 10
    w1 = Zone("W1", "RAW MATERIAL STORE", "PVC screen · not a closed room", "10'-0\" × 16'-0\"", "160 sq ft",
              WEST_X, y, WEST_W, 10, "pvc_store", "exterior",
              ("RACK", "RACK", "RACK", "WEIGHING"))

    es = Zone("E-S", "SOAP MAKING, CURING & PACKING", "mixer · racks · wrapping",
              "20'-2\" × 16'-0\"", "323 sq ft", EAST_X, 0, EAST_W, soap_h, "soap", "panel",
              ("MIXER / KETTLE", "MOULD TABLE", "CUTTER", "LYE MIXING (EXHAUST)",
               "CURING RACK", "CURING RACK", "CURING RACK", "SOAP WRAP / CARTONING"))
    em = Zone("E-M", "OPEN PACKING AREA", "oil / facepack / powder packing · open to path",
              "33'-8\" × 16'-0\"", "539 sq ft", EAST_X, soap_h + PANEL, EAST_W, pack_h, "open_packing", "pvc",
              ("PACKING TABLE", "PACKING TABLE", "CODING / SEAL / CARTONING",
               "STAGING · SHRINK · TAPE", "EMPTY CARTON HOLD"))
    en = Zone("E-N", "FINISHED PRODUCT STORE", "open packing bay · PVC screen south",
              "16'-0\" × 16'-0\"", "256 sq ft", EAST_X, soap_h + PANEL + pack_h, EAST_W, 16, "finished", "exterior",
              ("PALLET RACKS", "PALLET RACKS", "DISPATCH · HAND WASH"))

    return [w1, w2, w3, w4, w5, w6, en, em, es]


def to_screen(ox: float, oy: float, bx: float, by: float) -> tuple[float, float]:
    return ox + ft(bx), oy + ft(BUILDING_NS - by)


def zone_rect(ox: float, oy: float, z: Zone) -> tuple[float, float, float, float]:
    x1, y1 = to_screen(ox, oy, z.x, z.y + z.h)
    x2, y2 = to_screen(ox, oy, z.x + z.w, z.y)
    return x1, y1, x2, y2


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: float,
    y: float,
    max_w: float,
    font,
    fill: tuple[int, int, int],
    align: str = "center",
    line_gap: int = 2,
) -> float:
    words = text.replace(" · ", " · ").split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if draw.textlength(test, font=font) <= max_w:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    if not lines:
        lines = [text]
    lh = font.size + line_gap
    for i, line in enumerate(lines):
        tw = draw.textlength(line, font=font)
        tx = x - tw / 2 if align == "center" else x
        draw.text((tx, y + i * lh), line, fill=fill, font=font)
    return y + len(lines) * lh


def draw_equipment(draw: ImageDraw.ImageDraw, fonts: dict, ox: float, oy: float, z: Zone) -> None:
    x1, y1, x2, y2 = zone_rect(ox, oy, z)
    pad = 6
    inner_w = (x2 - x1) - pad * 2
    inner_h = (y2 - y1) - pad * 2 - 52
    if inner_h < 20:
        return
    items = list(z.equipment)
    cols = 2 if z.code in ("W4", "E-S", "E-M") else 1
    rows = math.ceil(len(items) / cols)
    cell_w = inner_w / cols
    cell_h = inner_h / max(rows, 1)
    font = fonts["equip"]
    for i, label in enumerate(items):
        col = i % cols
        row = i // cols
        cx = x1 + pad + col * cell_w + cell_w / 2
        cy = y1 + pad + 48 + row * cell_h + cell_h / 2
        bw = min(cell_w - 8, draw.textlength(label, font=font) + 12)
        bh = font.size + 10
        bx1, by1 = cx - bw / 2, cy - bh / 2
        draw.rounded_rectangle([bx1, by1, bx1 + bw, by1 + bh], radius=4,
                               fill=(255, 255, 255, 200), outline=(180, 175, 165), width=1)
        tw = draw.textlength(label, font=font)
        draw.text((cx - tw / 2, cy - font.size / 2 - 1), label, fill=(60, 60, 60), font=font)


def draw_pvc_screen(
    draw: ImageDraw.ImageDraw,
    p1: tuple[float, float],
    p2: tuple[float, float],
    label: str | None = None,
    fonts: dict | None = None,
) -> None:
    length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
    dashes = int(length / 14)
    for i in range(dashes):
        t0 = i / dashes
        t1 = (i + 0.55) / dashes
        if i % 2 == 0:
            x0 = p1[0] + (p2[0] - p1[0]) * t0
            y0 = p1[1] + (p2[1] - p1[1]) * t0
            x1 = p1[0] + (p2[0] - p1[0]) * t1
            y1 = p1[1] + (p2[1] - p1[1]) * t1
            draw.line([(x0, y0), (x1, y1)], fill=PVC_COLOR, width=3)
    if label and fonts:
        mx = (p1[0] + p2[0]) / 2
        my = (p1[1] + p2[1]) / 2
        draw.text((mx + 4, my - 8), label, fill=PVC_COLOR, font=fonts["tiny"])


def draw_panel(
    draw: ImageDraw.ImageDraw,
    fonts: dict,
    p1: tuple[float, float],
    p2: tuple[float, float],
) -> None:
    draw.line([p1, p2], fill=PANEL_COLOR, width=5)
    mx = (p1[0] + p2[0]) / 2
    my = (p1[1] + p2[1]) / 2
    draw.text((mx - 8, my - 16), '2"', fill=PANEL_COLOR, font=fonts["tiny"])


def draw_internal_door(
    draw: ImageDraw.ImageDraw,
    ox: float,
    oy: float,
    by: float,
    height: float = 3.5,
    width: float = 3.5,
) -> None:
    """3'-6\" door on west face of east-bay room or east face of west-bay room."""
    x, y = to_screen(ox, oy, PATH_X, by + height)
    w = ft(width)
    h = ft(0.3)
    draw.rectangle([x - 2, y, x + w, y + h], fill=BG)
    draw.arc([x, y - w * 0.8, x + w, y + w * 0.2], 180, 270, fill=DOOR, width=2)


def draw_rolling_shutter(
    draw: ImageDraw.ImageDraw,
    ox: float,
    oy: float,
    by: float,
    label: str,
    fonts: dict,
    width: float = 7.0,
) -> None:
    x, y = to_screen(ox, oy, BUILDING_EW, by + width)
    w = ft(width)
    draw.rectangle([x - 5, y, x + 5, y + w], fill=(220, 220, 215), outline=DOOR, width=3)
    for i in range(5):
        draw.line([(x - 4, y + i * w / 5), (x + 4, y + i * w / 5)], fill=(160, 160, 155), width=1)
    draw.text((x + 10, y + 4), label, fill=DOOR, font=fonts["tiny"])
    draw.text((x + 10, y + 16), "FACING EAST", fill=DOOR, font=fonts["tiny"])


def draw_dimension_chain(
    draw: ImageDraw.ImageDraw,
    fonts: dict,
    ox: float,
    oy: float,
    segments: list[tuple[float, str]],
    axis: str,
    pos: float,
    offset: float,
) -> None:
    """Draw chained dimensions. segments = [(length_ft, label), ...]."""
    cursor = 0.0
    coords: list[tuple[float, float, str]] = []
    for length, label in segments:
        coords.append((cursor, cursor + length, label))
        cursor += length
    if axis == "v":
        base_x = ox - offset
        for y0, y1, label in coords:
            sy0 = oy + ft(BUILDING_NS - y1)
            sy1 = oy + ft(BUILDING_NS - y0)
            draw.line([(base_x, sy0), (base_x, sy1)], fill=DIM, width=1)
            draw.line([(base_x - 5, sy0), (base_x + 5, sy0)], fill=DIM, width=1)
            draw.line([(base_x - 5, sy1), (base_x + 5, sy1)], fill=DIM, width=1)
            my = (sy0 + sy1) / 2
            draw.text((base_x - 46, my - 6), label, fill=DIM, font=fonts["tiny"])
    else:
        base_y = oy + ft(BUILDING_NS) + offset
        for x0, x1, label in coords:
            sx0 = ox + ft(x0)
            sx1 = ox + ft(x1)
            draw.line([(sx0, base_y), (sx1, base_y)], fill=DIM, width=1)
            draw.line([(sx0, base_y - 5), (sx0, base_y + 5)], fill=DIM, width=1)
            draw.line([(sx1, base_y - 5), (sx1, base_y + 5)], fill=DIM, width=1)
            mx = (sx0 + sx1) / 2
            tw = draw.textlength(label, font=fonts["tiny"])
            draw.text((mx - tw / 2, base_y + 6), label, fill=DIM, font=fonts["tiny"])


def render_floor_plan_page() -> Image.Image:
    fonts = load_fonts()
    zones = build_zones()
    plan_w = int(ft(BUILDING_EW))
    plan_h = int(ft(BUILDING_NS))
    notes_w = 420
    img_w = plan_w + MARGIN * 2 + notes_w
    img_h = plan_h + MARGIN * 2 + TITLE_H + 80
    img = Image.new("RGB", (img_w, img_h), BG)
    draw = ImageDraw.Draw(img)

    ox = MARGIN
    oy = MARGIN + TITLE_H

    # Title
    draw.text((ox, 24), "PARAMBU — SOAP, OIL, FACEPACK & POWDER", fill=ACCENT, font=fonts["title"])
    draw.text(
        (ox, 62),
        "FLOOR PLAN  36'-0\" × 70'-0\" = 2,520 SQ FT  ·  EAST FACING",
        fill=TEXT,
        font=fonts["subtitle"],
    )
    draw.text(
        (ox, 84),
        "W1/W2 and east packing bay are PVC-screened · 4'-0\" central path · 2\" panels at closed rooms · no false ceiling",
        fill=DIM,
        font=fonts["tiny"],
    )
    draw.line([(ox, 108), (img_w - MARGIN, 108)], fill=GOLD, width=2)

    shell = [ox, oy, ox + plan_w, oy + plan_h]
    draw.rectangle(shell, fill=ZONE_COLORS["circulation"], outline=WALL, width=4)

    # Central path full height
    path_box = [ox + ft(PATH_X), oy, ox + ft(PATH_X + PATH_W), oy + plan_h]
    draw.rectangle(path_box, fill=ZONE_COLORS["circulation"], outline=None)
    pcx = ox + ft(PATH_X + PATH_W / 2)
    for i, line in enumerate(["CENTRAL", "PATH", "4'-0\"", "× 70'-0\""]):
        tw = draw.textlength(line, font=fonts["dim"])
        draw.text((pcx - tw / 2, oy + plan_h / 2 - 40 + i * 16), line, fill=DIM, font=fonts["dim"])

    # Zone fills
    for z in zones:
        x1, y1, x2, y2 = zone_rect(ox, oy, z)
        draw.rectangle([x1, y1, x2, y2], fill=ZONE_COLORS[z.zone_type], outline=None)

    # 2" panels west bay (between W6/W5, W5/W4, W4/W3, W3/W2)
    panel_ys = [10, 20.167, 39.833, 49.833]
    for py in panel_ys:
        p1 = to_screen(ox, oy, WEST_X, py)
        p2 = to_screen(ox, oy, WEST_X + WEST_W, py)
        draw_panel(draw, fonts, p1, p2)

    # East panel between soap and packing
    soap_h = 20 + 2 / 12
    py = soap_h
    p1 = to_screen(ox, oy, EAST_X, py)
    p2 = to_screen(ox, oy, EAST_X + EAST_W, py)
    draw_panel(draw, fonts, p1, p2)

    # PVC screen W1/W2
    p1 = to_screen(ox, oy, WEST_X, 60)
    p2 = to_screen(ox, oy, WEST_X + WEST_W, 60)
    draw_pvc_screen(draw, p1, p2, "PVC", fonts)

    # PVC screen W1/W2 opening to path
    p1 = to_screen(ox, oy, WEST_X + WEST_W, 50)
    p2 = to_screen(ox, oy, PATH_X, 60)
    draw_pvc_screen(draw, p1, p2, None, fonts)
    p1 = to_screen(ox, oy, WEST_X + WEST_W, 60)
    p2 = to_screen(ox, oy, PATH_X, 70)
    draw_pvc_screen(draw, p1, p2, None, fonts)

    # PVC screen E-N / E-M
    pack_top = soap_h + PANEL + (33 + 8 / 12)
    p1 = to_screen(ox, oy, EAST_X, pack_top)
    p2 = to_screen(ox, oy, EAST_X + EAST_W, pack_top)
    draw_pvc_screen(draw, p1, p2, "PVC SCREEN", fonts)

    # Path boundary lines
    draw.line([to_screen(ox, oy, PATH_X, 0), to_screen(ox, oy, PATH_X, BUILDING_NS)], fill=WALL, width=2)
    draw.line([to_screen(ox, oy, PATH_X + PATH_W, 0), to_screen(ox, oy, PATH_X + PATH_W, BUILDING_NS)],
              fill=WALL, width=2)

    draw.rectangle(shell, outline=WALL, width=4)

    # Zone labels
    for z in zones:
        x1, y1, x2, y2 = zone_rect(ox, oy, z)
        cx = (x1 + x2) / 2
        cy = y1 + 14
        tw = draw.textlength(z.code, font=fonts["code"])
        draw.text((cx - tw / 2, cy), z.code, fill=ACCENT, font=fonts["code"])
        cy += 18
        for line in z.title.split(" & "):
            tw = draw.textlength(line, font=fonts["room"])
            draw.text((cx - tw / 2, cy), line, fill=TEXT, font=fonts["room"])
            cy += 15
        cy += 2
        draw_wrapped(draw, z.subtitle, cx, cy, x2 - x1 - 10, fonts["tiny"], DIM)
        cy = y2 - 28
        draw.text((cx - draw.textlength(z.size, font=fonts["tiny"]) / 2, cy), z.size, fill=DIM, font=fonts["tiny"])
        draw.text((cx - draw.textlength(z.area, font=fonts["tiny"]) / 2, cy + 12), z.area, fill=DIM, font=fonts["tiny"])

    # Equipment
    for z in zones:
        draw_equipment(draw, fonts, ox, oy, z)

    # Doors on closed rooms (W3–W6, E-S)
    closed = [z for z in zones if z.code in ("W3", "W4", "W5", "W6", "E-S")]
    for z in closed:
        draw_internal_door(draw, ox, oy, z.y + z.h / 2 - 1.75)
    draw_rolling_shutter(draw, ox, oy, 61, "D1 · 7'-0\"", fonts)
    draw_rolling_shutter(draw, ox, oy, 33, "D2 · 7'-0\"", fonts)

    # Exterior dimensions
    draw.text((ox + plan_w / 2 - 30, oy - 28), "36'-0\"", fill=DIM, font=fonts["dim"])
    draw.text((ox - 58, oy + plan_h / 2), "70'-0\"", fill=DIM, font=fonts["dim"])
    draw.text((ox + plan_w / 2 - 50, oy + plan_h + 14), "WEST ←──→ EAST", fill=DIM, font=fonts["dim"])
    draw.text((ox - 90, oy + plan_h / 2 - 30), "NORTH ↓ SOUTH", fill=DIM, font=fonts["dim"])

    # West dimension chain (south to north: W6 → W1)
    west_segments = [
        (10, "10'-0\""), (PANEL, "2\""), (10, "10'-0\""), (PANEL, "2\""),
        (19 + 4 / 12, "19'-4\""), (PANEL, "2\""), (10, "10'-0\""), (PANEL, "2\""),
        (10, "10'-0\""), (10, "10'-0\""),
    ]
    draw_dimension_chain(draw, fonts, ox, oy, west_segments, "v", 0, 48)

    # East dimension chain
    east_segments = [
        (16, "16'-0\""), (33 + 8 / 12, "33'-8\""), (PANEL, "2\""), (20 + 2 / 12, "20'-2\""),
    ]
    draw_dimension_chain(draw, fonts, ox, oy, east_segments, "v", BUILDING_EW, -42)

    # Bay labels
    draw.text((ox + ft(8) - 20, oy + plan_h + 36), "16'-0\" WEST BAY", fill=DIM, font=fonts["tiny"])
    draw.text((ox + ft(18) - 14, oy + plan_h + 36), "4'-0\" PATH", fill=DIM, font=fonts["tiny"])
    draw.text((ox + ft(28) - 18, oy + plan_h + 36), "16'-0\" EAST BAY", fill=DIM, font=fonts["tiny"])

    # East-bay zone tags (like reference drawing)
    draw.text((ox + ft(EAST_X + 4), oy + ft(6)), "SOAP", fill=DIM, font=fonts["dim"])
    draw.text((ox + ft(EAST_X + 2), oy + ft(38)), "MID GODOWN", fill=DIM, font=fonts["dim"])
    draw.text((ox + ft(EAST_X + 1), oy + ft(38) + 14), "PACKING", fill=DIM, font=fonts["dim"])
    draw.text((ox + ft(EAST_X + 2), oy + ft(62)), "FG STORE", fill=DIM, font=fonts["dim"])

    # North arrow
    nx = ox + plan_w + 30
    ny = oy - 10
    draw.polygon([(nx, ny - 36), (nx - 14, ny + 6), (nx + 14, ny + 6)], fill=ACCENT)
    draw.text((nx - 5, ny - 56), "N", fill=ACCENT, font=fonts["code"])

    # Legend
    lx = ox + plan_w + 36
    ly = oy + 10
    draw.text((lx, ly), "LEGEND", fill=ACCENT, font=fonts["room"])
    legend_items = [
        ("pvc_store", "PVC-screened store"),
        ("production", "Production"),
        ("open_packing", "Open packing"),
        ("office_lab", "Office & lab"),
        ("finished", "Finished goods"),
        ("circulation", "Circulation"),
    ]
    for i, (key, label) in enumerate(legend_items):
        y = ly + 22 + i * 22
        draw.rectangle([lx, y, lx + 18, y + 14], fill=ZONE_COLORS[key], outline=WALL)
        draw.text((lx + 26, y - 1), label, fill=TEXT, font=fonts["tiny"])
    sym_y = ly + 22 + len(legend_items) * 22 + 8
    draw.line([(lx, sym_y), (lx + 18, sym_y)], fill=DOOR, width=2)
    draw.text((lx + 26, sym_y - 6), "Internal door 3'-6\"", fill=TEXT, font=fonts["tiny"])
    draw.rectangle([lx, sym_y + 18, lx + 18, sym_y + 32], fill=(220, 220, 215), outline=DOOR)
    draw.text((lx + 26, sym_y + 14), "East door 7'-0\"", fill=TEXT, font=fonts["tiny"])
    draw_pvc_screen(draw, (lx, sym_y + 42), (lx + 18, sym_y + 42), None, fonts)
    draw.text((lx + 26, sym_y + 36), "PVC screen", fill=TEXT, font=fonts["tiny"])
    draw.line([(lx, sym_y + 58), (lx + 18, sym_y + 58)], fill=PANEL_COLOR, width=4)
    draw.text((lx + 26, sym_y + 52), "2\" closed-room panel", fill=TEXT, font=fonts["tiny"])

    # Construction notes
    ny0 = ly + 200
    draw.text((lx, ny0), "CONSTRUCTION NOTES", fill=ACCENT, font=fonts["room"])
    notes = [
        "1. Closed rooms (W3–W6, soap) use 2\" (50 mm) panels.",
        "2. W1/W2 and east packing bay are PVC-screened, not closed.",
        "3. 16' west + 4' path + 16' east = 36'. Every bay 16' deep.",
        "4. W4: oil press, 5 tanks, filling — 309 sq ft (28.7 m²).",
        "5. E-S soap: make, cure & pack together — 323 sq ft.",
        "6. D1/D2: 7'-0\" rolling shutters facing east.",
        "7. Floor: PVC mat wood finish. No false ceiling; 12' clear.",
        "8. Toilet block detached, 25' clear of north wall.",
    ]
    for i, note in enumerate(notes):
        draw.text((lx, ny0 + 20 + i * 15), note, fill=TEXT, font=fonts["tiny"])

    # Scale
    draw.rectangle([ox, oy + plan_h + 52, ox + ft(10), oy + plan_h + 62], fill=ACCENT)
    draw.text((ox, oy + plan_h + 66), "10'-0\"", fill=TEXT, font=fonts["tiny"])

    return img


def save_png(img: Image.Image, path: Path) -> None:
    img.save(path, "PNG", dpi=(200, 200))


def build_page2_pdf(c: canvas.Canvas, page_w: float, page_h: float) -> None:
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", parent=styles["Heading1"], fontSize=14,
                                 textColor=colors.HexColor("#1B4332"), spaceAfter=8)
    sub_style = ParagraphStyle("sub", parent=styles["Normal"], fontSize=9, textColor=colors.grey)

    y = page_h - 0.55 * inch
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#1B4332"))
    c.drawString(0.55 * inch, y, "PARAMBU — SOAP, OIL, FACEPACK & POWDER")
    y -= 16
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.grey)
    c.drawString(0.55 * inch, y, "ROOM SCHEDULE, PROCESS FLOW & NOTES  ·  36'-0\" × 70'-0\" = 2,520 sq ft")
    y -= 22

    schedule_data = [
        ["CODE", "ROOM", "SIZE", "AREA", "ZONE", "NOTES"],
        ["W1", "Raw material store", "10'-0\" × 16'-0\"", "160 sq ft", "North-west", "PVC screen, not closed"],
        ["W2", "Packing item store", "10'-0\" × 16'-0\"", "160 sq ft", "North-west", "PVC screen, not closed"],
        ["W3", "Facepack & powder making", "10'-0\" × 16'-0\"", "160 sq ft", "West", "Mixer, mill, sifter, jar filling"],
        ["W4", "Oil making, storage & filling", "19'-4\" × 16'-0\"", "309 sq ft", "West / SW", "Cold press, 5 tanks, filling line"],
        ["W5", "Quality control lab", "10'-0\" × 16'-0\"", "160 sq ft", "South-west", "Bench, sink, retained samples"],
        ["W6", "Office", "10'-0\" × 16'-0\"", "160 sq ft", "South-west", "Records; owner seated facing east"],
        ["E-N", "Finished product store", "16'-0\" × 16'-0\"", "256 sq ft", "North-east", "Open bay, PVC screen to packing"],
        ["E-M", "Open packing area", "33'-8\" × 16'-0\"", "539 sq ft", "East", "Open to path; oil/facepack/powder pack"],
        ["E-S", "Soap making, curing & packing", "20'-2\" × 16'-0\"", "323 sq ft", "South-east", "Mixer, curing racks, wrapping"],
        ["P1", "Central path", "4'-0\" × 70'-0\"", "280 sq ft", "Centre", "Serves every bay"],
    ]
    table = Table(schedule_data, colWidths=[0.45 * inch, 1.55 * inch, 0.95 * inch, 0.65 * inch, 0.75 * inch, 2.1 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B4332")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F1E4")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    tw, th = table.wrapOn(c, page_w - 1.1 * inch, page_h)
    table.drawOn(c, 0.55 * inch, y - th)
    y = y - th - 14

    c.setFont("Helvetica-Oblique", 8)
    c.drawString(0.55 * inch, y, "Working bays = 2,227 sq ft · path = 280 sq ft · 2\" panels = 13 sq ft · built-up = 2,520 sq ft")
    y -= 20

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#1B4332"))
    c.drawString(0.55 * inch, y, "PROCESS FLOW")
    y -= 14
    flows = [
        "OIL:  W1 raw material → W4 make/tanks/fill → E-M open packing → E-N finished goods → D1/D2 dispatch",
        "PACK: W1 raw material → W3 facepack & powder → E-M open packing → E-N finished goods → D1/D2 dispatch",
        "SOAP: W1 raw material → E-S soap make/cure/pack → E-N finished goods → D1/D2 dispatch",
    ]
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.black)
    for line in flows:
        c.drawString(0.55 * inch, y, line)
        y -= 12

    y -= 6
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#1B4332"))
    c.drawString(0.55 * inch, y, "VASTU — PLACEMENT")
    y -= 14
    vastu = [
        "Office in south-west (W6), owner seated facing east.",
        "Soap making in south-east (E-S), Agni corner, with curing and packing in same room.",
        "Oil plant in W4 (west/south-west) — right side for heavy machinery.",
        "Finished goods in north-east (E-N), next to D1 for east dispatch without crossing production.",
        "W1/W2 open PVC bays north-west for raw material and packing items.",
        "QC lab in W5 next to office. 4'-0\" central path keeps centre free of machines.",
    ]
    c.setFont("Helvetica", 8)
    for line in vastu:
        c.drawString(0.55 * inch, y, f"• {line}")
        y -= 11

    y -= 6
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.55 * inch, y, "DOOR, SCREEN & FINISH SCHEDULE")
    y -= 14
    door_data = [
        ["MARK", "SIZE / TYPE", "LOCATION", "REMARKS"],
        ["D1", "7'-0\" rolling shutter", "East wall, finished-goods bay", "Main entry, facing east, north-east"],
        ["D2", "7'-0\" rolling shutter", "East wall, open packing (mid-godown)", "Second east door, facing east"],
        ["W3–W6, E-S", "3'-6\" × 7'-0\" flush", "Each closed room to path", "Opens into room, not into path"],
        ["W1 / W2", "PVC strip curtain", "Full opening onto central path", "Not closed; PVC between W1 and W2"],
        ["E-N / E-M", "PVC screen", "Between finished goods and packing", "Open packing bay, no masonry"],
        ["Floor", "PVC mat, wood finish", "Entire 36' × 70' shed", "No tiles / no epoxy"],
        ["Ceiling", "None — no false ceiling", "Entire shed", "Exposed roof; 12'-0\" clear to purlins"],
    ]
    dtable = Table(door_data, colWidths=[0.7 * inch, 1.2 * inch, 1.6 * inch, 2.8 * inch])
    dtable.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B4332")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F1E4")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
    ]))
    dtw, dth = dtable.wrapOn(c, page_w - 1.1 * inch, page_h)
    dtable.drawOn(c, 0.55 * inch, y - dth)

    c.setFont("Helvetica-Oblique", 7)
    c.drawString(
        0.55 * inch, 0.45 * inch,
        "Dimension check: west 10+10+10+19'-4\"+10+10+four 2\" panels=70'-0\"  |  "
        "east 16'+33'-8\"+2\"+20'-2\"=70'-0\"  |  across 16'+4'+16'=36'-0\"",
    )


def save_pdf(page1: Image.Image, path: Path) -> None:
    page_w, page_h = landscape(letter)
    c = canvas.Canvas(str(path), pagesize=landscape(letter))

    # Page 1 — floor plan
    buf = BytesIO()
    page1.save(buf, format="PNG", dpi=(200, 200))
    buf.seek(0)
    img_w, img_h = page1.size
    scale = min((page_w - 28) / img_w, (page_h - 28) / img_h)
    draw_w = img_w * scale
    draw_h = img_h * scale
    c.drawImage(ImageReader(buf), (page_w - draw_w) / 2, (page_h - draw_h) / 2,
                width=draw_w, height=draw_h)
    c.showPage()

    # Page 2 — schedule & notes
    build_page2_pdf(c, page_w, page_h)
    c.showPage()

    c.setAuthor("Parambu Organics")
    c.setTitle("Parambu Organics Factory Floor Plan — Complete")
    c.save()


def main() -> None:
    page1 = render_floor_plan_page()
    save_png(page1, OUTPUT_PNG)
    save_pdf(page1, OUTPUT_PDF)
    print(f"Wrote {OUTPUT_PNG}")
    print(f"Wrote {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
