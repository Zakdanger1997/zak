# i.Mak Redüktör Seçim Programı

A browser-based gearbox selection tool for [i.Mak Redüktör](https://www.imakreduktor.com), built on the power/speed tables of i.Mak's own public catalogues. It follows the four-step flow familiar from manufacturer selection programs (operating conditions → drive data → forces and options → result) and works entirely offline once the three files are on disk.

Open `index.html` in a browser. No build step, server or dependency is needed at run time.

## What it does

1. **Operating conditions.** Pick the driven machine from the catalogue's load-characteristics list (89 machines in 10 groups), the prime mover and the daily operating hours. The required service factor fs comes from the i.Mak service-factor table (electric motor / piston engines × 0–3 h, 3–10 h, 10–24 h × load class U/M/H). A manual override is available.
2. **Drive data.** Choose the family (IR helical, IRK helical-bevel, YP parallel-shaft, IRS worm, IRSD helical-worm, S aluminium worm), geared motor or motorless gear unit, the given quantity (motor power P1 or required torque M2), output speed n2 with a tolerance, motor poles, 50/60 Hz and the efficiency class.
3. **Forces and options.** Mounting (foot / flange / both), an optional radial-force check (calculated from the transmission element and its pitch diameter, or your own value), mounting position, brake, backstop, encoder, forced cooling.
4. **Result.** Every catalogue row whose output speed is within tolerance and whose service factor and radial load are sufficient, smallest size first. Clicking a row shows the full designation (type, size, primary stage, motor code), ratio, speed deviation, torque, actual service factor, permissible radial load, weights and catalogue dimension pages of each mounting variant, a link into the catalogue PDF table, and a copyable selection summary.

Turkish and English interface. Inputs are remembered in the browser.

## Data

| File | Content | Source |
|------|---------|--------|
| `data/catalog.js` | 11 516 performance-table rows in 1 390 size groups (IR, IRK, YP, IRS, IRSD, S) | IR 2026 Rev.01, IRK 2026, YP 2026 Rev.02, IRS/IRSD 2026 Rev.01 catalogues |
| `data/applications.js` | Load class (U/M/H) of 89 driven machines | YP catalogue, "Load characteristics of gearboxes" |
| service-factor table, family ranges | hard-coded in `index.html` | YP catalogue p. 10–13; 2026 summary catalogue |

Three table kinds are parsed:

- **Geared motors** (`k: "motor"`): P1, n2, i, service factor, M2, permissible radial load FR at mid-shaft, type variants, size / primary gear unit / motor code, dimension pages, weights. Rows are `[n2, i, Sf, M2, FR]`; IRSD rows carry the worm-stage ratio as a sixth value.
- **Gear units without motor** (`k: "unit"`, IRK and YP): at a fixed input speed n1 (1400, 900 or 700 rpm) and service factor 1: table P1, n2, i, rated torque M2n, radial load at input and output. Rows are `[P1, n2, i, M2n, FR_in, FR_out]`.
- **Helical-worm** units (IRSD) with two ratio columns.

The catalogues print the motor power once per power block rather than per size group, so `tools/build_data.py` resolves P1 per motor code (for example `63M 4a` = 0,12 kW) from the kW labels found in its groups, disambiguating the horsepower labels printed beneath them, and cross-checks against the shaft power `M2·n2/9550` of the helical families. The build log lists every code and how it was resolved.

### Rebuilding the data

```bash
pip install pdfplumber
# download the four catalogue PDFs from https://www.imakreduktor.com/catalogs/ into a folder, then:
python3 tools/parse_catalogs.py IR_Katalog_2026_Rev.01.pdf        IR  raw_IR.json
python3 tools/parse_catalogs.py IRK-Katalog-web.pdf               IRK raw_IRK.json
python3 tools/parse_catalogs.py YP-Katalog-2026-Rev.02.pdf        YP  raw_YP.json
python3 tools/parse_catalogs.py IRS_IRSD_Katalog_2026_Rev.01.pdf  IRS raw_IRS.json
python3 tools/build_data.py data/catalog.js raw_IR.json raw_IRK.json raw_YP.json raw_IRS.json
```

`parse_catalogs.py` reads each table page with pdfplumber: column positions come from the unit labels in the header (`[kW]`, `[r.p.m]`, `[Nm]`, `[N]`), size groups from the shaded blocks and full-width separator rules, and the type annotation that sits inside each group. Pages whose layout differs are skipped and reported.

## Selection logic

- Required service factor `fs_req` from the table (or the manual value).
- **Geared motor, P1 given:** rows of groups with that P1 (and pole count) where `|n2 − n2_req| ≤ tol` and `Sf ≥ fs_req`.
- **Geared motor, M2 given:** rows where `|n2 − n2_req| ≤ tol`, `M2_row ≥ M2_req` and `M2_row·Sf / M2_req ≥ fs_req`; the smallest motor and size come first.
- **Gear unit:** rows at the chosen n1 where `|n2 − n2_req| ≤ tol` and `M2n / M2_req ≥ fs_req`; the required input power is `P1_table · M2_req / M2n`.
- **Radial load:** `FR = 2000 · M2 · fz / d0` (M2 in Nm, d0 in mm; fz: gear 1,15, chain 1,40, timing belt 1,50, V-belt 1,75, flat belt 2,50) compared with the catalogue's permissible value.
- **60 Hz:** the 50 Hz table values are scaled ×1,2 in speed and power and marked as approximate.

## Limits

- Only the six series with machine-readable performance tables are included. IRC, MA/MK, IRNX, IRO, A/AE, IPR/IPRK, 4DS and AD/ADK/ADS are listed with a pointer to the catalogues.
- Thermal rating, mounting-position oil quantities, axial loads, brake sizing and non-standard voltages are not checked.
- This is a pre-selection aid built from published tables. Confirm the final choice with i.Mak or their official [i-Guide](https://iguide.imakreduktor.com/) application.

## Files

```
imak-reduktor-secim/
├── index.html              # the application (single page, no dependencies)
├── data/
│   ├── catalog.js          # generated performance-table data
│   └── applications.js     # generated load-class list
├── tools/
│   ├── parse_catalogs.py   # PDF → raw JSON
│   ├── build_data.py       # raw JSON → data/catalog.js (+ validation report)
│   └── apps.py             # YP catalogue text → data/applications.js
└── README.md
```

i.Mak, the series names and the catalogue values belong to İ.MAK Redüktör San. ve Tic. A.Ş. This tool is an independent reading of their public documents.
