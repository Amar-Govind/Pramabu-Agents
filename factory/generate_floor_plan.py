#!/usr/bin/env python3
"""Generate Parambu Organics factory floor plan (PNG + PDF).

Building: 36' E–W × 70' N–S, east-facing.
Coordinate system: origin at SW corner; +X east, +Y north (feet).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Rectangle

# --- Geometry (feet) ---------------------------------------------------------
BUILDING_W = 36.0
BUILDING_H = 70.0

WEST_W = 16.0
CORR_W = 4.0
EAST_X = WEST_W + CORR_W  # 20
EAST_W = 16.0

NORTH_Y = 62.0
NORTH_H = 8.0

# West stack (south → north)
OFFICE = (0.0, 0.0, WEST_W, 10.0)
QC = (0.0, 10.0, WEST_W, 10.0)
SOAP = (0.0, 20.0, WEST_W, 41.0 + 8.0 / 12.0)  # 41'-8"

# North strip (full width, no 4' corridor)
RAW = (0.0, NORTH_Y, 30.0, NORTH_H)  # raw material / W1
CHANGE = (30.0, NORTH_Y, 6.0, NORTH_H)  # men change & safety

# East stack (south → north of oil)
OIL = (EAST_X, 0.0, EAST_W, 22.0)
FACE = (EAST_X, 22.0, EAST_W, 10.0)
PACK = (EAST_X, 32.0, EAST_W, 16.0)
DOCK = (EAST_X, 48.0, EAST_W, 10.0)
EAST_CIRC = (EAST_X, 58.0, EAST_W, 4.0)  # 4' link under north strip

CORRIDOR = (WEST_W, 0.0, CORR_W, NORTH_Y)

ROOMS = [
    (*OFFICE, "OFFICE", "10' × 16'"),
    (*QC, "QC", "10' × 16'"),
    (*SOAP, "SOAP MAKING\n(W2–W4 JOINED)", "41'-8\" × 16'"),
    (*RAW, "RAW MATERIAL / W1", "8' × 30'"),
    (*CHANGE, "MEN CHANGE\n& SAFETY", "6' × 8'"),
    (*OIL, "OIL MAKING", "22' × 16'"),
    (*FACE, "FACEPACK\n& POWDER", "10' × 16'"),
    (*PACK, "PACKING", "16' × 16'"),
    (*DOCK, "OPEN DOCK", "10' × 16'"),
]

# Fill colors (muted industrial)
FILLS = {
    "OFFICE": "#E8DCC8",
    "QC": "#D9E2EC",
    "SOAP MAKING\n(W2–W4 JOINED)": "#C5D5C5",
    "RAW MATERIAL / W1": "#E2D4B8",
    "MEN CHANGE\n& SAFETY": "#D4C4B0",
    "OIL MAKING": "#C9D6E3",
    "FACEPACK\n& POWDER": "#D8CBE0",
    "PACKING": "#F0D9C8",
    "OPEN DOCK": "#D0D5D8",
}


def ft_label(v: float) -> str:
    whole = int(v)
    inches = round((v - whole) * 12)
    if inches == 0:
        return f"{whole}'"
    if inches == 12:
        return f"{whole + 1}'"
    return f"{whole}'-{inches}\""


def draw_door_swing(ax, x, y, width, wall: str, inward: bool = True):
    """Draw a simple door leaf + swing arc.

    wall: 'N','S','E','W' — which wall the door sits on.
    Door opens inward (into the room) unless inward=False.
    """
    leaf = 0.12
    if wall == "N":
        # hinge at west end of opening on north wall; swing south into room
        ax.plot([x, x], [y, y - width], color="#222", lw=1.4)
        theta1, theta2 = (180, 270) if inward else (90, 180)
        ax.add_patch(
            Arc(
                (x, y),
                2 * width,
                2 * width,
                angle=0,
                theta1=theta1,
                theta2=theta2,
                color="#444",
                lw=0.9,
                ls="--",
            )
        )
        ax.add_patch(Rectangle((x, y - leaf / 2), width, leaf, color="#222", lw=0))
    elif wall == "S":
        ax.plot([x, x], [y, y + width], color="#222", lw=1.4)
        theta1, theta2 = (90, 180) if inward else (180, 270)
        ax.add_patch(
            Arc(
                (x, y),
                2 * width,
                2 * width,
                angle=0,
                theta1=theta1,
                theta2=theta2,
                color="#444",
                lw=0.9,
                ls="--",
            )
        )
        ax.add_patch(Rectangle((x, y - leaf / 2), width, leaf, color="#222", lw=0))
    elif wall == "E":
        # hinge at south end; swing west into room
        ax.plot([x, x - width], [y, y], color="#222", lw=1.4)
        theta1, theta2 = (90, 180) if inward else (0, 90)
        ax.add_patch(
            Arc(
                (x, y),
                2 * width,
                2 * width,
                angle=0,
                theta1=theta1,
                theta2=theta2,
                color="#444",
                lw=0.9,
                ls="--",
            )
        )
        ax.add_patch(Rectangle((x - leaf / 2, y), leaf, width, color="#222", lw=0))
    elif wall == "W":
        ax.plot([x, x + width], [y, y], color="#222", lw=1.4)
        theta1, theta2 = (0, 90) if inward else (90, 180)
        ax.add_patch(
            Arc(
                (x, y),
                2 * width,
                2 * width,
                angle=0,
                theta1=theta1,
                theta2=theta2,
                color="#444",
                lw=0.9,
                ls="--",
            )
        )
        ax.add_patch(Rectangle((x - leaf / 2, y), leaf, width, color="#222", lw=0))


def draw_dim_h(ax, x0, x1, y, label, offset=0.0):
    y = y + offset
    ax.annotate(
        "",
        xy=(x0, y),
        xytext=(x1, y),
        arrowprops=dict(arrowstyle="<->", color="#333", lw=0.8),
    )
    ax.text(
        (x0 + x1) / 2,
        y + 0.35,
        label,
        ha="center",
        va="bottom",
        fontsize=7.5,
        color="#222",
        fontfamily="DejaVu Sans",
    )


def draw_dim_v(ax, y0, y1, x, label, offset=0.0):
    x = x + offset
    ax.annotate(
        "",
        xy=(x, y0),
        xytext=(x, y1),
        arrowprops=dict(arrowstyle="<->", color="#333", lw=0.8),
    )
    ax.text(
        x - 0.35,
        (y0 + y1) / 2,
        label,
        ha="right",
        va="center",
        fontsize=7.5,
        color="#222",
        rotation=90,
        fontfamily="DejaVu Sans",
    )


def build_figure():
    fig, ax = plt.subplots(figsize=(11, 17), dpi=150)
    fig.patch.set_facecolor("#F7F4EF")
    ax.set_facecolor("#F7F4EF")

    # Outer building shell (2" panels ≈ slight wall band)
    wall = 2.0 / 12.0
    ax.add_patch(
        Rectangle(
            (-wall, -wall),
            BUILDING_W + 2 * wall,
            BUILDING_H + 2 * wall,
            facecolor="#5C5346",
            edgecolor="#2C2820",
            lw=1.5,
            zorder=1,
        )
    )
    ax.add_patch(
        Rectangle(
            (0, 0),
            BUILDING_W,
            BUILDING_H,
            facecolor="#EFE8DC",
            edgecolor="#2C2820",
            lw=1.2,
            zorder=2,
        )
    )

    # Corridor
    ax.add_patch(
        Rectangle(
            CORRIDOR[:2],
            CORRIDOR[2],
            CORRIDOR[3],
            facecolor="#F3EEE4",
            edgecolor="#8A7F6E",
            lw=0.8,
            ls="--",
            zorder=3,
        )
    )
    ax.text(
        CORRIDOR[0] + CORRIDOR[2] / 2,
        CORRIDOR[3] / 2,
        "4' PATH",
        ha="center",
        va="center",
        fontsize=7,
        rotation=90,
        color="#5A5246",
        fontfamily="DejaVu Sans",
        zorder=4,
    )

    # East circulation strip under north
    ax.add_patch(
        Rectangle(
            EAST_CIRC[:2],
            EAST_CIRC[2],
            EAST_CIRC[3],
            facecolor="#F3EEE4",
            edgecolor="#8A7F6E",
            lw=0.8,
            ls="--",
            zorder=3,
        )
    )
    ax.text(
        EAST_CIRC[0] + EAST_CIRC[2] / 2,
        EAST_CIRC[1] + EAST_CIRC[3] / 2,
        "4' CIRCULATION",
        ha="center",
        va="center",
        fontsize=7,
        color="#5A5246",
        fontfamily="DejaVu Sans",
        zorder=4,
    )

    # Rooms
    for x, y, w, h, name, dim in ROOMS:
        fill = FILLS.get(name, "#E8E0D4")
        ax.add_patch(
            Rectangle(
                (x, y),
                w,
                h,
                facecolor=fill,
                edgecolor="#2C2820",
                lw=1.1,
                zorder=3,
            )
        )
        ax.text(
            x + w / 2,
            y + h / 2 + 0.55,
            name,
            ha="center",
            va="center",
            fontsize=8.2 if h >= 10 else 7.2,
            fontweight="bold",
            color="#1E1A14",
            fontfamily="DejaVu Sans",
            zorder=5,
            linespacing=1.15,
        )
        ax.text(
            x + w / 2,
            y + h / 2 - (1.15 if h >= 8 else 0.85),
            dim,
            ha="center",
            va="center",
            fontsize=7,
            color="#3A342A",
            fontfamily="DejaVu Sans",
            zorder=5,
        )

    # Thin gap note between soap top and north strip (~4")
    soap_top = SOAP[1] + SOAP[3]
    if abs(NORTH_Y - soap_top) > 0.05:
        ax.add_patch(
            Rectangle(
                (0, soap_top),
                WEST_W,
                NORTH_Y - soap_top,
                facecolor="#5C5346",
                edgecolor="none",
                zorder=3.5,
            )
        )

    # Specified exterior doors
    # 6' north door — raw material (centered on 30' wall)
    raw_door_w = 6.0
    raw_door_x = RAW[0] + (RAW[2] - raw_door_w) / 2
    draw_door_swing(ax, raw_door_x, BUILDING_H, raw_door_w, "N", inward=True)
    ax.text(
        raw_door_x + raw_door_w / 2,
        BUILDING_H + 1.1,
        "6' N DOOR",
        ha="center",
        va="bottom",
        fontsize=6.5,
        color="#222",
        fontfamily="DejaVu Sans",
    )

    # 3' north door — men change (centered on 6' wall)
    ch_door_w = 3.0
    ch_door_x = CHANGE[0] + (CHANGE[2] - ch_door_w) / 2
    draw_door_swing(ax, ch_door_x, BUILDING_H, ch_door_w, "N", inward=True)
    ax.text(
        ch_door_x + ch_door_w / 2,
        BUILDING_H + 1.1,
        "3' N DOOR",
        ha="center",
        va="bottom",
        fontsize=6.5,
        color="#222",
        fontfamily="DejaVu Sans",
    )

    # 4' east door — oil making
    oil_door_w = 4.0
    oil_door_y = OIL[1] + (OIL[3] - oil_door_w) / 2
    draw_door_swing(ax, BUILDING_W, oil_door_y, oil_door_w, "E", inward=True)
    ax.text(
        BUILDING_W + 1.35,
        oil_door_y + oil_door_w / 2,
        "4' E DOOR",
        ha="left",
        va="center",
        fontsize=6.5,
        color="#222",
        rotation=90,
        fontfamily="DejaVu Sans",
    )

    # 7' east door — into open dock
    dock_door_w = 7.0
    dock_door_y = DOCK[1] + (DOCK[3] - dock_door_w) / 2
    draw_door_swing(ax, BUILDING_W, dock_door_y, dock_door_w, "E", inward=True)
    ax.text(
        BUILDING_W + 1.35,
        dock_door_y + dock_door_w / 2,
        "7' E DOOR",
        ha="left",
        va="center",
        fontsize=6.5,
        color="#222",
        rotation=90,
        fontfamily="DejaVu Sans",
    )

    # Internal corridor door gaps (practical access)
    west_doors = [
        (OFFICE[1] + 3.5, 3.0),
        (QC[1] + 3.5, 3.0),
        (SOAP[1] + 8.0, 3.5),
        (SOAP[1] + 22.0, 3.5),
    ]
    east_doors = [
        (OIL[1] + 9.0, 3.5),
        (FACE[1] + 3.5, 3.0),
        (PACK[1] + 6.0, 3.5),
        (DOCK[1] + 3.5, 3.0),
    ]
    for y0, dh in west_doors:
        ax.plot(
            [WEST_W, WEST_W],
            [y0, y0 + dh],
            color="#EFE8DC",
            lw=2.6,
            zorder=6,
            solid_capstyle="butt",
        )
    for y0, dh in east_doors:
        ax.plot(
            [EAST_X, EAST_X],
            [y0, y0 + dh],
            color="#EFE8DC",
            lw=2.6,
            zorder=6,
            solid_capstyle="butt",
        )

    # Access from corridor / circ into north strip
    ax.plot([WEST_W + 0.4, WEST_W + 3.6], [NORTH_Y, NORTH_Y], color="#EFE8DC", lw=2.6, zorder=6)
    ax.plot([EAST_X + 6, EAST_X + 10], [NORTH_Y, NORTH_Y], color="#EFE8DC", lw=2.6, zorder=6)
    ax.plot([28, 31], [NORTH_Y, NORTH_Y], color="#EFE8DC", lw=2.6, zorder=6)  # into change

    # Door opening gaps on exterior walls (white notches)
    ax.plot([raw_door_x, raw_door_x + raw_door_w], [BUILDING_H, BUILDING_H], color="#EFE8DC", lw=3.2, zorder=6)
    ax.plot([ch_door_x, ch_door_x + ch_door_w], [BUILDING_H, BUILDING_H], color="#EFE8DC", lw=3.2, zorder=6)
    ax.plot([BUILDING_W, BUILDING_W], [oil_door_y, oil_door_y + oil_door_w], color="#EFE8DC", lw=3.2, zorder=6)
    ax.plot([BUILDING_W, BUILDING_W], [dock_door_y, dock_door_y + dock_door_w], color="#EFE8DC", lw=3.2, zorder=6)

    # Overall dimensions
    draw_dim_h(ax, 0, BUILDING_W, -2.8, f"{ft_label(BUILDING_W)} E–W")
    draw_dim_v(ax, 0, BUILDING_H, -2.6, f"{ft_label(BUILDING_H)} N–S")

    # Bay dimensions along south
    draw_dim_h(ax, 0, WEST_W, -1.5, "16'")
    draw_dim_h(ax, WEST_W, EAST_X, -1.5, "4'")
    draw_dim_h(ax, EAST_X, BUILDING_W, -1.5, "16'")

    # North strip dims
    draw_dim_h(ax, 0, 30, BUILDING_H + 2.4, "30'")
    draw_dim_h(ax, 30, 36, BUILDING_H + 2.4, "6'")

    # East stack dims
    draw_dim_v(ax, 0, 22, BUILDING_W + 2.8, "22'")
    draw_dim_v(ax, 22, 32, BUILDING_W + 2.8, "10'")
    draw_dim_v(ax, 32, 48, BUILDING_W + 2.8, "16'")
    draw_dim_v(ax, 48, 58, BUILDING_W + 2.8, "10'")
    draw_dim_v(ax, 58, 62, BUILDING_W + 2.8, "4'")
    draw_dim_v(ax, 62, 70, BUILDING_W + 2.8, "8'")

    # West stack dims
    draw_dim_v(ax, 0, 10, -1.35, "10'")
    draw_dim_v(ax, 10, 20, -1.35, "10'")
    draw_dim_v(ax, 20, soap_top, -1.35, "41'-8\"")
    draw_dim_v(ax, soap_top, NORTH_Y, -1.35, "4\"")
    draw_dim_v(ax, NORTH_Y, BUILDING_H, -1.35, "8'")

    # North arrow
    nx, ny = BUILDING_W + 7.5, BUILDING_H - 4
    ax.annotate(
        "",
        xy=(nx, ny + 2.2),
        xytext=(nx, ny - 1.2),
        arrowprops=dict(arrowstyle="-|>", color="#1E1A14", lw=1.6, mutation_scale=14),
    )
    ax.text(nx, ny + 2.7, "N", ha="center", va="bottom", fontsize=11, fontweight="bold", fontfamily="DejaVu Sans")

    # East-facing marker
    ax.annotate(
        "",
        xy=(BUILDING_W + 6.2, 8),
        xytext=(BUILDING_W + 3.2, 8),
        arrowprops=dict(arrowstyle="-|>", color="#1E1A14", lw=1.3, mutation_scale=12),
    )
    ax.text(
        BUILDING_W + 4.7,
        9.1,
        "EAST\nFACING",
        ha="center",
        va="bottom",
        fontsize=7,
        fontfamily="DejaVu Sans",
    )

    # Title block
    ax.text(
        BUILDING_W / 2,
        BUILDING_H + 5.2,
        "PARAMBU ORGANICS",
        ha="center",
        va="bottom",
        fontsize=16,
        fontweight="bold",
        color="#1E1A14",
        fontfamily="DejaVu Sans",
    )
    ax.text(
        BUILDING_W / 2,
        BUILDING_H + 4.0,
        "Factory Floor Plan — 36' E–W × 70' N–S (East Facing)",
        ha="center",
        va="bottom",
        fontsize=9.5,
        color="#3A342A",
        fontfamily="DejaVu Sans",
    )

    # Finishes / notes panel
    notes = (
        "FINISHES\n"
        "• Floor: PVC wood-finish mat\n"
        "• Ceiling: no false ceiling\n"
        "• Walls: 2\" sandwich panels\n"
        "\n"
        "NOTES\n"
        "• North strip has no 4' path\n"
        "  (raw / W1 joined full width)\n"
        "• Soap W2–W4 joined as one bay\n"
        "• Scale: 1 square ≈ planning grid\n"
        "• Doors shown: specified openings\n"
        "  + corridor access gaps"
    )
    ax.text(
        BUILDING_W + 3.0,
        42,
        notes,
        ha="left",
        va="top",
        fontsize=7.2,
        color="#2C2820",
        fontfamily="DejaVu Sans",
        linespacing=1.35,
        bbox=dict(
            boxstyle="round,pad=0.6",
            facecolor="#FFFCF7",
            edgecolor="#8A7F6E",
            lw=0.9,
        ),
    )

    # Scale bar (10')
    sx0, sy = -2.6, -5.2
    ax.plot([sx0, sx0 + 10], [sy, sy], color="#1E1A14", lw=2.2)
    for t in range(0, 11, 5):
        ax.plot([sx0 + t, sx0 + t], [sy - 0.25, sy + 0.25], color="#1E1A14", lw=1.2)
        ax.text(sx0 + t, sy - 0.7, str(t), ha="center", va="top", fontsize=6.5, fontfamily="DejaVu Sans")
    ax.text(sx0 + 5, sy + 0.7, "SCALE (feet)", ha="center", va="bottom", fontsize=6.5, fontfamily="DejaVu Sans")

    ax.set_xlim(-6.5, BUILDING_W + 14)
    ax.set_ylim(-7.5, BUILDING_H + 7)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout(pad=0.4)
    return fig


def main():
    out_dir = Path(__file__).resolve().parent
    root = out_dir.parent
    fig = build_figure()

    png_factory = out_dir / "floor-plan.png"
    pdf_factory = out_dir / "floor-plan.pdf"
    png_root = root / "floor-plan.png"
    pdf_root = root / "floor-plan.pdf"

    fig.savefig(png_factory, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(pdf_factory, format="pdf", bbox_inches="tight", facecolor=fig.get_facecolor())
    # Also place at repo root for easy Files access
    fig.savefig(png_root, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(pdf_root, format="pdf", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    print(f"Wrote {png_root}")
    print(f"Wrote {pdf_root}")
    print(f"Wrote {png_factory}")
    print(f"Wrote {pdf_factory}")


if __name__ == "__main__":
    main()
