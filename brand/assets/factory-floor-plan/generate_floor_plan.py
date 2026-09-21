#!/usr/bin/env python3
"""Generate Parambu Organics factory floor plan (PNG + PDF)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[2]
OUTPUT_PNG = REPO_ROOT / "floor-plan.png"
OUTPUT_PDF = REPO_ROOT / "floor-plan.pdf"

# Building envelope (feet)
BUILDING_EW = 36.0
BUILDING_NS = 70.0
WING_DEPTH = 16.0
AISLE_WIDTH = 4.0
NORTH_STRIP_DEPTH = 8.0

# Palette
BG = (252, 250, 246)
WALL = (30, 30, 30)
WALL_LIGHT = (120, 120, 120)
ROOM_FILL = (245, 240, 232)
AISLE_FILL = (235, 230, 220)
DOOR = (180, 60, 40)
TEXT = (25, 45, 35)
ACCENT = (27, 67, 50)
DIM = (90, 90, 90)
TITLE = (214, 170, 132)

PX_PER_FT = 18
MARGIN_LEFT = 140
MARGIN_RIGHT = 300
MARGIN_TOP = 140
TITLE_H = 200


@dataclass(frozen=True)
class Room:
    name: str
    x: float
    y: float
    w: float
    h: float
    fill: tuple[int, int, int] = ROOM_FILL
    label_size: int = 22


@dataclass(frozen=True)
class Door:
    wall: str  # north | south | east | west
    x: float
    y: float
    width: float
    room: str


def ft_to_px(value: float) -> float:
    return value * PX_PER_FT


def load_fonts() -> dict[str, ImageFont.FreeTypeFont | ImageFont.ImageFont]:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    bold = regular = None
    for path in candidates:
        if Path(path).exists():
            if "Bold" in path and bold is None:
                bold = ImageFont.truetype(path, 22)
            elif "Bold" not in path and regular is None:
                regular = ImageFont.truetype(path, 18)
    if bold is None:
        bold = ImageFont.load_default()
    if regular is None:
        regular = ImageFont.load_default()
    return {
        "title": ImageFont.truetype(candidates[0], 34) if Path(candidates[0]).exists() else bold,
        "subtitle": ImageFont.truetype(candidates[1], 20) if Path(candidates[1]).exists() else regular,
        "room": ImageFont.truetype(candidates[0], 22) if Path(candidates[0]).exists() else bold,
        "small": ImageFont.truetype(candidates[1], 16) if Path(candidates[1]).exists() else regular,
        "dim": ImageFont.truetype(candidates[1], 14) if Path(candidates[1]).exists() else regular,
    }


def build_layout() -> tuple[list[Room], list[Door], list[tuple[float, float, float, float]]]:
    """Return rooms, doors, and partition wall segments (x1,y1,x2,y2) in feet."""
    soap_ns = 41.0 + 8.0 / 12.0  # 41'-8"
    prod_floor_top = BUILDING_NS - NORTH_STRIP_DEPTH  # 62'

    rooms: list[Room] = [
        # North strip (full width, no central aisle)
        Room("RAW MATERIAL\nSTORAGE", 0, prod_floor_top, 30, NORTH_STRIP_DEPTH, (238, 228, 210), 20),
        Room("MEN CHANGE\n& SAFETY", 30, prod_floor_top, 6, NORTH_STRIP_DEPTH, (228, 236, 228), 18),
        # West wing (16' deep from west wall)
        Room("OFFICE", 0, 0, WING_DEPTH, 10, (232, 236, 244), 22),
        Room("QC / QUALITY\nCONTROL", 0, 10, WING_DEPTH, 10, (236, 232, 244), 18),
        Room(
            "SOAP MAKING\n(W2 – W4 joined)",
            0,
            20,
            WING_DEPTH,
            soap_ns,
            (244, 236, 228),
            20,
        ),
        # East wing (16' deep from east wall)
        Room("OPEN DOCK", WING_DEPTH + AISLE_WIDTH, 0, WING_DEPTH, 10, (228, 236, 228), 20),
        Room("PACKING", WING_DEPTH + AISLE_WIDTH, 10, WING_DEPTH, 16, (244, 240, 228), 22),
        Room("FACEPACK &\nPOWDER", WING_DEPTH + AISLE_WIDTH, 26, WING_DEPTH, 10, (240, 244, 228), 18),
        Room("OIL MAKING", WING_DEPTH + AISLE_WIDTH, 36, WING_DEPTH, 22, (236, 244, 236), 20),
        # Central aisle label zone handled separately
    ]

    doors: list[Door] = [
        Door("north", 12, BUILDING_NS, 6, "RAW MATERIAL\nSTORAGE"),
        Door("north", 33, BUILDING_NS, 3, "MEN CHANGE\n& SAFETY"),
        Door("east", BUILDING_EW, 47, 4, "OIL MAKING"),
        Door("east", BUILDING_EW, 1.5, 7, "OPEN DOCK"),
    ]

    partitions: list[tuple[float, float, float, float]] = [
        # W1 – separates raw material from production floor (north strip)
        (30, prod_floor_top, 30, BUILDING_NS),
        # Interior soap bay partitions W2–W4 (evenly spaced across soap room depth)
        *[
            (WING_DEPTH, 20 + i * soap_ns / 3, WING_DEPTH, 20 + (i + 1) * soap_ns / 3)
            for i in range(1, 3)
        ],
        # Room dividers west wing
        (0, 10, WING_DEPTH, 10),
        (0, 20, WING_DEPTH, 20),
        # Room dividers east wing
        (WING_DEPTH + AISLE_WIDTH, 10, BUILDING_EW, 10),
        (WING_DEPTH + AISLE_WIDTH, 26, BUILDING_EW, 26),
        (WING_DEPTH + AISLE_WIDTH, 36, BUILDING_EW, 36),
        # Central aisle edges
        (WING_DEPTH, 0, WING_DEPTH, prod_floor_top),
        (WING_DEPTH + AISLE_WIDTH, 0, WING_DEPTH + AISLE_WIDTH, prod_floor_top),
        # North strip floor line
        (0, prod_floor_top, BUILDING_EW, prod_floor_top),
    ]

    return rooms, doors, partitions


def draw_dimension(
    draw: ImageDraw.ImageDraw,
    fonts: dict,
    p1: tuple[float, float],
    p2: tuple[float, float],
    label: str,
    offset: float = 28,
    vertical: bool = False,
) -> None:
    x1, y1 = p1
    x2, y2 = p2
    if vertical:
        mx = x1 - offset
        draw.line([(mx, y1), (mx, y2)], fill=DIM, width=2)
        draw.line([(mx - 6, y1), (mx + 6, y1)], fill=DIM, width=2)
        draw.line([(mx - 6, y2), (mx + 6, y2)], fill=DIM, width=2)
        cy = (y1 + y2) / 2
        draw.text((mx - 52, cy - 8), label, fill=DIM, font=fonts["dim"])
    else:
        my = y1 - offset
        draw.line([(x1, my), (x2, my)], fill=DIM, width=2)
        draw.line([(x1, my - 6), (x1, my + 6)], fill=DIM, width=2)
        draw.line([(x2, my - 6), (x2, my + 6)], fill=DIM, width=2)
        cx = (x1 + x2) / 2
        bbox = draw.textbbox((0, 0), label, font=fonts["dim"])
        tw = bbox[2] - bbox[0]
        draw.text((cx - tw / 2, my - 22), label, fill=DIM, font=fonts["dim"])


def to_screen(ox: float, oy: float, bx: float, by: float) -> tuple[float, float]:
    """Convert building coordinates (x east, y north) to image coordinates."""
    return ox + ft_to_px(bx), oy + ft_to_px(BUILDING_NS - by)


def draw_door(
    draw: ImageDraw.ImageDraw,
    ox: float,
    oy: float,
    door: Door,
    wall_thickness: float = 6,
) -> None:
    w = ft_to_px(door.width)
    if door.wall == "north":
        x, y = to_screen(ox, oy, door.x, BUILDING_NS)
        draw.rectangle([x, y - wall_thickness, x + w, y + wall_thickness], fill=BG)
        draw.arc([x, y, x + w, y + w], 180, 270, fill=DOOR, width=3)
        draw.line([(x, y), (x, y + w)], fill=DOOR, width=2)
    elif door.wall == "east":
        x, y = to_screen(ox, oy, BUILDING_EW, door.y + door.width)
        draw.rectangle([x - wall_thickness, y, x + wall_thickness, y + w], fill=BG)
        draw.arc([x - w, y, x, y + w], 270, 360, fill=DOOR, width=3)
        draw.line([(x, y), (x - w, y)], fill=DOOR, width=2)


def wrap_label(draw: ImageDraw.ImageDraw, text: str, font, max_width: float) -> list[str]:
    words = text.replace("\n", " ").split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if draw.textlength(test, font=font) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [text]


def draw_room_label(
    draw: ImageDraw.ImageDraw,
    fonts: dict,
    ox: float,
    oy: float,
    room: Room,
) -> None:
    cx = ox + ft_to_px(room.x + room.w / 2)
    cy = oy + ft_to_px(room.y + room.h / 2)
    font = fonts["room"] if room.label_size >= 20 else fonts["small"]
    lines = room.name.split("\n")
    if len(lines) == 1:
        lines = wrap_label(draw, room.name, font, ft_to_px(room.w) - 16)
    line_h = room.label_size + 6
    total_h = len(lines) * line_h
    start_y = cy - total_h / 2
    for i, line in enumerate(lines):
        tw = draw.textlength(line, font=font)
        draw.text((cx - tw / 2, start_y + i * line_h), line, fill=TEXT, font=font)


def draw_north_arrow(draw: ImageDraw.ImageDraw, fonts: dict, x: float, y: float) -> None:
    size = 50
    draw.polygon(
        [(x, y - size), (x - 18, y + 10), (x + 18, y + 10)],
        fill=ACCENT,
    )
    draw.rectangle([x - 6, y + 10, x + 6, y + 34], fill=ACCENT)
    label = "N"
    tw = draw.textlength(label, font=fonts["room"])
    draw.text((x - tw / 2, y - size - 28), label, fill=ACCENT, font=fonts["room"])
    draw.text((x - 42, y + 42), "EAST FACADE →", fill=ACCENT, font=fonts["small"])


def render_floor_plan() -> Image.Image:
    fonts = load_fonts()
    rooms, doors, partitions = build_layout()

    plan_w = int(ft_to_px(BUILDING_EW))
    plan_h = int(ft_to_px(BUILDING_NS))
    img_w = plan_w + MARGIN_LEFT + MARGIN_RIGHT
    img_h = plan_h + MARGIN_TOP + MARGIN_LEFT + TITLE_H
    img = Image.new("RGB", (img_w, img_h), BG)
    draw = ImageDraw.Draw(img)

    ox = MARGIN_LEFT
    oy = MARGIN_TOP + TITLE_H

    # Title block
    draw.text((MARGIN_LEFT, 36), "PARAMBU ORGANICS", fill=ACCENT, font=fonts["title"])
    draw.text(
        (MARGIN_LEFT, 82),
        "Factory Floor Plan — 36' E-W × 70' N-S (East Facing)",
        fill=TEXT,
        font=fonts["subtitle"],
    )
    draw.line([(MARGIN_LEFT, 120), (img_w - MARGIN_RIGHT, 120)], fill=TITLE, width=3)

    # Building shell
    shell = [ox, oy, ox + plan_w, oy + plan_h]
    draw.rectangle(shell, fill=ROOM_FILL, outline=WALL, width=5)

    # Central aisle
    aisle = [
        ox + ft_to_px(WING_DEPTH),
        oy,
        ox + ft_to_px(WING_DEPTH + AISLE_WIDTH),
        oy + ft_to_px(BUILDING_NS - NORTH_STRIP_DEPTH),
    ]
    draw.rectangle(aisle, fill=AISLE_FILL, outline=None)
    ax = ox + ft_to_px(WING_DEPTH + AISLE_WIDTH / 2)
    ay1 = oy + ft_to_px(8)
    ay2 = oy + ft_to_px(BUILDING_NS - NORTH_STRIP_DEPTH - 8)
    draw.text((ax - 34, (ay1 + ay2) / 2 - 40), "4'", fill=DIM, font=fonts["dim"])
    draw.text((ax - 58, (ay1 + ay2) / 2), "CIRCULATION", fill=DIM, font=fonts["dim"])
    draw.text((ax - 34, (ay1 + ay2) / 2 + 24), "AISLE", fill=DIM, font=fonts["dim"])

    # Rooms
    for room in rooms:
        box = [
            ox + ft_to_px(room.x),
            oy + ft_to_px(BUILDING_NS - room.y - room.h),
            ox + ft_to_px(room.x + room.w),
            oy + ft_to_px(BUILDING_NS - room.y),
        ]
        draw.rectangle(box, fill=room.fill, outline=None)

    # Partition walls
    for x1, y1, x2, y2 in partitions:
        draw.line(
            [
                ox + ft_to_px(x1),
                oy + ft_to_px(BUILDING_NS - y1),
                ox + ft_to_px(x2),
                oy + ft_to_px(BUILDING_NS - y2),
            ],
            fill=WALL_LIGHT,
            width=3,
        )

    # Re-stroke exterior
    draw.rectangle(shell, outline=WALL, width=5)

    # W1 label (north strip partition between raw material and men change)
    w1x = ox + ft_to_px(30) + 6
    w1y = oy + ft_to_px(NORTH_STRIP_DEPTH / 2) - 6
    draw.text((w1x, w1y), "W1", fill=DIM, font=fonts["dim"])

    # Soap bay labels W2–W4
    soap_ns = 41.0 + 8.0 / 12.0
    for i, label in enumerate(["W2", "W3", "W4"], start=1):
        bay_y = 20 + (i - 0.5) * soap_ns / 3
        draw.text(
            (ox + ft_to_px(2), oy + ft_to_px(BUILDING_NS - bay_y) - 8),
            label,
            fill=DIM,
            font=fonts["dim"],
        )

    # Doors
    for door in doors:
        draw_door(draw, ox, oy, door)

    # Room labels
    for room in rooms:
        draw_room_label(draw, fonts, ox, oy, room)

    # North strip note
    note_x = ox + ft_to_px(15)
    note_y = oy + ft_to_px(NORTH_STRIP_DEPTH / 2) - 10
    draw.text((note_x - 80, note_y + 50), "(no 4' aisle in north strip)", fill=DIM, font=fonts["dim"])

    # Dimensions
    draw_dimension(
        draw,
        fonts,
        (ox, oy + plan_h + 36),
        (ox + plan_w, oy + plan_h + 36),
        "36' E-W",
        offset=-36,
    )
    draw_dimension(
        draw,
        fonts,
        (ox - 36, oy),
        (ox - 36, oy + plan_h),
        "70' N-S",
        offset=0,
        vertical=True,
    )

    # Finishes legend
    legend_x = ox + plan_w + 24
    legend_y = oy + 20
    draw.text((legend_x, legend_y), "FINISHES", fill=ACCENT, font=fonts["room"])
    specs = [
        "Floor: PVC wood-finish mat",
        "Ceiling: Open (no false ceiling)",
        "Partitions: 2\" panel walls",
        "North doors: 6' (raw material), 3' (men change)",
        "East doors: 4' (oil), 7' (open dock)",
    ]
    for i, line in enumerate(specs):
        draw.text((legend_x, legend_y + 34 + i * 24), f"• {line}", fill=TEXT, font=fonts["small"])

    # Scale bar
    scale_y = oy + plan_h + 72
    scale_len = ft_to_px(10)
    draw.rectangle([ox, scale_y, ox + scale_len, scale_y + 10], fill=ACCENT)
    draw.text((ox, scale_y + 16), "10 feet", fill=TEXT, font=fonts["small"])

    draw_north_arrow(draw, fonts, ox + plan_w + 50, oy + 30)

    # Room schedule
    sched_y = oy + plan_h - 150
    draw.text((legend_x, sched_y), "ROOM SCHEDULE", fill=ACCENT, font=fonts["room"])
    schedule = [
        "Raw material storage — 8' × 30'",
        "Men change & safety — 6' × 8'",
        "Soap making (W2–W4) — 41'-8\" × 16'",
        "Oil making — 22' × 16'",
        "Facepack & powder — 10' × 16'",
        "Packing — 16' × 16'",
        "Open dock — 10' × 16'",
        "QC — 10' × 16'",
        "Office — 10' × 16'",
    ]
    for i, line in enumerate(schedule):
        draw.text((legend_x, sched_y + 30 + i * 20), line, fill=TEXT, font=fonts["dim"])

    return img


def save_pdf(img: Image.Image, path: Path) -> None:
    page_w, page_h = landscape(letter)
    c = canvas.Canvas(str(path), pagesize=landscape(letter))
    img_w, img_h = img.size
    scale = min((page_w - 36) / img_w, (page_h - 36) / img_h)
    draw_w = img_w * scale
    draw_h = img_h * scale
    x = (page_w - draw_w) / 2
    y = (page_h - draw_h) / 2
    c.drawImage(ImageReader(img), x, y, width=draw_w, height=draw_h)
    c.setAuthor("Parambu Organics")
    c.setTitle("Parambu Organics Factory Floor Plan")
    c.showPage()
    c.save()


def main() -> None:
    img = render_floor_plan()
    img.save(OUTPUT_PNG, "PNG", dpi=(150, 150))
    save_pdf(img, OUTPUT_PDF)
    print(f"Wrote {OUTPUT_PNG}")
    print(f"Wrote {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
