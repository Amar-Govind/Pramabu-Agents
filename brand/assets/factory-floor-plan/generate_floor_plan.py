#!/usr/bin/env python3
"""Parambu factory floor plan in the reference sheet style, revised layout."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, portrait
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
OUTPUT_PNG = REPO / "floor-plan.png"
OUTPUT_PDF = REPO / "floor-plan.pdf"

# Feet
EW, NS = 36.0, 70.0
WEST, PATH, EAST = 16.0, 4.0, 16.0
PANEL = 2.0 / 12.0
X_PATH, X_EAST = WEST, WEST + PATH

OFFICE_H, QC_H = 10.0, 10.0
SOAP_H = 41.0 + 8.0 / 12.0          # W2–W4
NORTH_H = 8.0                       # W1 + raw material join
OIL_H = 25.0 + 4.0 / 12.0           # E-S, sized so the east stack is 70'-0"
FP_H, PACK_H, OPEN_H = 10.0, 16.0, 10.0
MEN_W = 6.0

# South-origin elevations
Y_OFFICE = 0.0
Y_QC = OFFICE_H + PANEL
Y_SOAP = Y_QC + QC_H + PANEL
Y_NORTH = Y_SOAP + SOAP_H           # 62'-0"

Y_OIL = 0.0
Y_FP = OIL_H + PANEL
Y_PACK = Y_FP + FP_H + PANEL
Y_OPEN = Y_PACK + PACK_H + PANEL
Y_NORTH_E = Y_OPEN + OPEN_H + PANEL

assert abs(Y_NORTH - 62.0) < 1e-6, Y_NORTH
assert abs(Y_NORTH_E - 62.0) < 1e-6, Y_NORTH_E
assert abs(Y_NORTH + NORTH_H - NS) < 1e-6

S = 26  # px per foot
WHITE = (255, 255, 255)
INK = (35, 40, 38)
MUTED = (90, 96, 92)
DIM = (70, 74, 72)
GREEN = (36, 130, 72)
RED = (196, 42, 42)
PANEL_C = (45, 45, 45)
WALL_C = (25, 25, 25)

FILL = {
    "soap": (226, 236, 214),
    "oil": (214, 228, 238),
    "face": (214, 228, 238),
    "pack": (214, 232, 216),
    "open": (236, 242, 220),
    "raw": (244, 234, 210),
    "lab": (230, 224, 238),
    "path": (255, 255, 255),
}

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(str(FONT_DIR / name), size)


def feet_label(v: float) -> str:
    whole = int(round(v * 12))
    f, i = divmod(whole, 12)
    return f"{f}'-{i}\""


def main() -> None:
    img = render()
    img.convert("RGB").save(OUTPUT_PNG, "PNG", dpi=(150, 150))
    save_pdf(img.convert("RGB"), OUTPUT_PDF)
    print(f"Wrote {OUTPUT_PNG}")
    print(f"Wrote {OUTPUT_PDF}")


def render() -> Image.Image:
    f_title = font(26, True)
    f_sub = font(13)
    f_room = font(15, True)
    f_small = font(11)
    f_tiny = font(10)
    f_equip = font(9)
    f_dim = font(11)
    f_code = font(13, True)

    plan_w, plan_h = int(EW * S), int(NS * S)
    ml, mr, mt, mb = 190, 280, 250, 340
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

    def seg(x1, y1, x2, y2, fill=WALL_C, width=3):
        d.line([P(x1, y1), P(x2, y2)], fill=fill, width=width)

    # Title
    title = "PARAMBU  —  SOAP, OIL, FACEPACK & POWDER"
    sub = "FLOOR PLAN   36'-0\"  ×  70'-0\"  =  2,520 SQ FT    ·    EAST FACING"
    note = "W1–W4 joined as soap  ·  E-S is oil  ·  north band joins raw material to W1 (no 4' path)  ·  2\" panels  ·  no false ceiling"
    d.text((40, 28), title, fill=INK, font=f_title)
    d.text((40, 64), sub, fill=INK, font=f_sub)
    d.text((40, 86), note, fill=MUTED, font=f_tiny)
    d.line([(40, 110), (W - 40, 110)], fill=(180, 170, 150), width=2)

    # Fills
    rect(0, Y_SOAP, WEST, SOAP_H + NORTH_H, FILL["soap"])          # soap through W1 to north wall
    rect(X_PATH, Y_NORTH, EW - X_PATH - MEN_W, NORTH_H, FILL["raw"])
    rect(EW - MEN_W, Y_NORTH, MEN_W, NORTH_H, FILL["lab"])
    rect(0, Y_QC, WEST, QC_H, FILL["lab"])
    rect(0, Y_OFFICE, WEST, OFFICE_H, FILL["lab"])
    rect(X_EAST, Y_OIL, EAST, OIL_H, FILL["oil"])
    rect(X_EAST, Y_FP, EAST, FP_H, FILL["face"])
    rect(X_EAST, Y_PACK, EAST, PACK_H, FILL["pack"])
    rect(X_EAST, Y_OPEN, EAST, OPEN_H, FILL["open"])
    rect(X_PATH, 0, PATH, Y_NORTH, FILL["path"])

    # Exterior
    seg(0, 0, EW, 0, width=4)
    seg(0, NS, EW, NS, width=4)
    seg(0, 0, 0, NS, width=4)
    seg(EW, 0, EW, NS, width=4)

    # Path edges, stopping at the north band
    seg(X_PATH, 0, X_PATH, Y_NORTH, width=3)
    seg(X_EAST, 0, X_EAST, Y_NORTH, width=3)
    # North band south wall — open on the west (soap/W1 join), closed from the path eastward
    seg(X_PATH, Y_NORTH, EW, Y_NORTH, width=3)
    # Men-change partition
    seg(EW - MEN_W, Y_NORTH, EW - MEN_W, NS, width=3)

    def panel(x1, y1, x2, y2):
        seg(x1, y1, x2, y2, PANEL_C, 4)
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        sx, sy = P(mx, my)
        d.text((sx - 8, sy - 14), '2"', fill=DIM, font=f_tiny)

    panel(0, Y_QC - PANEL, WEST, Y_QC - PANEL)             # office / QC  (line sits on the panel zone)
    panel(0, Y_SOAP - PANEL, WEST, Y_SOAP - PANEL)         # QC / soap
    panel(X_EAST, Y_FP - PANEL, EW, Y_FP - PANEL)          # oil / facepack
    panel(X_EAST, Y_PACK - PANEL, EW, Y_PACK - PANEL)      # facepack / packing
    panel(X_EAST, Y_OPEN - PANEL, EW, Y_OPEN - PANEL)      # packing / open

    # Room cards
    card(d, P, "W1–W4", "SOAP MAKING, CURING & PACKING",
         "W1–W4 joined  ·  open north into raw material",
         f"{feet_label(SOAP_H + NORTH_H)} × 16'-0\"", "795 sq ft",
         0, Y_SOAP, WEST, SOAP_H, f_code, f_room, f_tiny,
         [("MIXER / KETTLE", "MOULD TABLE", "CUTTER"),
          ("LYE MIXING", "CURING RACK", "CURING RACK"),
          ("CURING RACK", "SOAP WRAP", "CARTONING")],
         f_equip, header_from_top=36)

    card(d, P, "W1", "JOINED WITH RAW MATERIAL",
         "no 4'-0\" path",
         "8'-0\" × 16'-0\"", "",
         0, Y_NORTH, WEST, NORTH_H, f_code, font(12, True), f_tiny,
         [], f_equip, header_from_top=28)

    card(d, P, "", "RAW MATERIAL",
         "joins W1  ·  6' north door",
         "14'-0\" × 8'-0\"", "",
         X_PATH, Y_NORTH, EW - X_PATH - MEN_W, NORTH_H, f_code, font(12, True), f_tiny,
         [("RACK", "RACK"), ("WEIGHING",)], f_equip, header_from_top=28)

    card(d, P, "", "MEN CHANGE\n& SAFETY",
         "safety kit",
         "6' × 8'", "48 sq ft",
         EW - MEN_W, Y_NORTH, MEN_W, NORTH_H, f_code, font(11, True), f_tiny,
         [("LOCKERS",), ("SAFETY KIT",)], f_equip, header_from_top=28)

    card(d, P, "W5", "QUALITY CONTROL LAB",
         "testing  ·  retained samples",
         "10'-0\" × 16'-0\"", "160 sq ft",
         0, Y_QC, WEST, QC_H, f_code, f_room, f_tiny,
         [("LAB BENCH", "SINK & WASH"), ("INSTRUMENTS", "SAMPLES")],
         f_equip)

    card(d, P, "W6", "OFFICE",
         "records  ·  owner seat faces east",
         "10'-0\" × 16'-0\"", "160 sq ft",
         0, Y_OFFICE, WEST, OFFICE_H, f_code, f_room, f_tiny,
         [("DESK", "VISITOR"), ("RECORD CABINET",)],
         f_equip)

    card(d, P, "E-S", "OIL MAKING, STORAGE & FILLING",
         "press  ·  5 tanks  ·  filling line",
         f"{feet_label(OIL_H)} × 16'-0\"", "405 sq ft",
         X_EAST, Y_OIL, EAST, OIL_H, f_code, f_room, f_tiny,
         [("COLD PRESS", "FILTER PRESS"),
          ("COLLECTION TANK", "T1  T2  T3  T4  T5"),
          ("FILLING", "CAPPING", "LABELLING"),
          ("TRANSFER PUMP", "SEED FEED", "CAKE BIN")],
         f_equip)

    card(d, P, "", "FACEPACK & POWDER",
         "mixer  ·  mill  ·  filling",
         "10'-0\" × 16'-0\"", "160 sq ft",
         X_EAST, Y_FP, EAST, FP_H, f_code, font(13, True), f_tiny,
         [("MIXER", "POWDER MILL"), ("SIFTER", "FILLING / JARS")],
         f_equip)

    card(d, P, "", "PACKING",
         "coding  ·  cartoning  ·  staging",
         "16'-0\" × 16'-0\"", "256 sq ft",
         X_EAST, Y_PACK, EAST, PACK_H, f_code, f_room, f_tiny,
         [("PACKING TABLE", "PACKING TABLE"),
          ("CODING / SEAL", "CARTONING"),
          ("STAGING", "SHRINK / TAPE")],
         f_equip)

    card(d, P, "", "OPEN",
         "10' open after the 7' east door",
         "10'-0\" × 16'-0\"", "160 sq ft",
         X_EAST, Y_OPEN, EAST, OPEN_H, f_code, f_room, f_tiny,
         [("EMPTY CARTONS", "PALLET STAGING"), ("DISPATCH PREP",)],
         f_equip)

    # Path label, rotated
    paste_vertical(img, "CENTRAL PATH", font(12, True), MUTED,
                   ox + (X_PATH + PATH / 2) * S, oy + (NS - Y_NORTH / 2) * S - 20)
    paste_vertical(img, "4'-0\"  ×  62'-0\"", font(11), MUTED,
                   ox + (X_PATH + PATH / 2) * S, oy + (NS - Y_NORTH / 2) * S + 150)

    # Doors — green internal swings into the room, red exterior callouts
    swing_into_west_room(d, P, Y_OFFICE + 3.2, 3.5)
    swing_into_west_room(d, P, Y_QC + 3.2, 3.5)
    swing_into_west_room(d, P, Y_SOAP + 18, 3.5)
    swing_into_east_room(d, P, Y_OIL + 8, 3.5)
    swing_into_east_room(d, P, Y_FP + 4.6, 3.5)
    swing_into_east_room(d, P, Y_PACK + 6, 3.5)

    # 4'-0" door in the wall immediately north of oil (east wall of facepack's south end)
    east_door(d, P, Y_FP + 0.4, 4.0, "4'-0\" DOOR", "NORTH OF OIL", f_tiny)
    # 7'-0" door into the open dock, on the east wall just north of packing
    east_door(d, P, Y_OPEN + 0.4, 7.0, "7'-0\" DOOR", "FACING EAST", f_tiny)

    # North doors. Labels sit inside the rooms, under the openings.
    north_door(d, P, 21.0, 6.0, "6'-0\" RAW MATERIAL", f_tiny)
    north_door(d, P, 31.5, 3.0, "3'-0\" MEN", f_tiny)

    # Overall dimensions, stacked clear of the title rule and the north wall.
    wall_top = oy
    screen_hdim(d, ox, ox + plan_w, wall_top - 36, "36'-0\"", f_dim)
    screen_hdim(d, ox, ox + WEST * S, wall_top - 68, "16'-0\" WEST BAY", f_tiny)
    screen_hdim(d, ox + WEST * S, ox + (WEST + PATH) * S, wall_top - 68, "4'-0\" PATH", f_tiny)
    screen_hdim(d, ox + X_EAST * S, ox + plan_w, wall_top - 68, "16'-0\" EAST BAY", f_tiny)
    d.text((ox + plan_w / 2 - 78, wall_top - 100), "WEST   ←——→   EAST", fill=DIM, font=f_dim)

    # Left chain, south to north
    left_chain = [
        (0, OFFICE_H, "10'-0\"  W6"),
        (Y_QC, Y_QC + QC_H, "10'-0\"  W5"),
        (Y_SOAP, Y_NORTH, "41'-8\"  SOAP"),
        (Y_NORTH, NS, "8'-0\"  W1"),
    ]
    draw_v_chain(d, P, left_chain, x=-0.7, font_=f_tiny, side="left")
    paste_vertical(img, "70'-0\"     NORTH  ↓  SOUTH", font(12, True), INK,
                   ox - 130, oy + plan_h / 2)

    right_chain = [
        (Y_OIL, Y_OIL + OIL_H, "25'-4\""),
        (Y_FP, Y_FP + FP_H, "10'-0\""),
        (Y_PACK, Y_PACK + PACK_H, "16'-0\""),
        (Y_OPEN, Y_OPEN + OPEN_H, "10'-0\""),
        (Y_NORTH, NS, "8'-0\""),
    ]
    draw_v_chain(d, P, right_chain, x=EW + 0.35, font_=f_tiny, side="right")

    # North arrow
    nx, ny = 78, oy + 36
    d.polygon([(nx, ny - 34), (nx - 12, ny + 8), (nx + 12, ny + 8)], fill=INK)
    d.rectangle([nx - 4, ny + 8, nx + 4, ny + 26], fill=INK)
    d.text((nx - 8, ny - 56), "N", fill=INK, font=font(16, True))

    # Scale, then a single legend row, then the notes.
    d.rectangle([ox, oy + plan_h + 14, ox + 10 * S, oy + plan_h + 22], fill=INK)
    d.text((ox + 10 * S + 8, oy + plan_h + 12), "10'-0\"", fill=INK, font=f_tiny)

    ly = oy + plan_h + 40
    d.text((ox, ly), "LEGEND", fill=INK, font=font(11, True))
    legend = [
        (FILL["soap"], "Soap (W1–W4)"),
        (FILL["oil"], "Oil / facepack"),
        (FILL["pack"], "Packing"),
        (FILL["open"], "Open dock"),
        (FILL["raw"], "Raw material"),
        (FILL["lab"], "Office, QC, men"),
        (FILL["path"], "Path"),
    ]
    lx = ox + 70
    for col, label in legend:
        d.rectangle([lx, ly, lx + 14, ly + 12], fill=col, outline=INK)
        d.text((lx + 18, ly - 1), label, fill=INK, font=f_tiny)
        lx += 18 + d.textlength(label, font=f_tiny) + 14
    d.arc([lx, ly - 2, lx + 14, ly + 12], 180, 270, fill=GREEN, width=2)
    d.text((lx + 18, ly - 1), "Door 3'-6\"", fill=INK, font=f_tiny)
    lx += 18 + d.textlength("Door 3'-6\"", font=f_tiny) + 10
    d.line([(lx, ly + 6), (lx + 16, ly + 6)], fill=RED, width=3)
    d.text((lx + 20, ly - 1), "East / north door", fill=INK, font=f_tiny)
    lx += 20 + d.textlength("East / north door", font=f_tiny) + 10
    d.line([(lx, ly + 6), (lx + 16, ly + 6)], fill=PANEL_C, width=4)
    d.text((lx + 20, ly - 1), "2\" panel", fill=INK, font=f_tiny)

    # Construction notes
    box = [40, oy + plan_h + 66, W - 40, H - 16]
    d.rounded_rectangle(box, radius=8, outline=(180, 180, 175), width=1)
    d.text((54, box[1] + 8), "CONSTRUCTION NOTES", fill=INK, font=font(12, True))
    notes = [
        "1.  W1, W2, W3 and W4 are one soap section (making, curing and packing). W5 is the QC lab. W6 is the office, south-west, owner seated facing east.",
        "2.  The north 8'-0\" band has no 4'-0\" path. W1 is open to the raw-material room (E-N). Together they run 30'-0\" to the men-change wall.",
        "3.  E-N is divided: north-east 6'-0\" × 8'-0\" men change & safety kit, entered by a 3'-0\" north door; the rest is the raw-material room, entered by a 6'-0\" north door.",
        "4.  E-S is oil making, storage and filling. Immediately north of it: a 4'-0\" east door, then facepack & powder 10'-0\" × 16'-0\" (160 sq ft), then packing 16'-0\" × 16'-0\".",
        "5.  A 7'-0\" east door, just north of packing, opens into 10'-0\" of open dock. Closed rooms use 2\" (50 mm) panels. Soap is open to W1 — no panel there.",
        "6.  East-west below the north band: 16'-0\" west bay + 4'-0\" path + 16'-0\" east bay = 36'-0\". Every production bay is 16'-0\" deep.",
        "7.  Floor: PVC mat, wood finish, over the full 36' × 70' shed. No false ceiling — roof structure left exposed, 12'-0\" clear to purlins.",
        "8.  Dimension check  ·  west: 10 + 2\" + 10 + 2\" + 41'-8\" + 8 = 70'-0\"   ·   east: 25'-4\" + 2\" + 10 + 2\" + 16 + 2\" + 10 + 2\" + 8 = 70'-0\".",
    ]
    ty = box[1] + 28
    for line in notes:
        d.text((54, ty), line, fill=INK, font=font(10))
        ty += 16

    return img


def card(d, P, code, title, subtitle, size, area, x, y, w, h,
         f_code, f_room, f_tiny, rows, f_equip, header_from_top=10):
    x1, y1 = P(x, y + h)          # top-left on screen
    x2, y2 = P(x + w, y)          # bottom-right
    cx = (x1 + x2) / 2
    top = y1 + header_from_top
    if code:
        label = f"{code}   {title}"
    else:
        label = title
    for i, line in enumerate(label.split("\n")):
        tw = d.textlength(line, font=f_room)
        d.text((cx - tw / 2, top + i * 16), line, fill=INK, font=f_room)
    top += 16 * len(label.split("\n"))
    tw = d.textlength(subtitle, font=f_tiny)
    d.text((cx - tw / 2, top), subtitle, fill=MUTED, font=f_tiny)
    top += 14
    size_line = size if not area else f"{size}     {area}"
    tw = d.textlength(size_line, font=f_tiny)
    d.text((cx - tw / 2, top), size_line, fill=DIM, font=f_tiny)
    if not rows:
        return
    inner_top = top + 18
    inner_bot = y2 - 8
    inner_h = inner_bot - inner_top
    if inner_h < 16:
        return
    n = len(rows)
    row_h = inner_h / n
    pad = 8
    for r, items in enumerate(rows):
        cols = len(items)
        cell_w = ((x2 - x1) - pad * 2) / cols
        cy = inner_top + r * row_h + row_h / 2
        for c, text in enumerate(items):
            ccx = x1 + pad + c * cell_w + cell_w / 2
            tw = d.textlength(text, font=f_equip)
            bw = min(cell_w - 6, tw + 14)
            bh = 16
            d.rounded_rectangle([ccx - bw / 2, cy - bh / 2, ccx + bw / 2, cy + bh / 2],
                                radius=3, fill=WHITE, outline=(190, 190, 185))
            d.text((ccx - tw / 2, cy - 6), text, fill=INK, font=f_equip)


def swing_into_east_room(d, P, y, width):
    """3'-6\" door on the west wall of an east-bay room, swinging in."""
    _swing(d, P, X_EAST, y, width, into="east")


def swing_into_west_room(d, P, y, width):
    """Door on the east wall of a west-bay room, or the west wall of an east room from the path.
    Used for west rooms (hinge on the path's west side)."""
    _swing(d, P, X_PATH, y, width, into="west")


def _swing(d, P, wall_x, y, width, into):
    # Opening along the wall, hinge at the south jamb, leaf swings into the room.
    x, y_s = P(wall_x, y)             # south jamb (lower on the building, lower on screen? )
    # P: larger building y → smaller screen y. South jamb of an opening that runs
    # from y to y+width is the smaller building y, which is the larger screen y.
    _, y_n = P(wall_x, y + width)
    # screen: y_n is above y_s
    gap = 5
    if into == "east":
        d.rectangle([x - 2, y_n, x + gap, y_s], fill=WHITE)
        d.arc([x, y_n, x + (y_s - y_n), y_s], 270, 360, fill=GREEN, width=2)
        d.line([(x, y_s), (x + (y_s - y_n), y_s)], fill=GREEN, width=2)
    else:
        d.rectangle([x - gap, y_n, x + 2, y_s], fill=WHITE)
        w = y_s - y_n
        d.arc([x - w, y_n, x, y_s], 180, 270, fill=GREEN, width=2)
        d.line([(x, y_s), (x - w, y_s)], fill=GREEN, width=2)


def east_door(d, P, y, width, line1, line2, fnt):
    x, y_s = P(EW, y)
    _, y_n = P(EW, y + width)
    d.rectangle([x - 4, y_n, x + 4, y_s], fill=WHITE, outline=RED, width=2)
    mid = (y_n + y_s) / 2
    d.line([(x + 4, mid), (x + 78, mid)], fill=RED, width=2)
    d.polygon([(x + 78, mid - 4), (x + 86, mid), (x + 78, mid + 4)], fill=RED)
    d.text((x + 92, mid - 16), line1, fill=RED, font=fnt)
    d.text((x + 92, mid - 2), line2, fill=RED, font=fnt)


def north_door(d, P, x, width, label, fnt):
    sx, sy = P(x, NS)
    ex, _ = P(x + width, NS)
    d.rectangle([sx, sy - 4, ex, sy + 4], fill=WHITE, outline=RED, width=2)
    # Short swing symbol so a 6' leaf does not cover the 8' room.
    r = 34
    d.arc([sx, sy, sx + r, sy + r], 180, 270, fill=RED, width=2)
    tw = d.textlength(label, font=fnt)
    d.text(((sx + ex) / 2 - tw / 2, sy + 8), label, fill=RED, font=fnt)


def screen_hdim(d, x0, x1, y, label, fnt):
    d.line([(x0, y), (x1, y)], fill=DIM, width=1)
    d.line([(x0, y - 4), (x0, y + 4)], fill=DIM, width=1)
    d.line([(x1, y - 4), (x1, y + 4)], fill=DIM, width=1)
    tw = d.textlength(label, font=fnt)
    d.text(((x0 + x1) / 2 - tw / 2, y - 14), label, fill=DIM, font=fnt)


def draw_h_dim(d, P, x0, x1, y, label, fnt):
    a, b = P(x0, y), P(x1, y)
    d.line([a, b], fill=DIM, width=1)
    d.line([(a[0], a[1] - 4), (a[0], a[1] + 4)], fill=DIM, width=1)
    d.line([(b[0], b[1] - 4), (b[0], b[1] + 4)], fill=DIM, width=1)
    tw = d.textlength(label, font=fnt)
    d.text(((a[0] + b[0]) / 2 - tw / 2, a[1] - 14), label, fill=DIM, font=fnt)


def draw_v_chain(d, P, spans, x, font_, side):
    for y0, y1, label in spans:
        a, b = P(x, y0), P(x, y1)
        d.line([a, b], fill=DIM, width=1)
        d.line([(a[0] - 4, a[1]), (a[0] + 4, a[1])], fill=DIM, width=1)
        d.line([(b[0] - 4, b[1]), (b[0] + 4, b[1])], fill=DIM, width=1)
        my = (a[1] + b[1]) / 2
        if side == "left":
            tw = d.textlength(label, font=font_)
            d.text((a[0] - tw - 8, my - 6), label, fill=DIM, font=font_)
        else:
            d.text((a[0] + 8, my - 6), label, fill=DIM, font=font_)


def paste_vertical(base: Image.Image, text: str, fnt, fill, cx: float, cy: float) -> None:
    tmp = Image.new("RGBA", (1, 1))
    td = ImageDraw.Draw(tmp)
    bbox = td.textbbox((0, 0), text, font=fnt)
    tw, th = bbox[2] - bbox[0] + 4, bbox[3] - bbox[1] + 4
    chip = Image.new("RGBA", (tw, th), (255, 255, 255, 0))
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
    scale = min((pw - 28) / img.width, (ph - 28) / img.height)
    dw, dh = img.width * scale, img.height * scale
    c.drawImage(ImageReader(buf), (pw - dw) / 2, (ph - dh) / 2, width=dw, height=dh)
    c.showPage()
    schedule_page(c, letter[0], letter[1])
    c.setAuthor("Parambu Organics")
    c.setTitle("Parambu Organics Factory Floor Plan")
    c.save()


def schedule_page(c: canvas.Canvas, pw: float, ph: float) -> None:
    # landscape content on a portrait letter page, kept narrow
    y = ph - 0.6 * inch
    c.setFillColor(colors.HexColor("#1B4332"))
    c.setFont("Helvetica-Bold", 13)
    c.drawString(0.6 * inch, y, "PARAMBU — ROOM SCHEDULE")
    y -= 14
    c.setFillColor(colors.grey)
    c.setFont("Helvetica", 8)
    c.drawString(0.6 * inch, y, "36'-0\" × 70'-0\" = 2,520 sq ft   ·   east facing   ·   W1–W4 joined soap   ·   E-S oil")
    y -= 18
    rows = [
        ["CODE", "ROOM", "SIZE", "AREA", "NOTES"],
        ["W1–W4", "Soap making, curing & packing", "49'-8\" × 16'-0\"", "795 sq ft", "W1–W4 one room; W1 open to raw material"],
        ["W1 / E-N", "Raw material joined to W1", "30'-0\" × 8'-0\"", "240 sq ft", "No 4' path; includes W1; 6'-0\" north door"],
        ["E-N", "Men change & safety", "6'-0\" × 8'-0\"", "48 sq ft", "North-east; 3'-0\" north door"],
        ["W5", "Quality control lab", "10'-0\" × 16'-0\"", "160 sq ft", "Bench, sink, retained samples"],
        ["W6", "Office", "10'-0\" × 16'-0\"", "160 sq ft", "South-west; owner faces east"],
        ["E-S", "Oil making, storage & filling", "25'-4\" × 16'-0\"", "405 sq ft", "Press, five tanks, filling line"],
        ["—", "Facepack & powder", "10'-0\" × 16'-0\"", "160 sq ft", "North of the 4'-0\" door"],
        ["—", "Packing", "16'-0\" × 16'-0\"", "256 sq ft", "North of facepack"],
        ["—", "Open dock", "10'-0\" × 16'-0\"", "160 sq ft", "Entered by the 7'-0\" east door"],
        ["P1", "Central path", "4'-0\" × 62'-0\"", "248 sq ft", "Stops at the north band"],
    ]
    table = Table(rows, colWidths=[0.7 * inch, 2.15 * inch, 1.25 * inch, 0.7 * inch, 2.5 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B4332")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F1E4")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    _, th = table.wrapOn(c, pw, ph)
    table.drawOn(c, 0.55 * inch, y - th)
    y = y - th - 14
    c.setFillColor(colors.grey)
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(0.6 * inch, y, "The 30' × 8' north band includes W1. Do not add it on top of the 795 sq ft soap hall.")
    y -= 16
    c.setFillColor(colors.HexColor("#1B4332"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.6 * inch, y, "DOORS")
    y -= 12
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 8)
    for line in (
        "4'-0\" east door — immediately north of oil (E-S), at the facepack room.",
        "7'-0\" east door — immediately north of packing; opens into the 10'-0\" open dock.",
        "3'-0\" north door — men entry into the 6'-0\" × 8'-0\" change & safety room.",
        "6'-0\" north door — raw-material entry into E-N, which is open to W1.",
        "Closed rooms (office, QC, soap, oil, facepack, packing) have 3'-6\" doors to the path.",
        "Floor: PVC mat, wood finish. Ceiling: none. Clear height 12'-0\" to purlins.",
    ):
        c.drawString(0.6 * inch, y, line)
        y -= 12


if __name__ == "__main__":
    main()
