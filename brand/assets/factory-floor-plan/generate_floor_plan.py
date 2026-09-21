#!/usr/bin/env python3
"""Parambu soap & oil unit floor plan.

Internal sizes: 36'-0\" east-west by 70'-0\" north-south, east facing.
The exterior wall is drawn outside those sizes. North is up.
"""

from __future__ import annotations

import math
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import portrait
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
OUTPUT_PNG = REPO / "floor-plan.png"
OUTPUT_PDF = REPO / "floor-plan.pdf"

EW, NS = 36.0, 70.0
WEST, PATH, EAST = 16.0, 4.0, 16.0
PANEL = 2.0 / 12.0
X_PATH, X_EAST = WEST, WEST + PATH
OUT = 0.75  # exterior wall drawn outside the internal size
S = 28

PAPER = (250, 248, 244)
WHITE = (255, 255, 255)
INK = (28, 36, 44)
MUTED = (86, 92, 98)
DIM = (72, 80, 88)
GREEN = (22, 112, 68)
RED = (168, 48, 42)
WALL = (32, 40, 50)
GLASS = (64, 96, 118)
PLATE = (255, 255, 255)

STORE = (248, 239, 216)
PROD = (224, 238, 224)
PACK = (224, 234, 246)
LAB = (240, 230, 244)
CIRC = (232, 235, 238)

FONT = Path("/usr/share/fonts/truetype/dejavu")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(str(FONT / name), size)


def stack(heights: list[float]) -> list[tuple[float, float]]:
    """South-origin (y, height) for each zone, with a 2\" panel between zones."""
    y = 0.0
    out = []
    for i, h in enumerate(heights):
        out.append((y, h))
        y += h
        if i < len(heights) - 1:
            y += PANEL
    if abs(y - NS) > 1e-6:
        raise SystemExit(f"stack sums to {y}, not {NS}")
    return out


def feet(n: float) -> str:
    sign = "-" if n < 0 else ""
    n = abs(n)
    whole = int(n)
    inches = int(round((n - whole) * 12))
    if inches == 12:
        whole += 1
        inches = 0
    if inches == 0:
        return f"{sign}{whole}'-0\""
    return f"{sign}{whole}'-{inches}\""


WEST_H = [10, 10, 19 + 2 / 12, 10, 10, 10]  # W6 W5 W4 W3 W2 W1
EAST_H = [10, 10, 9.5, 10, 10, 9.5, 10]  # E5 E4 godown E3 E2 entry E1
WEST_Y = stack(WEST_H)
EAST_Y = stack(EAST_H)


def main() -> None:
    img, overlaps = render()
    rgb = img.convert("RGB")
    rgb.save(OUTPUT_PNG, "PNG", dpi=(144, 144))
    save_pdf(rgb, OUTPUT_PDF)
    print(f"Wrote {OUTPUT_PNG} ({img.width}×{img.height})")
    print(f"Wrote {OUTPUT_PDF}")
    if overlaps:
        print(f"{len(overlaps)} overlap(s):")
        for line in overlaps:
            print(" ", line)
        raise SystemExit(1)


def render() -> tuple[Image.Image, list[str]]:
    f_title = font(26, True)
    f_sub = font(13)
    f_room = font(15, True)
    f_small = font(12)
    f_tiny = font(11)
    f_fix = font(10)
    f_dim = font(12)
    f_note = font(11)

    plan_w, plan_h = int(EW * S), int(NS * S)
    ml, mr, mt, mb = 230, 500, 200, 460
    W, H = ml + plan_w + mr, mt + plan_h + mb
    img = Image.new("RGBA", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    ox, oy = ml, mt
    boxes: list[tuple[str, float, float, float, float]] = []
    swings: list[tuple[str, float, float, float, float]] = []

    def P(x: float, y: float) -> tuple[float, float]:
        return ox + x * S, oy + (NS - y) * S

    def rect(x, y, w, h, fill):
        x1, y1 = P(x, y + h)
        x2, y2 = P(x + w, y)
        draw.rectangle([min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)], fill=fill)

    def track(key, bb):
        boxes.append((key, bb[0], bb[1], bb[2], bb[3]))

    def center(sx, sy, text, fnt, fill, key=None, plate=False):
        bb = draw.textbbox((0, 0), text, font=fnt)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        x = sx - tw / 2 - bb[0]
        y = sy - th / 2 - bb[1]
        if plate:
            draw.rectangle([x - 2, y - 1, x + tw + 2, y + th + 1], fill=PLATE)
        draw.text((x, y), text, font=fnt, fill=fill)
        track(key or text, (x + bb[0], y + bb[1], x + bb[2], y + bb[3]))

    def btext(bx, by, text, fnt, fill, key=None, plate=False):
        center(*P(bx, by), text, fnt, fill, key, plate)

    def stext(sx, sy, text, fnt, fill, key=None):
        draw.text((sx, sy), text, font=fnt, fill=fill)
        bb = draw.textbbox((sx, sy), text, font=fnt)
        track(key or text, bb)

    wy = {code: WEST_Y[i] for i, code in enumerate(["W6", "W5", "W4", "W3", "W2", "W1"])}
    ey = {code: EAST_Y[i] for i, code in enumerate(["E5", "E4", "GD", "E3", "E2", "EN", "E1"])}
    y_raw = wy["W1"][0]
    soap_y = wy["W4"][0]
    soap_h = (wy["W2"][0] + wy["W2"][1]) - soap_y
    oil_y = ey["E5"][0]
    oil_h = (ey["E4"][0] + ey["E4"][1]) - oil_y
    en_y, en_h = ey["EN"]
    gd_y, gd_h = ey["GD"]
    e2_y, e2_h = ey["E2"]
    e3_y, _e3_h = ey["E3"]

    # Door locations. Widths are the clear openings.
    raw_x, raw_w = 21.5, 6.0
    men_x, men_w = 32.0, 3.0
    out_x, out_w = 29.0, 6.0
    path_w = 4.0
    path_y = en_y + (en_h - path_w) / 2
    d1_y = en_y + (en_h - 7.0) / 2
    d2_y = gd_y + (gd_h - 7.0) / 2
    office_y, qc_y = 2.6, wy["W5"][0] + 3.1
    soap_door_y = soap_y + 17.6
    oil_door_y, e3_door_y, e2_door_y = 6.0, e3_y + 3.1, e2_y + 3.1
    leaf = 3.5

    # --- title ---
    stext(36, 16, "PARAMBU ORGANICS", f_title, INK, "title")
    stext(36, 48, "SOAP & OIL UNIT   ·   FLOOR PLAN", font(15, True), INK, "subtitle")
    stext(36, 70, "36'-0\"  ×  70'-0\" internal    ·    2,520 sq ft    ·    east facing    ·    north up", f_tiny, MUTED, "sub2")
    draw.line([(36, 94), (W - 36, 94)], fill=(186, 180, 166), width=2)

    # --- room fills ---
    rect(0, wy["W6"][0], WEST, wy["W6"][1], LAB)
    rect(0, wy["W5"][0], WEST, wy["W5"][1], LAB)
    rect(0, soap_y, WEST, soap_h, PROD)
    rect(0, y_raw, EW, wy["W1"][1], STORE)
    rect(X_EAST, oil_y, EAST, oil_h, PROD)
    rect(X_EAST, gd_y, EAST, gd_h, CIRC)
    rect(X_EAST, e3_y, EAST, ey["E3"][1], PACK)
    rect(X_EAST, e2_y, EAST, e2_h, STORE)
    rect(X_EAST, en_y, EAST, en_h, CIRC)
    rect(X_PATH, 0, PATH, y_raw, CIRC)

    def hatch(x, y, w, h):
        x1, y1 = P(x, y + h)
        x2, y2 = P(x + w, y)
        a, b = int(min(x1, x2)), int(min(y1, y2))
        c, d_ = int(max(x1, x2)), int(max(y1, y2))
        pw, ph = c - a, d_ - b
        if pw < 6 or ph < 6:
            return
        chip = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        cd = ImageDraw.Draw(chip)
        for i in range(-ph, pw + ph, 8):
            cd.line([(i, ph), (i + ph, 0)], fill=(90, 96, 100, 55), width=1)
        img.alpha_composite(chip, (a, b))

    def fixture(x, y, w, h, label, kind="table"):
        x1, y1 = P(x, y + h)
        x2, y2 = P(x + w, y)
        box = [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)]
        if kind == "rack":
            hatch(x, y, w, h)
        draw.rectangle(box, outline=INK, width=2)
        if kind == "sink":
            pad = 4
            draw.ellipse([box[0] + pad, box[1] + pad, box[2] - pad, box[3] - pad], outline=GLASS, width=2)
        if not label:
            return
        fnt = f_fix
        if draw.textlength(label, font=fnt) > (w * S) - 8:
            fnt = font(9)
        btext(x + w / 2, y + h / 2, label, fnt, INK, f"{label}@{x:.1f},{y:.1f}", plate=(kind == "rack"))

    def tank(cx, cy, r, label):
        x, y = P(cx, cy)
        rr = r * S
        draw.ellipse([x - rr, y - rr, x + rr, y + rr], outline=INK, width=2)
        draw.ellipse([x - rr + 4, y - rr + 4, x + rr - 4, y + rr - 4], outline=(120, 128, 134), width=1)
        btext(cx, cy, label, f_fix, INK, label, plate=True)

    # Raw material — equipment stays in the west half, clear of the two north swings.
    fixture(0.7, 64.4, 6.6, 2.15, "RACK", "rack")
    fixture(7.7, 64.4, 6.4, 2.15, "RACK", "rack")
    fixture(14.6, 64.45, 4.6, 2.05, "WEIGH", "table")
    fixture(0.7, 61.15, 6.6, 2.35, "RACK", "rack")
    fixture(7.7, 61.15, 6.4, 2.35, "RACK", "rack")
    fixture(14.6, 61.2, 4.6, 2.25, "SAMPLE", "table")

    # Soap making & curing. The east door swing occupies y 38.2–41.7, x 12.5–16.
    fixture(0.6, 52.35, 7.2, 3.15, "MIXER", "table")
    fixture(8.2, 52.35, 7.2, 3.15, "MOULD", "table")
    fixture(0.6, 48.15, 7.2, 3.15, "CUTTER", "table")
    fixture(8.2, 48.15, 7.2, 3.15, "LYE", "table")
    fixture(0.6, 43.15, 4.7, 3.9, "CURING", "rack")
    fixture(5.65, 43.15, 4.7, 3.9, "CURING", "rack")
    fixture(10.7, 43.15, 4.7, 3.9, "CURING", "rack")
    fixture(0.6, 33.7, 7.2, 3.3, "WRAP", "table")
    fixture(8.2, 33.7, 7.2, 3.3, "CARTON", "table")
    fixture(0.6, 29.45, 7.2, 3.2, "STORE", "rack")
    fixture(8.2, 29.45, 7.2, 3.2, "TABLE", "table")
    fixture(0.6, 25.2, 14.8, 3.15, "CURING RACK", "rack")
    fixture(0.6, 21.15, 14.8, 3.0, "CAKE & WASTE", "table")

    # QC and office. Swings are the east 3'-6\" of each room.
    fixture(0.55, 14.7, 11.3, 2.35, "LAB BENCH", "table")
    fixture(0.55, 11.05, 5.2, 2.55, "SINK", "sink")
    fixture(6.15, 11.1, 5.0, 2.45, "SCOPES", "table")
    fixture(11.55, 10.95, 3.9, 1.95, "SAMPLES", "rack")
    fixture(0.7, 4.15, 6.6, 3.05, "DESK", "table")
    fixture(8.0, 5.15, 4.0, 1.9, "CABINET", "rack")
    fixture(0.7, 0.7, 4.4, 2.55, "VISITOR", "table")
    fixture(8.0, 0.75, 3.9, 3.5, "FILES", "rack")

    # Oil. The west door swing occupies x 20–23.5, y 6–9.5.
    fixture(20.75, 14.05, 6.7, 3.25, "COLD PRESS", "table")
    fixture(28.55, 14.05, 6.7, 3.25, "FILTER", "table")
    fixture(20.75, 11.15, 3.6, 2.15, "TANK", "table")
    for i, lab in enumerate(["T1", "T2", "T3", "T4", "T5"]):
        tank(26.15 + i * 1.85, 10.55, 0.72, lab)
    fixture(24.3, 1.7, 3.5, 3.15, "FILL", "table")
    fixture(28.15, 1.7, 3.5, 3.15, "CAP", "table")
    fixture(32.0, 1.7, 3.3, 3.15, "LABEL", "table")

    # Godown, facepack, finished product.
    fixture(21.1, 21.05, 5.6, 2.05, "PALLET", "rack")
    fixture(29.2, 21.05, 5.6, 2.05, "PALLET", "rack")
    fixture(24.15, 34.25, 5.5, 2.75, "MIXER", "table")
    fixture(30.35, 34.25, 4.9, 2.75, "MILL", "table")
    fixture(24.15, 30.65, 5.5, 2.55, "SIFTER", "table")
    fixture(30.35, 30.65, 4.9, 2.55, "JARS", "table")
    fixture(20.7, 40.7, 4.7, 2.05, "PALLET", "rack")
    fixture(25.75, 40.7, 4.7, 2.05, "PALLET", "rack")
    fixture(30.8, 40.7, 4.5, 2.05, "DISPATCH", "rack")

    # Hand wash in the clear southwest corner of D1, clear of the path-door swing.
    fixture(20.55, 50.9, 1.55, 1.3, "", "sink")
    btext(23.2, 51.55, "WASH", font(9), MUTED, "wash")

    # --- exterior poche, outside the internal line ---
    def band(x, y, w, h, fill):
        rect(x, y, w, h, fill)

    band(-OUT, 0, OUT, NS, WALL)          # west
    band(EW, 0, OUT, NS, WALL)             # east
    band(-OUT, NS, EW + 2 * OUT, OUT, WALL)  # north
    band(-OUT, -OUT, EW + 2 * OUT, OUT, WALL)  # south

    def punch(x, y, w, h):
        rect(x, y, w, h, PAPER)

    def jamb_h(x0, x1, y):
        draw.line([P(x0, y), P(x1, y)], fill=WALL, width=2)

    def window_v(x_inner, outward, y0, length):
        y1 = y0 + length
        x_outer = x_inner + outward * OUT
        punch(min(x_inner, x_outer), y0, abs(x_outer - x_inner), length)
        for t in (0.32, 0.68):
            x = x_inner + outward * OUT * t
            draw.line([P(x, y0), P(x, y1)], fill=GLASS, width=2)
        jamb_h(x_inner, x_outer, y0)
        jamb_h(x_inner, x_outer, y1)

    def shutter(y0):
        y1 = y0 + 7.0
        punch(EW, y0, OUT, 7.0)
        for i in range(9):
            yy = y0 + 7.0 * (i + 0.5) / 9
            draw.line([P(EW + 0.08, yy), P(EW + OUT - 0.08, yy)], fill=RED, width=2)
        jamb_h(EW, EW + OUT, y0)
        jamb_h(EW, EW + OUT, y1)
        # mark just outside the wall, clear of the dimension chain
        paste_vertical(img, "D1" if abs(y0 - d1_y) < 0.1 else "D2", font(12, True), RED, *P(EW + OUT + 0.55, (y0 + y1) / 2), boxes)

    window_v(0, -1, 63.2, 4.0)
    window_v(0, -1, 48.4, 4.0)
    window_v(0, -1, 26.2, 4.0)
    window_v(0, -1, 15.4, 4.0)
    window_v(0, -1, 3.4, 4.0)
    window_v(EW, 1, 64.0, 4.0)
    window_v(EW, 1, 42.2, 4.0)
    window_v(EW, 1, 31.4, 4.0)
    window_v(EW, 1, 13.4, 4.0)
    shutter(d1_y)
    shutter(d2_y)

    # --- 2\" panels. Joins omit the wall: soap hall, oil hall, north raw room. ---
    def segments(a, b, gaps):
        cuts = []
        for g0, g1 in gaps:
            lo, hi = max(a, min(g0, g1)), min(b, max(g0, g1))
            if hi - lo > 1e-6:
                cuts.append((lo, hi))
        cuts.sort()
        merged = []
        for g0, g1 in cuts:
            if merged and g0 <= merged[-1][1] + 1e-6:
                merged[-1] = (merged[-1][0], max(merged[-1][1], g1))
            else:
                merged.append([g0, g1])
        out, x = [], a
        for g0, g1 in merged:
            if g0 - x > 0.03:
                out.append((x, g0))
            x = g1
        if b - x > 0.03:
            out.append((x, b))
        return out

    def wall_h(x0, x1, y, gaps):
        t = PANEL
        for a, b in segments(x0, x1, gaps):
            rect(a, y - t / 2, b - a, t, WALL)

    def wall_v(x, y0, y1, gaps):
        t = PANEL
        for a, b in segments(y0, y1, gaps):
            rect(x - t / 2, a, t, b - a, WALL)

    wall_h(0, WEST, wy["W5"][0], [])
    wall_h(0, WEST, soap_y, [])
    wall_h(0, EW, y_raw, [(raw_x, raw_x + raw_w), (men_x, men_x + men_w)])
    wall_h(X_EAST, EW, oil_y + oil_h, [])
    wall_h(X_EAST, EW, e3_y, [])
    wall_h(X_EAST, EW, e2_y, [])
    wall_h(X_EAST, EW, en_y, [(out_x, out_x + out_w)])

    wall_v(X_PATH, 0, y_raw, [(office_y, office_y + leaf), (qc_y, qc_y + leaf), (soap_door_y, soap_door_y + leaf)])
    wall_v(
        X_EAST,
        0,
        y_raw,
        [
            (oil_door_y, oil_door_y + leaf),
            (oil_y + oil_h, e3_y),  # godown open to the path
            (e3_door_y, e3_door_y + leaf),
            (e2_door_y, e2_door_y + leaf),
            (path_y, path_y + path_w),
        ],
    )

    def threshold_h(x, y, w):
        draw.line([P(x, y), P(x + w, y)], fill=(120, 116, 108), width=1)

    def threshold_v(x, y, h):
        draw.line([P(x, y), P(x, y + h)], fill=(120, 116, 108), width=1)

    threshold_h(raw_x, y_raw, raw_w)
    threshold_h(men_x, y_raw, men_w)
    threshold_h(out_x, en_y, out_w)
    for x, y in (
        (X_PATH, office_y),
        (X_PATH, qc_y),
        (X_PATH, soap_door_y),
        (X_EAST, oil_door_y),
        (X_EAST, e3_door_y),
        (X_EAST, e2_door_y),
        (X_EAST, path_y),
    ):
        width = path_w if abs(y - path_y) < 0.01 else leaf
        threshold_v(x, y, width)

    def swing(hx, hy, radius, a0, a1, key):
        sx, sy = P(hx, hy)
        r = radius * S
        pts = []
        for i in range(24):
            a = math.radians(a0 + (a1 - a0) * i / 23)
            pts.append((sx + r * math.cos(a), sy - r * math.sin(a)))
        draw.line(pts, fill=GREEN, width=1)
        draw.line([(sx, sy), pts[-1]], fill=GREEN, width=2)
        xs = [p[0] for p in pts] + [sx]
        ys = [p[1] for p in pts] + [sy]
        swings.append((key, min(xs), min(ys), max(xs), max(ys)))

    # Swings open into the room, off the 4' path. The D1 path door opens into the entry.
    swing(raw_x, y_raw, raw_w, 0, 90, "raw-in")
    swing(men_x, y_raw, men_w, 0, 90, "men")
    swing(out_x, en_y, out_w, 0, -90, "out")
    swing(X_EAST, path_y, path_w, 90, 0, "to-path")
    swing(X_PATH, office_y, leaf, 90, 180, "office")
    swing(X_PATH, qc_y, leaf, 90, 180, "qc")
    swing(X_PATH, soap_door_y, leaf, 90, 180, "soap")
    swing(X_EAST, oil_door_y, leaf, 90, 0, "oil")
    swing(X_EAST, e3_door_y, leaf, 90, 0, "facepack")
    swing(X_EAST, e2_door_y, leaf, 90, 0, "finished-door")

    # --- room titles, placed clear of swings and fixtures ---
    def title_block(bx, by, code, name, size_line):
        if code:
            btext(bx, by, code, f_tiny, MUTED, code + "-code")
            by -= 0.72
        btext(bx, by, name, f_room, INK, name)
        btext(bx, by - 0.84, size_line, f_tiny, DIM, name + "-size")

    title_block(16.5, 69.05, "W1 + E1", "RAW MATERIAL", "10'-0\" × 36'-0\"      360 sq ft")
    title_block(8.0, 58.85, "W2 – W4", "SOAP MAKING & CURING", "39'-6\" × 16'-0\"      632 sq ft")
    title_block(8.0, 19.55, "W5", "QUALITY CONTROL", "10'-0\" × 16'-0\"      160 sq ft")
    title_block(8.0, 9.45, "W6", "OFFICE", "10'-0\" × 16'-0\"      160 sq ft")
    title_block(28.2, 19.55, "E4 + E5", "OIL MAKING & FILLING", "20'-2\" × 16'-0\"      323 sq ft")
    title_block(28.0, 28.45, "", "GODOWN PATH", "9'-6\" × 16'-0\"      152 sq ft")
    btext(24.2, 24.35, "OPEN TO PATH", font(10), MUTED, "open-path")
    title_block(29.6, 39.15, "E3", "POWDER & FACEPACK", "10'-0\" × 16'-0\"      160 sq ft")
    # E2 title sits in the pocket west of the 6' swing and north of the 3'-6\" door swing.
    btext(25.7, 49.05, "E2", f_tiny, MUTED, "e2-code")
    btext(25.7, 48.1, "FINISHED", f_room, INK, "finished-1")
    btext(25.7, 47.15, "PRODUCT", f_room, INK, "finished-2")
    btext(25.7, 46.35, "160 sq ft", f_tiny, DIM, "finished-size")

    # D1 holds only its name. Door names sit in the larger rooms they open into.
    btext(30.2, 56.35, "D1", f_tiny, MUTED, "d1-code")
    btext(30.2, 55.3, "ENTRY", f_room, INK, "entry")
    btext(30.2, 54.25, "9'-6\" × 16'-0\"     152 sq ft", f_tiny, DIM, "entry-size")

    btext(raw_x + raw_w / 2, 66.85, "RAW IN   6'-0\"", font(11, True), RED, "tag-raw")
    btext(men_x + men_w / 2, 64.15, "MEN   3'-0\"", font(11, True), RED, "tag-men")
    btext(out_x + out_w / 2, 43.55, "OUT   6'-0\"", font(11, True), RED, "tag-out")
    btext(X_PATH + 2.0, path_y - 1.15, "4'-0\"", font(11, True), RED, "tag-path")

    paste_vertical(img, "CENTRAL PATH", font(13, True), MUTED, *P(X_PATH + 2.0, 34.2), boxes)

    # --- dimensions ---
    def hdim(x0_ft, x1_ft, sy, label, fnt):
        x0, x1 = P(x0_ft, 0)[0], P(x1_ft, 0)[0]
        tw = draw.textlength(label, font=fnt)
        mid = (x0 + x1) / 2
        gap = tw / 2 + 5
        if gap * 2 < (x1 - x0) - 8:
            draw.line([(x0, sy), (mid - gap, sy)], fill=DIM, width=1)
            draw.line([(mid + gap, sy), (x1, sy)], fill=DIM, width=1)
        else:
            draw.line([(x0, sy), (x1, sy)], fill=DIM, width=1)
        draw.line([(x0, sy - 4), (x0, sy + 4)], fill=DIM, width=1)
        draw.line([(x1, sy - 4), (x1, sy + 4)], fill=DIM, width=1)
        center(mid, sy - 11, label, fnt, DIM, label)

    def extension(sx, y_from, y_to):
        draw.line([(sx, y_from), (sx, y_to)], fill=(170, 166, 158), width=1)

    outer_top = oy - OUT * S
    for xft in (0, WEST, X_EAST, EW):
        extension(P(xft, NS)[0], outer_top - 2, outer_top - 62)
    hdim(0, WEST, oy - 36, "16'-0\"", f_dim)
    hdim(WEST, X_EAST, oy - 36, "4'-0\"", f_tiny)
    hdim(X_EAST, EW, oy - 36, "16'-0\"", f_dim)
    hdim(0, EW, oy - 64, "36'-0\"  INTERNAL", f_dim)
    compass = "WEST    ←——→    EAST"
    center(ox + plan_w / 2, oy - 92, compass, f_dim, DIM, "compass")

    def vchain(spans, xft):
        sx = P(xft, 0)[0]
        for y0, y1, label in spans:
            a, b = P(xft, y0), P(xft, y1)
            if abs(a[1] - b[1]) < 10:
                center(sx - 18, (a[1] + b[1]) / 2, label, font(9), DIM, label + f"@{y0:.1f}")
                continue
            draw.line([a, b], fill=DIM, width=1)
            draw.line([(a[0] - 4, a[1]), (a[0] + 4, a[1])], fill=DIM, width=1)
            draw.line([(b[0] - 4, b[1]), (b[0] + 4, b[1])], fill=DIM, width=1)
            bb = draw.textbbox((0, 0), label, font=f_tiny)
            tw = bb[2] - bb[0]
            stext(sx - tw - 8, (a[1] + b[1]) / 2 - 7, label, f_tiny, DIM, label + f"@{y0:.1f}")

    def spans_of(heights, labels):
        y = 0.0
        out = []
        for i, h in enumerate(heights):
            out.append((y, y + h, labels[i]))
            y += h
            if i < len(heights) - 1:
                out.append((y, y + PANEL, '2"'))
                y += PANEL
        return out

    vchain(spans_of([10, 10, 39.5, 10], ["10'-0\"", "10'-0\"", "39'-6\"", "10'-0\""]), -0.15)
    vchain(
        spans_of([20 + 2 / 12, 9.5, 10, 10, 9.5, 10], ["20'-2\"", "9'-6\"", "10'-0\"", "10'-0\"", "9'-6\"", "10'-0\""]),
        EW + 0.95,
    )
    # Overall height, outside the chain. SOUTH at the bottom, NORTH at the top.
    paste_vertical(img, "SOUTH      70'-0\"      NORTH", font(13, True), INK, ox - 168, oy + plan_h / 2, boxes)

    # North arrow
    nx, ny = ox + plan_w + 250, oy + 58
    draw.ellipse([nx - 24, ny - 24, nx + 24, ny + 24], outline=INK, width=2)
    draw.polygon([(nx, ny - 18), (nx - 8, ny + 2), (nx + 8, ny + 2)], fill=INK)
    draw.line([(nx, ny + 2), (nx, ny + 16)], fill=INK, width=2)
    center(nx, ny - 40, "N", font(16, True), INK, "north")

    # Door schedule and legend, to the right of the dimension chain.
    lx = ox + plan_w + 168
    ly = oy + 78
    stext(lx, ly, "DOOR SCHEDULE", font(13, True), INK, "door-head")
    schedule = [
        ("1", "3'-0\"", "Men entry", "D1 into raw material"),
        ("2", "6'-0\"", "Raw material in", "D1 into raw material"),
        ("3", "6'-0\"", "Finished out", "D1 into finished product"),
        ("4", "4'-0\"", "To central path", "Opens into the entry"),
        ("D1", "7'-0\"", "Rolling shutter", "East wall, entry"),
        ("D2", "7'-0\"", "Rolling shutter", "East wall, godown"),
        ("—", "3'-6\"", "Room doors", "Open into the room"),
    ]
    ly += 22
    for i, (mark, width, name, where) in enumerate(schedule):
        yy = ly + i * 36
        stext(lx, yy, mark, font(11, True), RED if mark != "—" else INK, f"sch-{mark}-{i}")
        stext(lx + 36, yy, width, f_tiny, INK, f"sch-w-{i}")
        stext(lx + 96, yy, name, f_tiny, INK, f"sch-n-{i}")
        stext(lx + 36, yy + 16, where, font(9), MUTED, f"sch-r-{i}")

    ly = ly + len(schedule) * 36 + 16
    stext(lx, ly, "LEGEND", font(13, True), INK, "legend-head")
    legend = [
        (STORE, "Stores"),
        (PROD, "Production"),
        (PACK, "Packing"),
        (LAB, "Office & lab"),
        (CIRC, "Circulation"),
    ]
    for i, (col, label) in enumerate(legend):
        yy = ly + 24 + i * 20
        draw.rectangle([lx, yy, lx + 18, yy + 13], fill=col, outline=WALL)
        stext(lx + 26, yy - 1, label, f_tiny, INK, "leg-" + label)
    yy = ly + 24 + len(legend) * 20 + 8
    draw.arc([lx, yy, lx + 16, yy + 16], 180, 270, fill=GREEN, width=2)
    stext(lx + 26, yy, "Door swing, into the room", f_tiny, INK, "leg-swing")
    yy += 22
    draw.rectangle([lx, yy + 2, lx + 16, yy + 12], outline=RED, width=2)
    stext(lx + 26, yy, "Rolling shutter", f_tiny, INK, "leg-shutter")
    yy += 22
    draw.rectangle([lx, yy + 3, lx + 16, yy + 11], fill=WALL)
    stext(lx + 26, yy, "Exterior wall, 9\"", f_tiny, INK, "leg-ext")
    yy += 22
    draw.rectangle([lx, yy + 5, lx + 16, yy + 9], fill=WALL)
    stext(lx + 26, yy, "Room panel, 2\"", f_tiny, INK, "leg-panel")
    yy += 22
    draw.line([(lx + 5, yy + 2), (lx + 5, yy + 12)], fill=GLASS, width=2)
    draw.line([(lx + 11, yy + 2), (lx + 11, yy + 12)], fill=GLASS, width=2)
    stext(lx + 26, yy, "Window, 4'-0\" × 3'-0\"", f_tiny, INK, "leg-win")

    # Graphic scale
    sx0, sy0 = 40, oy + plan_h + 28
    stext(sx0, sy0 - 18, "GRAPHIC SCALE", font(10, True), INK, "scale-h")
    runs = [5, 5, 10]
    x = sx0
    for i, feet_n in enumerate(runs):
        wpx = feet_n * S
        fill = INK if i % 2 == 0 else PAPER
        draw.rectangle([x, sy0, x + wpx, sy0 + 10], fill=fill, outline=INK)
        x += wpx
    for mark, label in ((0, "0"), (5, "5"), (10, "10"), (20, "20 ft")):
        mx = sx0 + mark * S
        draw.line([(mx, sy0 + 10), (mx, sy0 + 16)], fill=INK, width=1)
        center(mx, sy0 + 28, label, font(10), INK, "scale-" + label)

    # Room schedule and notes
    sched_top = oy + plan_h + 78
    stext(40, sched_top, "ROOM SCHEDULE", font(12, True), INK, "sched-head")
    rows = [
        ("Raw material", "36'-0\" × 10'-0\"", "360"),
        ("Soap making & curing", "39'-6\" × 16'-0\"", "632"),
        ("Quality control", "10'-0\" × 16'-0\"", "160"),
        ("Office", "10'-0\" × 16'-0\"", "160"),
        ("Oil making & filling", "20'-2\" × 16'-0\"", "323"),
        ("Powder & facepack", "10'-0\" × 16'-0\"", "160"),
        ("Finished product", "10'-0\" × 16'-0\"", "160"),
        ("D1 entry", "9'-6\" × 16'-0\"", "152"),
        ("Godown loading path", "9'-6\" × 16'-0\"", "152"),
        ("Central path", "4'-0\" × 60'-0\"", "240"),
    ]
    col_w = 430
    for i, (name, size, area) in enumerate(rows):
        col = i // 5
        row = i % 5
        x = 40 + col * col_w
        y = sched_top + 24 + row * 18
        stext(x, y, name, f_tiny, INK, "rm-" + name)
        stext(x + 210, y, size, font(10), DIM, "rmsz-" + name)
        stext(x + 360, y, area, font(10), INK, "rmar-" + name)
    stext(40, sched_top + 24 + 5 * 18 + 4, "Areas rounded to the nearest square foot.  2\" panels make up the rest of 2,520 sq ft.", font(10), MUTED, "sched-note")

    notes_top = sched_top + 24 + 5 * 18 + 28
    draw.rounded_rectangle([28, notes_top, W - 28, H - 18], radius=6, outline=(176, 172, 162), width=1)
    stext(42, notes_top + 8, "CONSTRUCTION NOTES", font(12, True), INK, "notes-head")
    notes = [
        "1.  Separators are 2\" (50 mm) panels — cement board, PUF or gypsum on a light frame. No masonry wall between rooms. The exterior wall is drawn at 9\" outside the internal dimensions.",
        "2.  East-west internal size closes exactly: 16'-0\" west rooms + 4'-0\" path + 16'-0\" east rooms = 36'-0\". Every occupied bay is 16'-0\" deep.",
        "3.  W2, W3 and W4 are one soap making and curing room. W5 is quality control. W6 is the office, with the owner’s seat facing east.",
        "4.  E4 and E5 are one oil making and filling room. E3 is powder and facepack. E2 is finished product. The godown loading path is open to the central path.",
        "5.  W1 and E1 are one raw-material room across the north, so the 4'-0\" path stops at that wall. From D1: 3'-0\" men door and 6'-0\" raw-material door into that room, 6'-0\" door into finished product, and 4'-0\" door onto the central path.",
        "6.  Unmarked doors are 3'-6\" × 7'-0\" and open into the room, clear of the path. D1 and D2 are 7'-0\" east-facing rolling shutters.",
        "7.  Floor: IPS / epoxy with 4\" coved skirting, graded to trapped gullies. No false ceiling. 12'-0\" clear to the purlins over soap and oil.",
        "8.  Windows are 4'-0\" × 3'-0\" on the west and east walls, with insect screens. Exhaust over the lye bench and over the cold press.",
        "9.  Toilet block is detached, minimum 25'-0\" clear of the north wall, and never opens into a production room. Hand wash is in the D1 entry.",
    ]
    max_w = W - 28 - 56
    ty = notes_top + 30
    for note in notes:
        for line in wrap(draw, note, f_note, max_w):
            stext(42, ty, line, f_note, INK, "note")
            ty += 15
        ty += 2

    overlaps = find_overlaps(boxes, swings)
    return img, overlaps


def wrap(draw, text, fnt, width):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def find_overlaps(boxes, swings):
    hits = []
    pad = 2

    def inflate(b):
        return b[0] - pad, b[1] - pad, b[2] + pad, b[3] + pad

    for i in range(len(boxes)):
        a_key, *a = boxes[i]
        ax0, ay0, ax1, ay1 = inflate(a)
        for j in range(i + 1, len(boxes)):
            b_key, *b = boxes[j]
            bx0, by0, bx1, by1 = inflate(b)
            ix = min(ax1, bx1) - max(ax0, bx0)
            iy = min(ay1, by1) - max(ay0, by0)
            if ix > 1 and iy > 1 and ix * iy > 12:
                hits.append(f"text '{a_key}' × '{b_key}' ({ix:.0f}×{iy:.0f})")
        for key, x0, y0, x1, y1 in swings:
            ix = min(ax1, x1) - max(ax0, x0)
            iy = min(ay1, y1) - max(ay0, y0)
            if ix > 2 and iy > 2 and ix * iy > 20:
                hits.append(f"text '{a_key}' × swing {key} ({ix:.0f}×{iy:.0f})")
    return hits


def paste_vertical(base, text, fnt, fill, cx, cy, boxes):
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bb = probe.textbbox((0, 0), text, font=fnt)
    tw, th = bb[2] - bb[0] + 4, bb[3] - bb[1] + 4
    chip = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(chip).text((2 - bb[0], 2 - bb[1]), text, font=fnt, fill=fill + (255,))
    rot = chip.rotate(90, expand=True, resample=Image.Resampling.BICUBIC)
    x, y = int(cx - rot.width / 2), int(cy - rot.height / 2)
    base.alpha_composite(rot, (x, y))
    boxes.append((text, x, y, x + rot.width, y + rot.height))


def save_pdf(img: Image.Image, path: Path) -> None:
    page = portrait((11 * inch, 17 * inch))
    pw, ph = page
    c = canvas.Canvas(str(path), pagesize=page)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    scale = min((pw - 28) / img.width, (ph - 28) / img.height)
    dw, dh = img.width * scale, img.height * scale
    c.drawImage(ImageReader(buf), (pw - dw) / 2, (ph - dh) / 2, width=dw, height=dh)
    c.setAuthor("Parambu Organics")
    c.setTitle("Parambu — Soap & Oil Unit Floor Plan")
    c.save()


if __name__ == "__main__":
    main()
