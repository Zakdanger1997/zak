# Denmark Machinery OEM Market Research — for I-MAK Reduktor

**Client:** I-MAK Reduktor (industrial gearboxes, worm/helical/bevel-helical gearboxes, variators, custom transmission solutions)
**Goal:** Identify Danish machinery manufacturers (OEMs) that use industrial gearboxes / geared motors, for use by an international sales team.
**Approach:** Option A — batched by industry sector. One batch per usage window to avoid mid-run cutoff. Each batch saved + committed before moving on.

## Status

| Batch | Sectors | Target | Status | Output file |
|---|---|---|---|---|
| 1 | Food processing, dairy, meat, fish, bakery, beverage | 40–70 | ⬜ Not started | `data/batch-1-food.md` |
| 2 | Agriculture, feed mills, grain, livestock, poultry | 30–50 | ⬜ Not started | `data/batch-2-agriculture.md` |
| 3 | Material handling, conveyors, packaging, logistics | 40–60 | ⬜ Not started | `data/batch-3-material-handling.md` |
| 4 | Wind energy, marine, offshore | 30–50 | ⬜ Not started | `data/batch-4-wind-marine.md` |
| 5 | Industrial automation, special machines, robotics, machine tools | 40–60 | ⬜ Not started | `data/batch-5-automation.md` |
| 6 | Recycling/environmental, wood, metal, plastic, misc. | 40–60 | ⬜ Not started | `data/batch-6-misc.md` |
| Final | Merge + Top-100 ranking + 11-tab workbook | — | ⬜ Not started | `Denmark-Gearbox-OEM-Prospects.xlsx` |

## Per-company fields
Company Name · Website · Headquarters · Industry · Machinery Produced · Gearbox Application ·
Est. Annual Revenue · Employees · Export Markets · Decision Makers (CEO, Purchasing, Eng. Mgr,
R&D, Production, Technical Director, Supply Chain) · LinkedIn Company Page · Decision Maker LinkedIn ·
Existing Gearbox Suppliers (SEW/Nord/Bonfiglioli/Flender/Rossi/Motovario/Bauer/Sumitomo…) ·
Evidence (why they buy gearboxes) · Source Links (2+ independent) · Buying Potential Score (1–10)

## Ground rules
- Every company verified from ≥2 independent sources.
- Distinguish CONFIRMED facts vs INFERRED (label confidence).
- Do not invent data. Blank fields left blank, not fabricated.
- Use Apollo.io (connected) for decision-maker + LinkedIn + firmographics enrichment.
- Prioritize machinery OEMs; exclude gearbox makers/distributors unless they're also OEMs.

## Final deliverable tabs
1. Executive Summary · 2. Top 100 Prospects · 3. Complete Company Database ·
4. Companies by Industry · 5. Companies by Region · 6. High-Potential Targets ·
7. Decision Makers · 8. Existing Gearbox Suppliers · 9. Sales Strategy Recommendations ·
10. Key Market Insights · 11. Quality Requirements

## How to resume
User says e.g. "run batch 1". Claude runs that one batch, writes the output file, commits, updates the Status table above. Repeat per window until all 6 batches done, then run Final.
