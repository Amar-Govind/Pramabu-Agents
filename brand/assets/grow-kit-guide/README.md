# Grow Kit User Guide

Two versions of the Parambu Organics grow-kit user guide are generated from
this folder:

## 1. Flat poster — `generate_user_guide.py`

The original single-sheet poster (`output/grow-kit-user-guide.png`): a 3x3
grid of step cards plus a wide finale card, brand footer, and feature icons.

```bash
python3 generate_user_guide.py
```

## 2. Foldable "Grow Trail" accordion guide — `generate_foldable_guide.py`

A pocket-size, 8-panel zig-zag (accordion) fold-out card designed to sit
inside the kit box instead of a flat poster. The concept:

- **Cover panel** — styled like a seed-packet tag (pennant top + hang hole)
  with a "waypoint list" previewing all 7 steps, like a trail map legend.
- **Panels 2–7** — one step per panel, each with its own "you are here"
  progress trail, an oversized ghost page-number watermark, and a
  "Next \u2192 \<step\>" wayfinding caption pointing to the following panel
  (or "Flip the card \u2192 Step 4" where the design continues onto the
  back sheet).
- **Panel 8** — Step 7 plus a condensed back cover (slogan, feature icons,
  contact line).
- Dashed fold lines with mountain/valley fold pictograms and fold-sequence
  badges (F1–F3) run through every gutter between panels.

Run it with:

```bash
python3 generate_foldable_guide.py
```

Outputs:

- `output/grow-kit-foldable-guide-front.png` — panels 1–4 (Cover, Steps 1–3)
- `output/grow-kit-foldable-guide-back.png` — panels 5–8 (Steps 4–7 + back cover)
- `output/grow-kit-foldable-guide-folded-mockup.png` — a presentation mockup
  of the card closed, showing the accordion pleats and cover

**Production note:** these are design concepts at print-ready panel
proportions, not an imposed press file. A print vendor should still finalize
the exact die-line, bleed, and panel mirroring/rotation needed for duplex
accordion folding on their equipment.
