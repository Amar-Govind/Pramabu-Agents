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
    d.text((36, 70), "11 rooms, each 16'-0\" deep   ·   4'-0\" central path   ·   2\" panel room separators   ·   Vastu + Cosmetics Rules 2020", fill=MUTED, font=f_tiny)
    d.line([(36, 92), (W - 36, 92)], fill=(190, 184, 170), width=2)

    # Fills — west, south to north: W6 office, W5 raw, W4 oil make, W3 tanks, W2 filling, W1 finished
    west_fill = [LAB, STORE, PROD, PROD, PACK, STORE]
    east_fill = [PROD, PROD, CIRC, PACK, STORE, CIRC, LAB]
    for (y, h), fill in zip(WEST_Y, west_fill):
        rect(0, y, WEST, h, fill)
    for (y, h), fill in zip(EAST_Y, east_fill):
        rect(X_EAST, y, EAST, h, fill)
    rect(X_PATH, 0, PATH, NS, CIRC)

    # Panels
    def panels(xs, xe, zones):
        y = 0.0
        for i, h in enumerate(zones):
            y += h
            if i < len(zones) - 1:
                seg(xs, y + PANEL / 2, xe, y + PANEL / 2, 3)
                y += PANEL

    panels(0, WEST, WEST_H)
    panels(X_EAST, EW, EAST_H)

    # Path walls, open across the two east loading paths (entry index 5, godown index 2)
    def path_wall(x):
        y = 0.0
        for i, h in enumerate(EAST_H):
            open_bay = i in (2, 5)
            if not open_bay:
                seg(x, y, x, y + h, 3)
            y += h + (PANEL if i < len(EAST_H) - 1 else 0)

    path_wall(X_EAST)
    seg(X_PATH, 0, X_PATH, NS, 3)

    # Exterior
    seg(0, 0, EW, 0, 4)
    seg(0, NS, EW, NS, 4)
    seg(0, 0, 0, NS, 4)
    seg(EW, 0, EW, NS, 4)

    # Room content
    wy = {code: WEST_Y[i] for i, code in enumerate(["W6", "W5", "W4", "W3", "W2", "W1"])}
    ey = {code: EAST_Y[i] for i, code in enumerate(["E5", "E4", "GD", "E3", "E2", "EN", "E1"])}

    card(d, P, "W1", "FINISHED GOODS STORE", "packed soap & oil  ·  dispatch",
         "10'-0\" × 16'-0\"", "160 sq ft", 0, *wy["W1"], WEST,
         [("PALLET RACK", "PALLET RACK", "PALLET RACK"), ("DISPATCH STAGING",)], f_room, f_tiny, f_eq)
    card(d, P, "W2", "OIL FILLING & PACKING ROOM", "filling  ·  capping  ·  labelling",
         "10'-0\" × 16'-0\"", "160 sq ft", 0, *wy["W2"], WEST,
         [("FILLING MACHINE", "CAPPING", "LABELLING"), ("PACKING TABLE",)], f_room, f_tiny, f_eq)
    card(d, P, "W3", "OIL STORAGE TANKS", "5 tanks  ·  settling & decanting",
         "10'-0\" × 16'-0\"", "160 sq ft", 0, *wy["W3"], WEST,
         [], f_room, f_tiny, f_eq)
    tanks(d, P, *wy["W3"], f_eq)
    card(d, P, "W4", "OIL MAKING ROOM", "cold press  ·  filter press",
         "19'-2\" × 16'-0\"", "307 sq ft", 0, *wy["W4"], WEST,
         [("COLD PRESS", "FILTER PRESS", "COLLECTION TANK"), ("SEED / COPRA FEED", "CAKE & WASTE BIN")],
         f_room, f_tiny, f_eq)
    card(d, P, "W5", "RAW MATERIAL STORE", "copra  ·  seeds  ·  oils  ·  lye",
         "10'-0\" × 16'-0\"", "160 sq ft", 0, *wy["W5"], WEST,
         [("RACK", "RACK", "RACK"), ("WEIGHING & SAMPLING",)], f_room, f_tiny, f_eq)
    card(d, P, "W6", "OFFICE", "records  ·  owner seat faces east",
         "10'-0\" × 16'-0\"", "160 sq ft", 0, *wy["W6"], WEST,
         [("DESK", "VISITOR", "RECORD CABINET",)], f_room, f_tiny, f_eq)

    card(d, P, "E1", "QUALITY CONTROL LAB", "testing  ·  retained samples",
         "10'-0\" × 16'-0\"", "160 sq ft", X_EAST, *ey["E1"], EAST,
         [("LAB BENCH", "SINK & WASH"), ("INSTRUMENTS & SAMPLE CUPBOARD",)], f_room, f_tiny, f_eq)
    card(d, P, "", "ENTRY / LOADING PATH", "",
         "9'-6\" × 16'-0\"", "152 sq ft", X_EAST, *ey["EN"], EAST,
         [("HAND WASH",)], f_room, f_tiny, f_eq)
    card(d, P, "E2", "PACKING ITEMS STORE", "bottles  ·  cartons  ·  labels",
         "10'-0\" × 16'-0\"", "160 sq ft", X_EAST, *ey["E2"], EAST,
         [("RACK", "RACK", "RACK"), ("CARTON STACK",)], f_room, f_tiny, f_eq)
    card(d, P, "E3", "SOAP PACKING ROOM", "wrapping  ·  cartoning",
         "10'-0\" × 16'-0\"", "160 sq ft", X_EAST, *ey["E3"], EAST,
         [("WRAPPING TABLE", "CARTONING TABLE"), ("CODING & SEALING",)], f_room, f_tiny, f_eq)
    card(d, P, "", "GODOWN LOADING PATH", "",
         "9'-6\" × 16'-0\"", "152 sq ft", X_EAST, *ey["GD"], EAST,
         [], f_room, f_tiny, f_eq)
    card(d, P, "E4", "SOAP CURING ROOM", "curing racks  ·  4 to 6 weeks",
         "10'-0\" × 16'-0\"", "160 sq ft", X_EAST, *ey["E4"], EAST,
         [("CURING RACK",), ("CURING RACK",), ("CURING RACK",), ("CURING RACK",)], f_room, f_tiny, f_eq)
    card(d, P, "E5", "SOAP MAKING ROOM", "mixer  ·  moulds  ·  cutter",
         "10'-0\" × 16'-0\"", "160 sq ft", X_EAST, *ey["E5"], EAST,
         [("MIXER / KETTLE", "MOULD TABLE", "CUTTER"), ("LYE MIXING (EXHAUST OVER)",)], f_room, f_tiny, f_eq)

    # Internal doors, opening into the room
    for code in ("W1", "W2", "W3", "W4", "W5", "W6"):
        y, h = wy[code]
        swing(d, P, X_PATH, y + h * 0.28, 3.5, into="west")
    for code in ("E1", "E2", "E3", "E4", "E5"):
        y, h = ey[code]
        swing(d, P, X_EAST, y + h * 0.28, 3.5, into="east")

    # East shutters, centered in each loading path
    for key, label in (("EN", "D1"), ("GD", "D2")):
        y, h = ey[key]
        east_door(d, P, y + (h - 7) / 2, 7.0, f"{label}  ·  7'-0\" DOOR", "FACING EAST", f_tiny)

    paste_vertical(img, "CENTRAL PATH    4'-0\"  ×  70'-0\"", font(12, True), MUTED,
                   ox + (X_PATH + PATH / 2) * S, oy + plan_h / 2)

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

    chain(WEST_H, ["10'-0\"  W6", "10'-0\"  W5", "19'-2\"  W4", "10'-0\"  W3", "10'-0\"  W2", "10'-0\"  W1"], -0.45, "left")
    chain(EAST_H, ["10'-0\"  E5", "10'-0\"  E4", "9'-6\"", "10'-0\"  E3", "10'-0\"  E2", "9'-6\"", "10'-0\"  E1"], EW + 0.4, "right")
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
        '3.  West bay north-south: 10 + 10 + 10 + 19\'-2" + 10 + 10 = 69\'-2". The remaining 10" is six 2" panels = 70\'-0".',
        '4.  East bay north-south: five 10\'-0" rooms + two 9\'-6" loading paths = 70\'-0". Both 7\'-0" east doors sit in those paths.',
        '5.  Internal doors 3\'-6" × 7\'-0", all opening into the room, not into the 4\'-0" path. External doors D1 and D2 are 7\'-0" rolling shutters facing east.',
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
