#!/usr/bin/env python3
"""Generate Parambu Organics detailed factory floor plan (PNG + 2-page PDF)."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

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

OIL_H = 20.0 + 2.0 / 12.0       # E-S oil making 20'-2"
FACEPACK_H = 10.0
PACKING_H = 16.0
OPEN_H = 10.0                     # open area after 7' east door

# North strip starts after east-bay stack below
EAST_STACK_S = OIL_H + PANEL + FACEPACK_H + PANEL + PACKING_H + PANEL + OPEN_H
NORTH_STRIP_H = BUILDING_NS - EAST_STACK_S
NORTH_STRIP_Y = EAST_STACK_S
MEN_CHANGE_W = 6.0
MEN_CHANGE_H = 8.0
RAW_JOIN_W = 30.0                 # raw material spans west + east, joins soap (no path)

OFFICE_H = 10.0
QC_H = 10.0
SOAP_H = BUILDING_NS - (OFFICE_H + PANEL + QC_H + PANEL)  # joined W1–W4

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
    "open_dock": (228, 240, 232),
    "circulation": (235, 230, 220),
    "soap": (244, 232, 228),
    "oil": (236, 244, 236),
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
    equipment: tuple[str, ...] = field(default_factory=tuple)
    span_path: bool = False


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
    """Building coords: x east from west wall, y north from south wall."""
    y = 0.0
    w6 = Zone(
        "W6", "OFFICE", "records · owner seat faces east", "10'-0\" × 16'-0\"", "160 sq ft",
        WEST_X, y, WEST_W, OFFICE_H, "office_lab", ("DESK", "VISITOR", "RECORD CABINET"),
    )
    y += OFFICE_H + PANEL
    w5 = Zone(
        "W5", "QUALITY CONTROL LAB", "testing · retained samples", "10'-0\" × 16'-0\"", "160 sq ft",
        WEST_X, y, WEST_W, QC_H, "office_lab", ("LAB BENCH", "SINK & WASH", "INSTRUMENTS", "SAMPLE CUPBOARD"),
    )
    y += QC_H + PANEL
    soap = Zone(
        "W-SOAP",
        "SOAP MAKING, CURING & PACKING",
        "W1+W2+W3+W4 joined · mixer · racks · wrapping",
        f"{_fmt_ft(SOAP_H)} × 16'-0\"",
        f"{int(SOAP_H * 16)} sq ft",
        WEST_X, y, WEST_W, SOAP_H, "soap",
        ("MIXER / KETTLE", "MOULD TABLE", "CUTTER", "LYE MIXING (EXHAUST)",
         "CURING RACK", "CURING RACK", "CURING RACK", "SOAP WRAP / CARTONING"),
    )

    es = Zone(
        "E-S", "OIL MAKING, STORAGE & FILLING", "press · 5 tanks · filling line",
        "20'-2\" × 16'-0\"", "323 sq ft", EAST_X, 0, EAST_W, OIL_H, "oil",
        ("COLD PRESS", "FILTER PRESS", "COLLECTION TANK", "T1 T2 T3 T4 T5",
         "FILLING / CAPPING / LABELLING", "TRANSFER PUMP · SEED FEED · CAKE BIN"),
    )
    y_e = OIL_H + PANEL
    e_face = Zone(
        "E-FP", "FACEPACK & POWDER MAKING", "mixer · mill · filling",
        "10'-0\" × 16'-0\"", "160 sq ft", EAST_X, y_e, EAST_W, FACEPACK_H, "production",
        ("MIXER", "POWDER MILL", "SIFTER", "FILLING / JARS"),
    )
    y_e += FACEPACK_H + PANEL
    e_pack = Zone(
        "E-PK", "PACKING", "cartoning · sealing · staging",
        "16'-0\" × 16'-0\"", "256 sq ft", EAST_X, y_e, EAST_W, PACKING_H, "open_packing",
        ("PACKING TABLE", "PACKING TABLE", "CODING / SEAL / CARTONING", "STAGING · SHRINK · TAPE"),
    )
    y_e += PACKING_H + PANEL
    e_open = Zone(
        "E-OPEN", "OPEN DOCK / STAGING", "10' open after 7' east entry door",
        "10'-0\" × 16'-0\"", "160 sq ft", EAST_X, y_e, EAST_W, OPEN_H, "open_dock",
        ("EMPTY CARTON HOLD", "PALLET STAGING", "DISPATCH PREP"),
    )

    raw = Zone(
        "E-N-RM", "RAW MATERIAL STORE", "joins soap north · 6' north entry door",
        f"{_fmt_ft(RAW_JOIN_W)} × {_fmt_ft(NORTH_STRIP_H)}",
        f"{int(RAW_JOIN_W * NORTH_STRIP_H)} sq ft",
        0, NORTH_STRIP_Y, RAW_JOIN_W, NORTH_STRIP_H, "pvc_store",
        ("RACK", "RACK", "RACK", "WEIGHING"), span_path=True,
    )
    men = Zone(
        "E-N-MC", "MEN CHANGE & SAFETY", "3' north entry door · safety kit",
        "6'-0\" × 8'-0\"", "48 sq ft",
        BUILDING_EW - MEN_CHANGE_W, BUILDING_NS - MEN_CHANGE_H, MEN_CHANGE_W, MEN_CHANGE_H,
        "office_lab", ("LOCKERS", "SAFETY KIT", "MIRROR", "BENCH"),
    )

    return [w6, w5, soap, es, e_face, e_pack, e_open, raw, men]


def _fmt_ft(v: float) -> str:
    feet = int(v)
    inches = round((v - feet) * 12)
    if inches == 0:
        return f"{feet}'-0\""
    return f"{feet}'-{inches}\""


def to_screen(ox: float, oy: float, bx: float, by: float) -> tuple[float, float]:
    return ox + ft(bx), oy + ft(BUILDING_NS - by)


def zone_rect(ox: float, oy: float, z: Zone) -> tuple[float, float, float, float]:
    x1, y1 = to_screen(ox, oy, z.x, z.y + z.h)
    x2, y2 = to_screen(ox, oy, z.x + z.w, z.y)
    return x1, y1, x2, y2


def draw_wrapped(draw, text, x, y, max_w, font, fill, align="center", line_gap=2) -> float:
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


def draw_equipment(draw, fonts, ox, oy, z: Zone) -> None:
    x1, y1, x2, y2 = zone_rect(ox, oy, z)
    pad = 6
    inner_w = (x2 - x1) - pad * 2
    inner_h = (y2 - y1) - pad * 2 - 52
    if inner_h < 20 or inner_w < 20:
        return
    items = list(z.equipment)
    cols = 2 if len(items) > 4 else 1
    rows = math.ceil(len(items) / cols)
    cell_w = inner_w / cols
    cell_h = inner_h / max(rows, 1)
    font = fonts["equip"]
    for i, label in enumerate(items):
        col, row = i % cols, i // cols
        cx = x1 + pad + col * cell_w + cell_w / 2
        cy = y1 + pad + 48 + row * cell_h + cell_h / 2
        bw = min(cell_w - 8, draw.textlength(label, font=font) + 12)
        bh = font.size + 10
        bx1, by1 = cx - bw / 2, cy - bh / 2
        draw.rounded_rectangle([bx1, by1, bx1 + bw, by1 + bh], radius=4,
                               fill=(255, 255, 255), outline=(180, 175, 165), width=1)
        tw = draw.textlength(label, font=font)
        draw.text((cx - tw / 2, cy - font.size / 2 - 1), label, fill=(60, 60, 60), font=font)


def draw_pvc_screen(draw, p1, p2, label=None, fonts=None) -> None:
    length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
    dashes = max(int(length / 14), 1)
    for i in range(dashes):
        if i % 2 == 0:
            t0, t1 = i / dashes, (i + 0.55) / dashes
            draw.line([
                (p1[0] + (p2[0] - p1[0]) * t0, p1[1] + (p2[1] - p1[1]) * t0),
                (p1[0] + (p2[0] - p1[0]) * t1, p1[1] + (p2[1] - p1[1]) * t1),
            ], fill=PVC_COLOR, width=3)
    if label and fonts:
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        draw.text((mx + 4, my - 8), label, fill=PVC_COLOR, font=fonts["tiny"])


def draw_panel(draw, fonts, p1, p2) -> None:
    draw.line([p1, p2], fill=PANEL_COLOR, width=5)
    mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    draw.text((mx - 8, my - 16), '2"', fill=PANEL_COLOR, font=fonts["tiny"])


def draw_door_on_path(draw, ox, oy, by, width, label=None, fonts=None) -> None:
    """Door on partition between bay and central path."""
    x, y = to_screen(ox, oy, PATH_X, by + width)
    w = ft(width)
    draw.rectangle([x - 2, y, x + w, y + ft(0.3)], fill=BG)
    draw.arc([x, y - w * 0.8, x + w, y + w * 0.2], 180, 270, fill=DOOR, width=2)
    if label and fonts:
        draw.text((x + w + 4, y), label, fill=DOOR, font=fonts["tiny"])


def draw_internal_door(draw, ox, oy, by, width=3.5) -> None:
    x, y = to_screen(ox, oy, PATH_X, by + width)
    w = ft(width)
    draw.rectangle([x - 2, y, x + w, y + ft(0.3)], fill=BG)
    draw.arc([x, y - w * 0.8, x + w, y + w * 0.2], 180, 270, fill=DOOR, width=2)


def draw_rolling_shutter(draw, ox, oy, by, label, fonts, width=7.0) -> None:
    x, y = to_screen(ox, oy, BUILDING_EW, by + width)
    w = ft(width)
    draw.rectangle([x - 5, y, x + 5, y + w], fill=(220, 220, 215), outline=DOOR, width=3)
    for i in range(5):
        draw.line([(x - 4, y + i * w / 5), (x + 4, y + i * w / 5)], fill=(160, 160, 155), width=1)
    draw.text((x + 10, y + 4), label, fill=DOOR, font=fonts["tiny"])
    draw.text((x + 10, y + 16), "FACING EAST", fill=DOOR, font=fonts["tiny"])


def draw_north_door(draw, ox, oy, bx, width, label, fonts) -> None:
    x, y = to_screen(ox, oy, bx, BUILDING_NS)
    w = ft(width)
    draw.rectangle([x, y - 5, x + w, y + 5], fill=BG)
    draw.arc([x, y, x + w, y + w], 180, 270, fill=DOOR, width=2)
    draw.text((x, y + 8), label, fill=DOOR, font=fonts["tiny"])


def draw_dimension_chain(draw, fonts, ox, oy, segments, axis, offset) -> None:
    cursor = 0.0
    coords = []
    for length, label in segments:
        coords.append((cursor, cursor + length, label))
        cursor += length
    if axis == "v":
        base_x = ox - offset
        for y0, y1, label in coords:
            sy0, sy1 = oy + ft(BUILDING_NS - y1), oy + ft(BUILDING_NS - y0)
            draw.line([(base_x, sy0), (base_x, sy1)], fill=DIM, width=1)
            draw.line([(base_x - 5, sy0), (base_x + 5, sy0)], fill=DIM, width=1)
            draw.line([(base_x - 5, sy1), (base_x + 5, sy1)], fill=DIM, width=1)
            draw.text((base_x - 46, (sy0 + sy1) / 2 - 6), label, fill=DIM, font=fonts["tiny"])
    else:
        base_y = oy + ft(BUILDING_NS) + offset
        for x0, x1, label in coords:
            sx0, sx1 = ox + ft(x0), ox + ft(x1)
            draw.line([(sx0, base_y), (sx1, base_y)], fill=DIM, width=1)
            tw = draw.textlength(label, font=fonts["tiny"])
            draw.text(((sx0 + sx1) / 2 - tw / 2, base_y + 6), label, fill=DIM, font=fonts["tiny"])


def render_floor_plan_page() -> Image.Image:
    fonts = load_fonts()
    zones = build_zones()
    plan_w, plan_h = int(ft(BUILDING_EW)), int(ft(BUILDING_NS))
    notes_w = 420
    img_w = plan_w + MARGIN * 2 + notes_w
    img_h = plan_h + MARGIN * 2 + TITLE_H + 80
    img = Image.new("RGB", (img_w, img_h), BG)
    draw = ImageDraw.Draw(img)
    ox, oy = MARGIN, MARGIN + TITLE_H

    draw.text((ox, 24), "PARAMBU — SOAP, OIL, FACEPACK & POWDER", fill=ACCENT, font=fonts["title"])
    draw.text((ox, 62), "FLOOR PLAN  36'-0\" × 70'-0\" = 2,520 SQ FT  ·  EAST FACING", fill=TEXT, font=fonts["subtitle"])
    draw.text(
        (ox, 84),
        "W1–W4 joined soap west · E-S oil · north strip joins raw material to soap (no 4' path) · 2\" panels",
        fill=DIM, font=fonts["tiny"],
    )
    draw.line([(ox, 108), (img_w - MARGIN, 108)], fill=GOLD, width=2)

    shell = [ox, oy, ox + plan_w, oy + plan_h]
    draw.rectangle(shell, fill=ZONE_COLORS["circulation"], outline=WALL, width=4)

    # Central path — stops at north strip (no path through north)
    path_box = [ox + ft(PATH_X), oy + ft(BUILDING_NS - NORTH_STRIP_Y),
                ox + ft(PATH_X + PATH_W), oy + plan_h]
    draw.rectangle(path_box, fill=ZONE_COLORS["circulation"], outline=None)
    pcx = ox + ft(PATH_X + PATH_W / 2)
    path_mid_y = oy + ft(BUILDING_NS - NORTH_STRIP_Y / 2)
    for i, line in enumerate(["CENTRAL", "PATH", "4'-0\""]):
        tw = draw.textlength(line, font=fonts["dim"])
        draw.text((pcx - tw / 2, path_mid_y - 20 + i * 16), line, fill=DIM, font=fonts["dim"])

    # Zone fills
    for z in zones:
        x1, y1, x2, y2 = zone_rect(ox, oy, z)
        draw.rectangle([x1, y1, x2, y2], fill=ZONE_COLORS[z.zone_type], outline=None)

    # Panels: W6/W5, W5/soap, oil/facepack, facepack/packing, packing/open
    for py in [OFFICE_H, OFFICE_H + PANEL + QC_H]:
        draw_panel(draw, fonts, to_screen(ox, oy, WEST_X, py), to_screen(ox, oy, WEST_X + WEST_W, py))
    for py in [OIL_H, OIL_H + PANEL + FACEPACK_H, OIL_H + PANEL + FACEPACK_H + PANEL + PACKING_H]:
        draw_panel(draw, fonts, to_screen(ox, oy, EAST_X, py), to_screen(ox, oy, BUILDING_EW, py))

    # Partition between raw material and men change in north strip
    div_x = BUILDING_EW - MEN_CHANGE_W
    p1 = to_screen(ox, oy, div_x, BUILDING_NS - MEN_CHANGE_H)
    p2 = to_screen(ox, oy, div_x, BUILDING_NS)
    draw_panel(draw, fonts, p1, p2)

    # Raw material joins soap — no path barrier at north interface
    join_y = NORTH_STRIP_Y
    p1 = to_screen(ox, oy, 0, join_y)
    p2 = to_screen(ox, oy, RAW_JOIN_W, join_y)
    draw.line([p1, p2], fill=ACCENT, width=2)
    mx = (p1[0] + p2[0]) / 2
    draw.text((mx - 60, p1[1] + 4), "JOINED — NO 4' PATH", fill=ACCENT, font=fonts["tiny"])

    # Path boundaries (south section only)
    draw.line([to_screen(ox, oy, PATH_X, 0), to_screen(ox, oy, PATH_X, NORTH_STRIP_Y)], fill=WALL, width=2)
    draw.line([to_screen(ox, oy, PATH_X + PATH_W, 0), to_screen(ox, oy, PATH_X + PATH_W, NORTH_STRIP_Y)],
              fill=WALL, width=2)
    draw.rectangle(shell, outline=WALL, width=4)

    # Labels & equipment
    for z in zones:
        x1, y1, x2, y2 = zone_rect(ox, oy, z)
        cx = (x1 + x2) / 2
        cy = y1 + 12
        tw = draw.textlength(z.code, font=fonts["code"])
        draw.text((cx - tw / 2, cy), z.code, fill=ACCENT, font=fonts["code"])
        cy += 16
        for part in z.title.split(" & "):
            tw = draw.textlength(part, font=fonts["room"])
            draw.text((cx - tw / 2, cy), part, fill=TEXT, font=fonts["room"])
            cy += 14
        draw_wrapped(draw, z.subtitle, cx, cy + 2, x2 - x1 - 8, fonts["tiny"], DIM)
        draw.text((cx - draw.textlength(z.size, font=fonts["tiny"]) / 2, y2 - 24), z.size, fill=DIM, font=fonts["tiny"])
        draw.text((cx - draw.textlength(z.area, font=fonts["tiny"]) / 2, y2 - 12), z.area, fill=DIM, font=fonts["tiny"])

    for z in zones:
        draw_equipment(draw, fonts, ox, oy, z)

    # Doors
    draw_door_on_path(draw, ox, oy, OIL_H - 2, 4.0, "4'-0\" DOOR", fonts)          # north of E-S oil
    draw_internal_door(draw, ox, oy, OIL_H + PANEL + FACEPACK_H / 2 - 1.75)        # facepack
    draw_internal_door(draw, ox, oy, OIL_H + PANEL + FACEPACK_H + PANEL + PACKING_H / 2 - 1.75)
    draw_internal_door(draw, ox, oy, OFFICE_H / 2 - 1.75)                          # W6
    draw_internal_door(draw, ox, oy, OFFICE_H + PANEL + QC_H / 2 - 1.75)           # W5
    draw_internal_door(draw, ox, oy, OFFICE_H + PANEL + QC_H + PANEL + SOAP_H / 2 - 1.75)  # soap

    pack_top = OIL_H + PANEL + FACEPACK_H + PANEL + PACKING_H
    draw_rolling_shutter(draw, ox, oy, pack_top - 1, "7'-0\" ENTRY", fonts)         # north of packing

    draw_north_door(draw, ox, oy, 27, 3.0, "3' MEN", fonts)                        # men entry
    draw_north_door(draw, ox, oy, 12, 6.0, "6' RAW MAT.", fonts)                   # raw material entry

    # Dimensions
    draw.text((ox + plan_w / 2 - 30, oy - 28), "36'-0\"", fill=DIM, font=fonts["dim"])
    draw.text((ox - 58, oy + plan_h / 2), "70'-0\"", fill=DIM, font=fonts["dim"])

    west_segments = [
        (OFFICE_H, "10'-0\""), (PANEL, "2\""), (QC_H, "10'-0\""), (PANEL, "2\""), (SOAP_H, _fmt_ft(SOAP_H)),
    ]
    draw_dimension_chain(draw, fonts, ox, oy, west_segments, "v", 48)

    east_segments = [
        (OIL_H, "20'-2\""), (PANEL, "2\""), (FACEPACK_H, "10'-0\""), (PANEL, "2\""),
        (PACKING_H, "16'-0\""), (PANEL, "2\""), (OPEN_H, "10'-0\""), (NORTH_STRIP_H, _fmt_ft(NORTH_STRIP_H)),
    ]
    draw_dimension_chain(draw, fonts, ox, oy, east_segments, "v", -48)

    draw.text((ox + ft(8) - 20, oy + plan_h + 36), "16'-0\" WEST BAY", fill=DIM, font=fonts["tiny"])
    draw.text((ox + ft(18) - 14, oy + plan_h + 36), "4'-0\" PATH", fill=DIM, font=fonts["tiny"])
    draw.text((ox + ft(28) - 18, oy + plan_h + 36), "16'-0\" EAST BAY", fill=DIM, font=fonts["tiny"])

    # North arrow
    nx, ny = ox + plan_w + 30, oy - 10
    draw.polygon([(nx, ny - 36), (nx - 14, ny + 6), (nx + 14, ny + 6)], fill=ACCENT)
    draw.text((nx - 5, ny - 56), "N", fill=ACCENT, font=fonts["code"])

    # Legend
    lx, ly = ox + plan_w + 36, oy + 10
    draw.text((lx, ly), "LEGEND", fill=ACCENT, font=fonts["room"])
    legend_items = [
        ("soap", "Soap making (W1–W4 joined)"),
        ("oil", "Oil making"),
        ("production", "Facepack & powder"),
        ("open_packing", "Packing"),
        ("open_dock", "Open dock / staging"),
        ("pvc_store", "Raw material store"),
        ("office_lab", "Office, QC, men change"),
        ("circulation", "Central path"),
    ]
    for i, (key, label) in enumerate(legend_items):
        y = ly + 22 + i * 20
        draw.rectangle([lx, y, lx + 18, y + 14], fill=ZONE_COLORS[key], outline=WALL)
        draw.text((lx + 26, y - 1), label, fill=TEXT, font=fonts["tiny"])

    ny0 = ly + 22 + len(legend_items) * 20 + 12
    draw.text((lx, ny0), "CONSTRUCTION NOTES", fill=ACCENT, font=fonts["room"])
    notes = [
        "1. W1+W2+W3+W4 joined as one soap section on west bay.",
        "2. E-S is oil making (20'-2\" × 16').",
        "3. East stack: oil → 4' door → facepack → packing → 7' east door → 10' open.",
        "4. E-N north strip: raw material (joins soap) + men change 6×8 NE.",
        "5. North strip has no 4'-0\" central path; raw material bridges west.",
        "6. North doors: 3' men entry, 6' raw material entry.",
        "7. Floor: PVC mat wood finish. No false ceiling; 12' clear.",
    ]
    for i, note in enumerate(notes):
        draw.text((lx, ny0 + 20 + i * 15), note, fill=TEXT, font=fonts["tiny"])

    draw.rectangle([ox, oy + plan_h + 52, ox + ft(10), oy + plan_h + 62], fill=ACCENT)
    draw.text((ox, oy + plan_h + 66), "10'-0\"", fill=TEXT, font=fonts["tiny"])
    return img


def save_png(img: Image.Image, path: Path) -> None:
    img.save(path, "PNG", dpi=(200, 200))


def build_page2_pdf(c: canvas.Canvas, page_w: float, page_h: float) -> None:
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
        ["CODE", "ROOM", "SIZE", "AREA", "NOTES"],
        ["W-SOAP", "Soap making (W1–W4 joined)", f"{_fmt_ft(SOAP_H)} × 16'-0\"", f"{int(SOAP_H * 16)} sq ft",
         "Mixer, curing racks, soap wrap/carton"],
        ["W5", "Quality control lab", "10'-0\" × 16'-0\"", "160 sq ft", "Bench, sink, retained samples"],
        ["W6", "Office", "10'-0\" × 16'-0\"", "160 sq ft", "Owner seated facing east"],
        ["E-S", "Oil making, storage & filling", "20'-2\" × 16'-0\"", "323 sq ft", "Press, 5 tanks, filling line"],
        ["E-FP", "Facepack & powder making", "10'-0\" × 16'-0\"", "160 sq ft", "North of 4' door from oil"],
        ["E-PK", "Packing", "16'-0\" × 16'-0\"", "256 sq ft", "Cartoning, sealing, staging"],
        ["E-OPEN", "Open dock / staging", "10'-0\" × 16'-0\"", "160 sq ft", "After 7' east entry door"],
        ["E-N-RM", "Raw material store", f"{_fmt_ft(RAW_JOIN_W)} × {_fmt_ft(NORTH_STRIP_H)}",
         f"{int(RAW_JOIN_W * NORTH_STRIP_H)} sq ft", "Joins soap north; 6' north door; no 4' path"],
        ["E-N-MC", "Men change & safety", "6'-0\" × 8'-0\"", "48 sq ft", "NE corner; 3' north door"],
        ["P1", "Central path", f"4'-0\" × {_fmt_ft(NORTH_STRIP_Y)}", f"{int(PATH_W * NORTH_STRIP_Y)} sq ft",
         "Stops at north strip"],
    ]
    table = Table(schedule_data, colWidths=[0.55 * inch, 1.65 * inch, 0.95 * inch, 0.65 * inch, 2.4 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B4332")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F1E4")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    tw, th = table.wrapOn(c, page_w - 1.1 * inch, page_h)
    table.drawOn(c, 0.55 * inch, y - th)
    y -= th + 16

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#1B4332"))
    c.drawString(0.55 * inch, y, "PROCESS FLOW")
    y -= 14
    flows = [
        "OIL:  Raw material (E-N) → E-S oil make/tanks/fill → E-PK packing → E-OPEN → dispatch (7' east door)",
        "PACK: Raw material → E-FP facepack/powder → E-PK packing → E-OPEN → dispatch",
        "SOAP: Raw material (joined north) → W-SOAP make/cure/pack → E-PK or E-OPEN dispatch",
    ]
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.black)
    for line in flows:
        c.drawString(0.55 * inch, y, line)
        y -= 12

    y -= 6
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.55 * inch, y, "DOOR SCHEDULE")
    y -= 14
    door_data = [
        ["MARK", "SIZE", "LOCATION", "REMARKS"],
        ["—", "4'-0\"", "North of E-S oil, to facepack/path", "Wide passage door"],
        ["—", "7'-0\" rolling shutter", "East wall, north of packing", "Entry to 10' open dock"],
        ["—", "3'-0\"", "North wall, men change", "Men entry into E-N NE room"],
        ["—", "6'-0\"", "North wall, raw material", "Raw material entry into E-N"],
        ["W5/W6/soap", "3'-6\" × 7'-0\"", "West rooms to central path", "Flush, opens into room"],
        ["Floor", "PVC mat, wood finish", "Entire shed", "No false ceiling; 12'-0\" clear"],
    ]
    dtable = Table(door_data, colWidths=[0.7 * inch, 1.0 * inch, 1.5 * inch, 3.0 * inch])
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
        f"West: 10'+2\"+10'+2\"+{_fmt_ft(SOAP_H)}=70'-0\"  |  "
        f"East: 20'-2\"+10'+16'+10'+{_fmt_ft(NORTH_STRIP_H)}+panels=70'-0\"  |  across 16'+4'+16'=36'-0\"",
    )


def save_pdf(page1: Image.Image, path: Path) -> None:
    page_w, page_h = landscape(letter)
    c = canvas.Canvas(str(path), pagesize=landscape(letter))
    buf = BytesIO()
    page1.save(buf, format="PNG", dpi=(200, 200))
    buf.seek(0)
    img_w, img_h = page1.size
    scale = min((page_w - 28) / img_w, (page_h - 28) / img_h)
    draw_w, draw_h = img_w * scale, img_h * scale
    c.drawImage(ImageReader(buf), (page_w - draw_w) / 2, (page_h - draw_h) / 2, width=draw_w, height=draw_h)
    c.showPage()
    build_page2_pdf(c, page_w, page_h)
    c.showPage()
    c.setAuthor("Parambu Organics")
    c.setTitle("Parambu Organics Factory Floor Plan")
    c.save()


def main() -> None:
    page1 = render_floor_plan_page()
    save_png(page1, OUTPUT_PNG)
    save_pdf(page1, OUTPUT_PDF)
    print(f"Wrote {OUTPUT_PNG}")
    print(f"Wrote {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
