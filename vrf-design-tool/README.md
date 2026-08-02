# VRF System Design Tool

An **open, catalog-agnostic** design workbook for VRF / multi-split air-conditioning
systems — inspired by the *kind* of workflow that professional tools like Samsung's
DVM Pro 2, Daikin's VRV Xpress, Mitsubishi's Diamond System Builder, or LG's LATS
provide, but built entirely from **public HVAC engineering principles**.

It runs as a single self-contained `index.html` file — no install, no server, no
internet. Open it in any browser (desktop or phone) and it works.

## Important: what this is and isn't

- ✅ It **is** an original engineering aid that automates the repetitive VRF design
  math (combination ratio, capacity corrections, pipe sizing, refrigerant charge, BOM).
- ❌ It **is not** a copy of DVM Pro or any manufacturer's software, and it contains
  **none of their proprietary product data**. Manufacturer software is valuable
  precisely because it carries the private engineering database for that brand's
  equipment (exact capacities, pipe rules, correction curves, allowable combinations).
  That data is copyrighted and not reproduced here.
- 📥 **You supply the numbers.** Every table (pipe sizing, correction curves, charge
  rates, unit capacities) is editable. Paste the figures from your chosen
  manufacturer's engineering manual and the tool does the arithmetic. Results are only
  as correct as the catalog data you enter.

> For an actual Samsung DVM installation, always validate the final design in Samsung's
> official DVM Pro software before ordering or commissioning. This tool is a helper and
> a learning aid, not a substitute for the manufacturer's approved selection software.

## Features

| Tab | What it does |
|-----|--------------|
| **Project** | Job details + design ambient conditions and a diversity/simultaneity factor. |
| **Rooms & loads** | One row per indoor unit. Enter load directly, or area × W/m² to estimate. Totals connected indoor capacity and design load. |
| **Outdoor / CR** | Enter the outdoor unit and its capacity; computes the **combination ratio** and flags if it falls outside your allowable window (default 50–130%). |
| **Correction** | Editable length- and height-difference correction curves; interpolates the capacity-correction factor and the corrected outdoor capacity. |
| **Piping** | Editable capacity→diameter sizing table and per-metre charge table. Add pipe segments; liquid/gas diameter and additional charge are computed per segment. |
| **Charge** | Factory pre-charge + additional piping charge = total refrigerant charge. |
| **Summary / BOM** | One-page design summary and a bill of materials. Export CSV, or Print/PDF. |

Other niceties: autosaves to your browser (localStorage), **Save/Load** a project as a
`.json` file, **Print/PDF** a clean report, and **Export CSV** of the summary.

## Using it

1. Open `index.html` in a browser.
2. Fill in the **Project** conditions.
3. Add your rooms/indoor units under **Rooms & loads**.
4. On **Outdoor / CR**, enter the outdoor unit — watch the combination ratio.
5. On **Correction**, paste your manufacturer's length/height correction points.
6. On **Piping**, paste the sizing and charge tables, then add pipe segments.
7. Review **Summary / BOM**, then Print/PDF or Export CSV.

The default numbers loaded in the tables are **generic placeholders** to show the shape
of the data — replace them with your equipment's real figures.

## Defaults are placeholders

The sizing table, correction curves and charge rates shipped in the file are illustrative
round numbers, **not** any manufacturer's certified data. Do not use the defaults for a
real installation without replacing them.
