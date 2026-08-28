# Cold-process soap quality: getting to IS 2888 Grade 1

Working notes for the Parambu Organics soap line, written against the STS lab report
`STS/RE/2026-27/1093` (31.07.2026) for the Virgin Coconut Oil Soap.

Everything here is about **IS 2888:2004 — Toilet Soap (Third Revision)**, which is the
standard the lab tested against.

## 1. Where the bar stands today

| Parameter | Grade 1 | Grade 2 | Grade 3 | Result | Grade 1? |
| --- | --- | --- | --- | --- | --- |
| Total fatty matter, % min | 76.0 | 70.0 | 60.0 | **72.9** | No |
| Lather, ml min | 280 | 240 | 200 | **250** | No |
| Matter insoluble in alcohol, % max | 2.5 | 10 | 10 | **3.5** | No |
| Free caustic alkali as NaOH, % max | 0.05 | 0.05 | 0.05 | 0.006 | Yes |
| Chlorides as NaCl, % max | 1.50 | 1.50 | 1.50 | 1.0 | Yes |
| Free carbonated alkali, % max | 1.0 | 1.0 | 1.0 | 0.02 | Yes |
| Moisture, % max | not in IS 2888 | | | 13.2 | n/a |
| pH | not in IS 2888 | | | 8.0 | n/a |

The bar is **Grade 2**. Three parameters block Grade 1, and they are not independent —
all three are downstream of the same root cause.

Two things about the report worth knowing:

- **Moisture and pH are not in IS 2888 Table 1.** The standard specifies exactly seven
  characteristics: total fatty matter, rosin acid, free caustic alkali, matter insoluble
  in alcohol, chlorides, free carbonated alkali, and lather. The 15% moisture and
  7.5–9.0 pH lines on the report are the lab's own additions. Neither affects the grade.
- **Free caustic alkali and matter insoluble in alcohol are graded on a corrected basis.**
  Clause 5.6.2 says these results must be recalculated against the *minimum specified*
  TFM, because soap loses moisture on storage:

  ```
  Recalculated result = Actual result x (Minimum specified TFM / Actual TFM)
  ```

  Judged against Grade 1, the insolubles are therefore `3.5 x 76 / 72.9 = 3.65%`, not
  3.5%. The gap is slightly wider than it looks. Free caustic alkali corrects to 0.0063%
  and still passes with enormous margin.

## 2. Why the TFM is stuck: the 100 g budget

TFM is measured by splitting the soap with acid and weighing the recovered fatty
matter. The sodium bound in the soap is *not* counted, and neither is the glycerin.
Both still occupy mass in the bar. For a 100% coconut bar:

- Mean fatty acid mass ≈ 213, so bound sodium is `22/213` ≈ 10.3% of the fatty acid mass.
- Coconut triglycerides are short, so saponification liberates a lot of glycerin:
  `92/677` ≈ 13.6% of the oil weight. (Long-chain oils give ~10.5%.)

Cold process keeps all of that glycerin. So a Grade 1 bar has to fit inside this budget:

| Component (per 100 g of finished bar) | Mass |
| --- | --- |
| Fatty matter — the thing being measured | 76.0 g |
| Sodium bound in the soap — unavoidable | ~7.4 g |
| Glycerin from saponification — unavoidable in cold process | ~10.3 g |
| **Left over for water + salt + clay/herbs + fragrance** | **~6.2 g** |

That is the whole problem in one line. Commercial Grade 1 soap reaches 78–82% TFM
because the glycerin is washed out during kettle boiling or salting-out and sold
separately; the noodles arrive glycerin-free. Handcrafted cold process cannot do this,
so roughly ten points of the budget are spoken for before any water is added.

**Consequence: moisture and TFM trade off almost exactly one-for-one.** Every extra
percentage point of water in the bar costs about one point of TFM.

## 3. What the numbers say about the current recipe

Take the moisture out and look at the bar on a dry basis:

```
dry-basis TFM = 72.9 / (100 - 13.2) = 84.0%
```

Now compare against the theoretical ceiling for a 100% coconut cold-process bar at
various superfat levels (bone dry, no fillers):

| Superfat | Max possible TFM, dry |
| --- | --- |
| 0% | 80.2% |
| 5% | 81.0% |
| 10% | 81.9% |
| 15% | 82.8% |
| 20% | 83.7% |
| 25% | 84.6% |

A dry-basis 84.0% implies a superfat somewhere around 20–25% (or a blend carrying some
long-chain oil). Superfat counts fully towards TFM — the IS 2888 foreword notes the
unsaponified matter limit was deleted specifically "to cover the super fatted soap" —
so a heavily superfatted bar has a *high* ceiling.

A high superfat also explains the other three readings:

- **Lather 250 ml is low for a coconut bar.** Coconut is ~48% lauric and should foam
  copiously. Free, unsaponified oil is a potent defoamer, and 20%+ of it will hold
  lather down.
- **pH 8.0 is unusually low for a coconut soap** (1% solutions normally read 9.5–10.5).
  Excess free fatty acid buffers the bar downwards.
- **Free caustic alkali 0.006% is essentially zero**, which is what a large lye discount
  produces.

The important conclusion: **the formulation is already running at its theoretical
maximum efficiency. The entire 3.1-point TFM gap is water.** This is a drying and
purity problem, not a recipe problem.

At the current oil blend, cutting moisture to ~7% and insolubles to ~2% lands TFM at
76%+. That is the shortest path to Grade 1.

## 4. Action plan

### 4.1 Drive the moisture down — biggest lever, fixes TFM

Target **5–7% moisture**, from the current 13.2%.

- **Steepen the water discount.** Mix the lye at a 33% concentration (water = 2.03 x
  NaOH weight) instead of the usual 25–28%. Coconut traces very fast at 33%, so drop
  both oils and lye to 38–40 °C and blend in short bursts rather than continuously.
- **Force a full gel phase.** Insulate the mould. Complete saponification in gel drives
  off water and gives a harder, denser bar.
- **Extend and control the cure.** 8–12 weeks on open racks with forced air circulation,
  at **under 60% RH**. In Coimbatore this needs a dehumidified or at minimum a
  fan-ventilated curing room — ambient monsoon humidity will stall the cure and the bars
  will reabsorb water. Rotate bars so all faces get airflow.
- **Use weight loss, not the calendar, as the release criterion.** Weigh three marked
  bars from every batch weekly. Release only when weekly loss falls below 0.5%. "Cured
  for 6–8 weeks" is a schedule, not a specification.

### 4.2 Cut the alcohol-insolubles — fixes the 3.5%

Target **≤2.0%**, which leaves margin after the clause 5.6.2 correction.

Matter insoluble in alcohol is everything that will not dissolve in hot ethanol: salt,
sodium carbonate, clay, charcoal, starch, botanical powders, and calcium/magnesium
soaps. Chlorides alone account for 1.0 point of the 3.5.

- **Stop adding salt.** A coconut bar is already very hard and does not need brine.
- **Switch to demineralised or RO water** for the lye solution, TDS under 20 ppm. Hard
  water forms calcium and magnesium soaps, which are alcohol-insoluble *and* kill
  lather. This one change helps two failing parameters at once.
- **Use higher-purity NaOH** — ≥99%, low carbonate, with a certificate of analysis.
  Technical-grade flake carries NaCl and Na₂CO₃ straight into the bar. Keep drums
  sealed; open NaOH absorbs CO₂ and converts to carbonate.
- **Run this SKU additive-free.** Clays, activated charcoal and herbal powders are almost
  entirely alcohol-insoluble and go directly into this number. Keep them for the Grade 2
  herbal bars where the limit is 10%.

Getting insolubles below 1.1% has a bonus: clause 5.5 note says the free carbonated
alkali test can then be skipped entirely.

### 4.3 Raise the lather — fixes the 250 ml

The test (IS 13498, kitchen blender method) grates the bar through a 1.70 mm sieve,
blends **5 g in 100 ml of 300 ppm hard water** for 60 seconds, and reads foam volume in
a cylinder, normalised against a 1% sodium lauryl sulphate reference of 600 ml.

Three things follow from the method:

- It doses a fixed mass of **product**, not of soap. Raising TFM from 72.9 to 76 alone
  adds roughly 4% more actual soap per 5 g charge — worth about 10 ml. Necessary but
  not sufficient.
- It uses **300 ppm hard water**, so any calcium or magnesium already in the bar
  compounds with the test water. Demineralised process water matters here too.
- The bar is **grated**. A soft, sticky, high-moisture bar grates into irregular
  particles that disperse poorly in 60 seconds and reads low. Drier and harder is better.

The formulation change that matters:

- **Bring superfat down to 8–10%** from the implied ~20%. This is the single biggest
  lather lever. It will cost a little TFM headroom (ceiling drops from ~83.7% to ~81.7%
  dry), which is why it has to be paired with the moisture work in 4.1.
- **Add ~5% castor oil.** Ricinoleic acid is the standard foam-volume and foam-stability
  booster and is well worth its place in the blend.
- Keep coconut dominant. Lauric and myristic acid drive foam; do not dilute with more
  than ~20% soft high-oleic oils.

### 4.4 Mill and press — required by the Grade 1 definition

This one is easy to miss. IS 2888 does not define the grades purely by numbers; clause
5.1 describes them physically:

- **Grade 1** — "thoroughly saponified, **milled** soap or **homogenized** soap or both
  ... **compressed** in the form of firm smooth cakes"
- **Grade 2** — "thoroughly saponified, **plodded** soap of firm and smooth texture"
- **Grade 3** — "saponified soap of firm and smooth texture"

A poured-into-mould-and-cut cold-process bar matches the *Grade 3* description. Even at
76% TFM, a purely poured bar does not meet the Grade 1 description.

The fix is the classic French-milled route, and it happens to solve the moisture problem
at the same time: cure the cold-process soap, shred it, pass it through a triple-roll
mill (or repeatedly through a plodder), then extrude and stamp into cakes. Milling
drives out residual water, removes voids, homogenises additives, and gives a denser
bar that lasts longer and grates cleanly for the lather test. It is the only step that
addresses TFM, lather and the grade description simultaneously.

## 5. On pH — do not chase it lower

**pH 8.0 is already excellent, and it is not a grade criterion.** It appears nowhere in
IS 2888. Some specific points:

- A sodium soap of fatty acids is the salt of a strong base and a weak acid. Its
  solutions are alkaline by construction; 1% solutions of ordinary bar soap read
  9.5–10.5. Reading 8.0 is already at the bottom of what a true soap can do, and the
  current bar is only getting there because of the very high superfat.
- Pushing lower means partially converting soap back into free fatty acid. That destroys
  lather, lowers the effective soap content, softens the bar and invites rancidity. It
  works directly against the Grade 1 goal.
- The synthetic route is closed. Clause 5.6.2.1 states the material "shall neither
  contain any synthetic detergent ... nor any phosphate". A pH 5.5 bar built on SCI or
  SCS cannot be sold as IS 2888 toilet soap at all — that is a syndet or combo bar under
  a different specification.
- **The real mildness metric is free caustic alkali, and it is already outstanding:
  0.006% against a 0.05% limit, roughly eight times better than required.** That is the
  claim worth making, and it is defensible.

Expect pH to rise into the 9s as superfat comes down in 4.3. That is fine and expected;
trading pH 8.0 for Grade 1 lather is the right call because pH is not graded.

One practical note: pH readings depend entirely on method — 1% solution, 10% solution,
and surface pH on a wet bar give different numbers. Ask STS which they used and fix that
method for all future batches so results are comparable.

## 6. Target formulation

A starting point to trial, not a finished recipe. Recalculate lye against the actual
saponification value of the oil lot rather than a generic table figure.

| | |
| --- | --- |
| Coconut oil | 90% |
| Castor oil | 5% |
| Kokum or mango butter (hardness, raises TFM ceiling) | 5% |
| Superfat | 8% |
| Lye concentration | 33% (water = 2.03 x NaOH) |
| NaOH | ≥99%, low carbonate, with CoA |
| Water | DM/RO, TDS < 20 ppm |
| Added salt, clay, botanical powder | none |
| Mix temperature | 38–40 °C, both phases |
| Cure | 8–12 weeks, <60% RH, forced air, to weight plateau |
| Finish | shred, mill, extrude, press |

Predicted outcome at 5% moisture and 1.5% insolubles: TFM ≈ 76.5%, comfortably over the
line, with lather well clear of 280 ml once the superfat comes down.

Be realistic about the margin. A glycerin-retaining cold-process bar reaching 76% TFM is
operating within about five points of its physical ceiling. It is achievable, but only
with tight moisture control — which is exactly why the standard describes Grade 1 as a
milled and compressed soap.

## 7. Incoming material and batch QC

Most of the variation in the results above comes from inputs that are currently
unmeasured.

**Per oil lot** — require a CoA for saponification value, free fatty acid, and moisture.
A high-FFA copra or virgin coconut oil consumes more NaOH than the SAP table predicts,
which silently pushes the real superfat above target and drags lather down. This is the
most likely cause of batch-to-batch drift.

**Per NaOH lot** — purity, carbonate content, chloride content.

**Per batch** — record oil weights, NaOH lot and purity, water source and TDS, lye
concentration, both phase temperatures, trace time, mould and cut times, cure start
date, daily curing-room temperature and RH, and weekly bar weights.

**In-house, cheap:** moisture by loss on drying — weigh a grated sample, hold at 105 °C
to constant weight. This lets the moisture target be verified before paying for a full
lab panel, and moisture is the parameter that decides everything else.

**Retest panel** once a trial batch is through cure: TFM, matter insoluble in alcohol,
chlorides, free caustic alkali, lather, pH. Ask the lab to note that rosin acid is not
applicable — Amendment 3 (May 2013) to IS 2888 says the rosin test need not be performed
if rosin is not used in manufacture.

For a full Grade 1 claim the bar also has to pass dermatological safety testing to
IS 13424 (clause 5.6.2.2), which is a separate test house exercise.

## 8. Labelling and claims

The current bar is **Grade 2**. Until a retest confirms otherwise:

- Do not put "Grade 1" on packaging, the storefront, or campaign copy.
- "Complies" in the report's remarks column means the sample complies with IS 2888 at the
  grade it achieved, not with Grade 1.
- Claims that are true today and worth using: cold processed, glycerin retained, free
  caustic alkali at 0.006% against a 0.05% limit, pH 8.0.
- Under clause 5.2, any additive beyond perfume, colour, preservative and medicament has
  to be declared on the label. Relevant for the herbal and clay bars.
