#!/usr/bin/env python3
"""Recreate the Parambu soap & oil unit floor plan sheet."""

from __future__ import annotations

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

S = 22
WHITE = (255, 255, 255)
INK = (36, 44, 54)
MUTED = (90, 96, 100)
DIM = (70, 78, 86)
GREEN = (36, 122, 72)
RED = (176, 56, 48)
WALL = (36, 46, 58)

STORE = (250, 241, 218)
PROD = (227, 241, 228)
PACK = (227, 237, 249)
LAB = (242, 231, 247)
CIRC = (232, 236, 239)

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


# South to north, so the last entry is the north room.
WEST_H = [10, 10, 19 + 2 / 12, 10, 10, 10]  # W6 W5 W4 W3 W2 W1
EAST_H = [10, 10, 9.5, 10, 10, 9.5, 10]      # E5 E4 godown E3 E2 entry E1
WEST_Y = stack(WEST_H)
EAST_Y = stack(EAST_H)


def main() -> None:
    img = render()
    rgb = img.convert("RGB")
    rgb.save(OUTPUT_PNG, "PNG", dpi=(150, 150))
    save_pdf(rgb, OUTPUT_PDF)
    print(f"Wrote {OUTPUT_PNG}")
    print(f"Wrote {OUTPUT_PDF}")


def render() -> Image.Image:
    f_title = font(22, True)
    f_sub = font(12)
    f_tiny = font(10)
    f_room = font(13, True)
    f_eq = font(9)
    f_dim = font(11)

    plan_w, plan_h = int(EW * S), int(NS * S)
    ml, mr, mt, mb = 168, 300, 128, 248
    W, H = ml + plan_w + mr, mt + plan_h + mb
    img = Image.new("RGBA", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    ox, oy = ml, mt

    def P(x: float, y: float) -> tuple[float, float]:
        return ox + x * S, oy + (NS - y) * S

    def rect(x, y, w, h, fill):
        x1, y1 = P(x, y + h)
        x2, y2 = P(x + w, y)
        d.rectangle([x1, y1, x2, y2], fill=fill)

    def seg(x1, y1, x2, y2, width=3):
        d.line([P(x1, y1), P(x2, y2)], fill=WALL, width=width)

    d.text((36, 22), "PARAMBU  —  SOAP & OIL UNIT", fill=INK, font=f_title)
    d.text((36, 50), "FLOOR PLAN   36'-0\"  ×  70'-0\"  =  2,520 SQ FT    ·    EAST FACING", fill=INK, font=f_sub)
    d.text((36, 70), "W2–W4 joined soap & curing   ·   E4–E5 joined oil   ·   W1+E1 raw material, no path   ·   2\" panels", fill=MUTED, font=f_tiny)
    d.line([(36, 92), (W - 36, 92)], fill=(190, 184, 170), width=2)

    wy = {code: WEST_Y[i] for i, code in enumerate(["W6", "W5", "W4", "W3", "W2", "W1"])}
    ey = {code: EAST_Y[i] for i, code in enumerate(["E5", "E4", "GD", "E3", "E2", "EN", "E1"])}
    y_raw = wy["W1"][0]
    soap_y, soap_h = wy["W4"][0], (wy["W2"][0] + wy["W2"][1]) - wy["W4"][0]
    oil_y, oil_h = ey["E5"][0], (ey["E4"][0] + ey["E4"][1]) - ey["E5"][0]

    # Joined fills. The north 10' is one raw-material room across the full 36'.
    rect(0, wy["W6"][0], WEST, wy["W6"][1], LAB)
    rect(0, wy["W5"][0], WEST, wy["W5"][1], LAB)
    rect(0, soap_y, WEST, soap_h, PROD)
    rect(0, y_raw, EW, wy["W1"][1], STORE)
    rect(X_EAST, oil_y, EAST, oil_h, PROD)
    rect(X_EAST, ey["GD"][0], EAST, ey["GD"][1], CIRC)
    rect(X_EAST, ey["E3"][0], EAST, ey["E3"][1], PACK)
    rect(X_EAST, ey["E2"][0], EAST, ey["E2"][1], STORE)
    rect(X_EAST, ey["EN"][0], EAST, ey["EN"][1], CIRC)
    rect(X_PATH, 0, PATH, y_raw, CIRC)

    def panel_at(xs, xe, y):
        seg(xs, y, xe, y, 3)

    # Panels that remain. Joins omit the walls inside soap, inside oil, and across the north band.
    panel_at(0, WEST, wy["W5"][0])
    panel_at(0, WEST, soap_y)
    panel_at(0, EW, y_raw)
    panel_at(X_EAST, EW, oil_y + oil_h)
    panel_at(X_EAST, EW, ey["E3"][0])
    panel_at(X_EAST, EW, ey["E2"][0])
    panel_at(X_EAST, EW, ey["EN"][0])

    # Path walls stop at the raw-material band. Godown stays open to the path.
    seg(X_PATH, 0, X_PATH, y_raw, 3)
    seg(X_EAST, 0, X_EAST, ey["GD"][0], 3)
    seg(X_EAST, ey["GD"][0] + ey["GD"][1], X_EAST, y_raw, 3)

    # Exterior
    seg(0, 0, EW, 0, 4)
    seg(0, NS, EW, NS, 4)
    seg(0, 0, 0, NS, 4)
    seg(EW, 0, EW, NS, 4)

    card(d, P, "W1 + E1", "RAW MATERIAL ROOM", "joined across the north  ·  no 4' path",
         "10'-0\" × 36'-0\"", "360 sq ft", 0, y_raw, wy["W1"][1], EW,
         [("RACK", "RACK", "WEIGHING"), ("RACK", "RACK", "SAMPLING")], f_room, f_tiny, f_eq)
    card(d, P, "W2–W4", "SOAP MAKING & CURING", "mixer  ·  moulds  ·  curing racks",
         "39'-6\" × 16'-0\"", "632 sq ft", 0, soap_y, soap_h, WEST,
         [("MIXER / KETTLE", "MOULD TABLE", "CUTTER"),
          ("LYE MIXING", "CURING RACK", "CURING RACK"),
          ("CURING RACK", "SOAP WRAP", "CARTONING")], f_room, f_tiny, f_eq)
    card(d, P, "W5", "QUALITY CONTROL", "testing  ·  retained samples",
         "10'-0\" × 16'-0\"", "160 sq ft", 0, *wy["W5"], WEST,
         [("LAB BENCH", "SINK & WASH"), ("INSTRUMENTS", "SAMPLE CUPBOARD")], f_room, f_tiny, f_eq)
    card(d, P, "W6", "OFFICE", "records  ·  owner seat faces east",
         "10'-0\" × 16'-0\"", "160 sq ft", 0, *wy["W6"], WEST,
         [("DESK", "VISITOR", "RECORD CABINET",)], f_room, f_tiny, f_eq)

    card(d, P, "", "ENTRY / LOADING  ·  D1", "doors to raw material, finished goods, and the path",
         "9'-6\" × 16'-0\"", "152 sq ft", X_EAST, *ey["EN"], EAST,
         [("HAND WASH",)], f_room, f_tiny, f_eq)
    card(d, P, "E2", "FINISHED PRODUCT", "packed goods out  ·  6' door from D1",
         "10'-0\" × 16'-0\"", "160 sq ft", X_EAST, *ey["E2"], EAST,
         [("PALLET RACK", "PALLET RACK", "PALLET RACK"), ("DISPATCH STAGING",)], f_room, f_tiny, f_eq)
    card(d, P, "E3", "POWDER & FACEPACK", "mixer  ·  mill  ·  filling",
         "10'-0\" × 16'-0\"", "160 sq ft", X_EAST, *ey["E3"], EAST,
         [("MIXER", "POWDER MILL"), ("SIFTER", "FILLING / JARS")], f_room, f_tiny, f_eq)
    card(d, P, "", "GODOWN LOADING PATH", "",
         "9'-6\" × 16'-0\"", "152 sq ft", X_EAST, *ey["GD"], EAST,
         [], f_room, f_tiny, f_eq)
    card(d, P, "E4 + E5", "OIL MAKING & FILLING", "press  ·  tanks  ·  filling line",
         "20'-2\" × 16'-0\"", "323 sq ft", X_EAST, oil_y, oil_h, EAST,
         [("COLD PRESS", "FILTER PRESS"), ("T1  T2  T3  T4  T5",),
          ("FILLING", "CAPPING", "LABELLING")], f_room, f_tiny, f_eq)

    # Path doors for the closed rooms that still open onto the path.
    swing(d, P, X_PATH, soap_y + soap_h * 0.45, 3.5, into="west")
    swing(d, P, X_PATH, wy["W5"][0] + 3.0, 3.5, into="west")
    swing(d, P, X_PATH, wy["W6"][0] + 3.0, 3.5, into="west")
    swing(d, P, X_EAST, ey["E3"][0] + 3.0, 3.5, into="east")
    swing(d, P, X_EAST, oil_y + 6.0, 3.5, into="east")
    swing(d, P, X_EAST, ey["E2"][0] + 3.0, 3.5, into="east")

    # From the D1 entry: two doors north into the raw-material room (E1),
    # a 6' door south into finished product (E2), and a door west onto the path.
    en_y, en_h = ey["EN"]
    swing_h(d, P, 31.5, y_raw, 3.0, into="north")
    tag(d, P, 33.0, en_y + en_h - 1.3, "3'-0\" MEN ENTRY", f_tiny)
    swing_h(d, P, 21.5, y_raw, 6.0, into="north")
    tag(d, P, 24.5, en_y + en_h - 1.3, "6'-0\" RAW MATERIAL", f_tiny)
    swing_h(d, P, 25.0, en_y, 6.0, into="south")
    tag(d, P, 28.0, en_y + 1.5, "6'-0\" FINISHED OUT", f_tiny)
    swing(d, P, X_EAST, en_y + 2.6, 4.0, into="west")
    tag(d, P, X_EAST + 6.5, en_y + 4.5, "DOOR TO CENTRAL PATH", f_tiny)

    # East shutters, centered in each loading path
    for key, label in (("EN", "D1"), ("GD", "D2")):
        y, h = ey[key]
        east_door(d, P, y + (h - 7) / 2, 7.0, f"{label}  ·  7'-0\" DOOR", "FACING EAST", f_tiny)

    paste_vertical(img, "CENTRAL PATH    4'-0\"  ×  60'-0\"", font(12, True), MUTED,
                   ox + (X_PATH + PATH / 2) * S, oy + (NS - 30) * S)

    # Header dimensions
    screen_hdim(d, ox, ox + plan_w, oy - 28, "36'-0\"", f_dim)
    screen_hdim(d, ox, ox + WEST * S, oy - 54, "16'-0\"  WEST BAY", f_tiny)
    screen_hdim(d, ox + WEST * S, ox + X_EAST * S, oy - 54, "4'-0\"", f_tiny)
    screen_hdim(d, ox + X_EAST * S, ox + plan_w, oy - 54, "16'-0\"  EAST BAY", f_tiny)
    compass = "WEST    ←——→    EAST"
    tw = d.textlength(compass, font=f_dim)
    d.text((ox + plan_w / 2 - tw / 2, oy - 78), compass, fill=DIM, font=f_dim)

    # Side chains
    def chain(zones, labels, x, side):
        y = 0.0
        spans = []
        for i, h in enumerate(zones):
            spans.append((y, y + h, labels[i]))
            y += h
            if i < len(zones) - 1:
                spans.append((y, y + PANEL, '2"'))
                y += PANEL
        draw_v_chain(d, P, spans, x, f_tiny, side)

    chain(
        [10, 10, 39.5, 10],
        ["10'-0\"  OFFICE", "10'-0\"  QC", "39'-6\"  SOAP", "10'-0\"  RAW"],
        -0.45, "left",
    )
    chain(
        [20 + 2 / 12, 9.5, 10, 10, 9.5, 10],
        ["20'-2\"  OIL", "9'-6\"", "10'-0\"  FP", "10'-0\"  FIN", "9'-6\"  D1", "10'-0\"  RAW"],
        EW + 0.4, "right",
    )
    paste_vertical(img, "70'-0\"      NORTH   ↓   SOUTH", font(12, True), INK, ox - 128, oy + plan_h / 2)

    # North arrow
    nx, ny = 70, oy + 28
    d.polygon([(nx, ny - 36), (nx - 13, ny + 8), (nx + 13, ny + 8)], fill=INK)
    d.rectangle([nx - 4, ny + 8, nx + 4, ny + 28], fill=INK)
    d.text((nx - 8, ny - 56), "N", fill=INK, font=font(16, True))

    # Legend, lower right of the sheet margin
    lx, ly = ox + plan_w + 108, oy + plan_h - 230
    d.text((lx, ly), "LEGEND", fill=INK, font=font(12, True))
    legend = [
        (STORE, "Stores"),
        (PROD, "Production"),
        (PACK, "Packing"),
        (LAB, "Office & lab"),
        (CIRC, "Circulation"),
    ]
    for i, (col, label) in enumerate(legend):
        y = ly + 22 + i * 18
        d.rectangle([lx, y, lx + 16, y + 12], fill=col, outline=WALL)
        d.text((lx + 22, y - 1), label, fill=INK, font=f_tiny)
    y = ly + 22 + len(legend) * 18 + 6
    d.arc([lx, y, lx + 14, y + 14], 180, 270, fill=GREEN, width=2)
    d.text((lx + 22, y), "Internal door  3'-6\"", fill=INK, font=f_tiny)
    y += 18
    d.line([(lx, y + 6), (lx + 16, y + 6)], fill=RED, width=3)
    d.text((lx + 22, y), "East door  7'-0\"", fill=INK, font=f_tiny)
    y += 18
    d.line([(lx, y + 6), (lx + 16, y + 6)], fill=WALL, width=3)
    d.text((lx + 22, y), "2\" room panel", fill=INK, font=f_tiny)

    # Notes
    box = [28, oy + plan_h + 36, W - 28, H - 16]
    d.rounded_rectangle(box, radius=6, outline=(176, 176, 172), width=1)
    d.text((42, box[1] + 8), "CONSTRUCTION NOTES", fill=INK, font=font(11, True))
    notes = [
        '1.  Room separators are 2" (50 mm) panels — cement board / PUF / gypsum on a light frame. No masonry wall between rooms.',
        '2.  East-west closes exactly: 16\'-0" west rooms + 4\'-0" path + 16\'-0" east rooms = 36\'-0". Every room is 16\'-0" deep.',
        '3.  W2, W3 and W4 are one soap making and curing room. W5 is the QC room. W6 remains the office.',
        '4.  E4 and E5 are one oil making and filling room. E3 is powder and facepack. E2 is finished product.',
        '5.  W1 and E1 are one raw-material room across the north; the 4\' path stops there. From D1: 3\' men door and raw-material door into E1, 6\' door into E2, and a door onto the central path.',
        '6.  Floor: IPS / epoxy with 4" coved skirting, graded to trapped gullies. Ceiling 12\'-0" clear over soap and oil rooms.',
        '7.  Windows 4\'-0" × 3\'-0" on the west and east walls with insect screens; exhaust fan over the lye mixing bench and over the cold press.',
        '8.  Toilet block detached, minimum 25\'-0" clear of the north wall, never opening into a production room. Hand wash at the D1 entry path.',
    ]
    ty = box[1] + 28
    for line in notes:
        d.text((42, ty), line, fill=INK, font=font(10))
        ty += 16
    return img


def card(d, P, code, title, subtitle, size, area, x, y, h, w, rows, f_room, f_tiny, f_eq):
    x1, y1 = P(x, y + h)
    x2, y2 = P(x + w, y)
    cx = (x1 + x2) / 2
    top = y1 + 8
    label = f"{code}   {title}" if code else title
    tw = d.textlength(label, font=f_room)
    d.text((cx - tw / 2, top), label, fill=INK, font=f_room)
    top += 16
    if subtitle:
        tw = d.textlength(subtitle, font=f_tiny)
        d.text((cx - tw / 2, top), subtitle, fill=MUTED, font=f_tiny)
        top += 13
    size_line = f"{size}     {area}"
    tw = d.textlength(size_line, font=f_tiny)
    d.text((cx - tw / 2, top), size_line, fill=DIM, font=f_tiny)
    if not rows:
        return
    inner_top = top + 18
    inner_bot = y2 - 8
    if inner_bot - inner_top < 14:
        return
    row_h = (inner_bot - inner_top) / len(rows)
    pad = 8
    for r, items in enumerate(rows):
        cell = ((x2 - x1) - pad * 2) / len(items)
        cy = inner_top + r * row_h + row_h / 2
        for c, text in enumerate(items):
            ccx = x1 + pad + c * cell + cell / 2
            tw = d.textlength(text, font=f_eq)
            bw = min(cell - 6, tw + 12)
            d.rounded_rectangle([ccx - bw / 2, cy - 8, ccx + bw / 2, cy + 8], radius=3, fill=WHITE, outline=(186, 186, 182))
            d.text((ccx - tw / 2, cy - 6), text, fill=INK, font=f_eq)


def tanks(d, P, y, h, f_eq):
    """Five settling tanks across W3, under the room title."""
    labels = ["T1", "T2", "T3", "T4", "T5"]
    cy = y + h * 0.38
    for i, lab in enumerate(labels):
        cx = 1.6 + i * 2.7
        x, yy = P(cx, cy)
        r = 16
        d.ellipse([x - r, yy - r, x + r, yy + r], outline=INK, width=2)
        tw = d.textlength(lab, font=f_eq)
        d.text((x - tw / 2, yy - 6), lab, fill=INK, font=f_eq)
    x, yy = P(WEST / 2, y + 1.3)
    text = "TRANSFER PUMP & FILTER LINE"
    tw = d.textlength(text, font=f_eq)
    d.rounded_rectangle([x - tw / 2 - 6, yy - 8, x + tw / 2 + 6, yy + 8], radius=3, fill=WHITE, outline=(186, 186, 182))
    d.text((x - tw / 2, yy - 6), text, fill=INK, font=f_eq)


def swing_h(d, P, x, wall_y, width, into):
    """Door in a north-south wall. `into` is the room the leaf opens toward."""
    x0, y = P(x, wall_y)
    x1, _ = P(x + width, wall_y)
    d.rectangle([x0, y - 4, x1, y + 4], fill=WHITE)
    span = x1 - x0
    if into == "north":
        d.arc([x0, y - span, x1, y], 0, 90, fill=GREEN, width=2)
    else:
        d.arc([x0, y, x1, y + span], 270, 360, fill=GREEN, width=2)


def tag(d, P, x, y, text, fnt):
    sx, sy = P(x, y)
    tw = d.textlength(text, font=fnt)
    d.text((sx - tw / 2, sy), text, fill=RED, font=fnt)


def swing(d, P, wall_x, y, width, into):
    _, y_s = P(wall_x, y)
    x, y_n = P(wall_x, y + width)
    span = y_s - y_n
    if into == "east":
        d.rectangle([x - 2, y_n, x + 4, y_s], fill=WHITE)
        d.arc([x, y_n, x + span, y_s], 270, 360, fill=GREEN, width=2)
    else:
        d.rectangle([x - 4, y_n, x + 2, y_s], fill=WHITE)
        d.arc([x - span, y_n, x, y_s], 180, 270, fill=GREEN, width=2)


def east_door(d, P, y, width, line1, line2, fnt):
    x, y_s = P(EW, y)
    _, y_n = P(EW, y + width)
    d.rectangle([x - 4, y_n, x + 4, y_s], fill=WHITE, outline=RED, width=2)
    mid = (y_n + y_s) / 2
    d.line([(x + 4, mid), (x + 86, mid)], fill=RED, width=2)
    d.polygon([(x + 86, mid - 4), (x + 94, mid), (x + 86, mid + 4)], fill=RED)
    d.text((x + 100, mid - 14), line1, fill=RED, font=fnt)
    d.text((x + 100, mid), line2, fill=RED, font=fnt)


def screen_hdim(d, x0, x1, y, label, fnt):
    d.line([(x0, y), (x1, y)], fill=DIM, width=1)
    d.line([(x0, y - 4), (x0, y + 4)], fill=DIM, width=1)
    d.line([(x1, y - 4), (x1, y + 4)], fill=DIM, width=1)
    tw = d.textlength(label, font=fnt)
    d.text(((x0 + x1) / 2 - tw / 2, y - 13), label, fill=DIM, font=fnt)


def draw_v_chain(d, P, spans, x, fnt, side):
    for y0, y1, label in spans:
        a, b = P(x, y0), P(x, y1)
        if abs(a[1] - b[1]) < 8:
            # 2" panel — label only, the tick is too short to draw
            my = (a[1] + b[1]) / 2
            if side == "left":
                tw = d.textlength(label, font=fnt)
                d.text((a[0] - tw - 4, my - 6), label, fill=DIM, font=fnt)
            else:
                d.text((a[0] + 4, my - 6), label, fill=DIM, font=fnt)
            continue
        d.line([a, b], fill=DIM, width=1)
        d.line([(a[0] - 3, a[1]), (a[0] + 3, a[1])], fill=DIM, width=1)
        d.line([(b[0] - 3, b[1]), (b[0] + 3, b[1])], fill=DIM, width=1)
        my = (a[1] + b[1]) / 2
        if side == "left":
            tw = d.textlength(label, font=fnt)
            d.text((a[0] - tw - 6, my - 6), label, fill=DIM, font=fnt)
        else:
            d.text((a[0] + 6, my - 6), label, fill=DIM, font=fnt)


def paste_vertical(base, text, fnt, fill, cx, cy):
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bbox = tmp.textbbox((0, 0), text, font=fnt)
    tw, th = bbox[2] - bbox[0] + 4, bbox[3] - bbox[1] + 4
    chip = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(chip).text((2 - bbox[0], 2 - bbox[1]), text, font=fnt, fill=fill + (255,))
    rot = chip.rotate(90, expand=True, resample=Image.Resampling.BICUBIC)
    base.alpha_composite(rot, (int(cx - rot.width / 2), int(cy - rot.height / 2)))


def save_pdf(img: Image.Image, path: Path) -> None:
    page = portrait((11 * inch, 17 * inch))
    pw, ph = page
    c = canvas.Canvas(str(path), pagesize=page)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    scale = min((pw - 24) / img.width, (ph - 24) / img.height)
    dw, dh = img.width * scale, img.height * scale
    c.drawImage(ImageReader(buf), (pw - dw) / 2, (ph - dh) / 2, width=dw, height=dh)
    c.setAuthor("Parambu Organics")
    c.setTitle("Parambu — Soap & Oil Unit Floor Plan")
    c.save()


if __name__ == "__main__":
    main()
