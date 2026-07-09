# I-MAK Pricing Data (extracted from price lists)

Structured price data extracted from the official price-list PDFs (all dated **26.01.2026**, GAMAK **18.05.2026**). Extraction scripts live in `pricing/scripts/`; re-run them to refresh.

> **Source PDFs are proprietary** and are **not** committed (git-ignored). They live in `pricing/pricelists/` locally.

## Tables (also loaded into `imak_pricing.db` SQLite)

| File / table | Rows | Source | Currency | What it is |
|---|---|---|---|---|
| `imak_geared_motors.csv` | 1,753 | I-MAK main list | **TL** | Geared-motor SKUs (İRM/İRKM/YPM/İRSM/İRSDM/SM/İRCM). Each row = gearbox+motor combo with foot & flange price |
| `imak_iec_units.csv` | 627 | I-MAK main list | **TL** | Gear units with IEC/PAM motor adapter (İRP/İRKP/YPP…). Bare gear + B5/B14 flange |
| `imak_simple_types.csv` | 140 | I-MAK main list | **TL** | Simple type→price (industrial A series, shaft-mount İRNX/İRO, special AD/ADS/ADK, IP67, options) |
| `imak_mamk_euro_options.csv` | 245 | I-MAK MA/MK list | **EUR** | MA/MK & MAE/MKE industrial/extruder: splined shafts, backstops, cooling coils, fans, heat exchangers, expansion tanks, Atex/special adders |
| `gamak_motors.csv` | 327 | GAMAK list | **TL** (exproof USD) | Electric motors by IE class (IE1-IE4 + ATEX/Ex): power, type/frame/pole, price |
| `emf_brakes.csv` | 401 | EMF Fren list | **TL** (+ DEX in EUR) | Brakes/clutches by family (YBF AC, DEX, dusty, servo, natural-magnet): torque, bare vs motor-mounted variants |

**Total: ~3,490 priced rows.**

## Column notes

**`imak_geared_motors.csv`** — `series, page, power_kw, power_hp, output_rpm, type_full, gearbox, motor, price_foot_tl, price_flange_tl`
- `type_full` e.g. `İRM 143 IR 73 / 71 M4a` → `gearbox`=`İRM 143 IR 73`, `motor`=`71 M4a`.
- `output_rpm` is the output-speed *range* across the ratio band, e.g. `0,13-0,48`.
- Prices are TL; `Standart` = standard-fit (no upcharge), `-` = not offered.

**`gamak_motors.csv`** — `ie_class` ∈ {IE1,IE2,IE3,IE4,IE-}; `motor_type` e.g. `M22D 71 M 2a` (frame 71, 2-pole).

**`emf_brakes.csv`** — `price_variant` distinguishes ÇIPLAK FREN (bare brake) vs MOTORA MONTAJLI (motor-mounted, cooled/uncooled) vs flange-mounted. Match brake to motor by `torque_nm` and motor frame.

## Known extraction caveats (to verify against source before quoting)
- I-MAK **hoist İRCM** table is a doubled side-by-side layout — split programmatically; spot-check a few rows.
- A handful of `type_full` strings carry an `(*P)` PAM marker; kept verbatim.
- MA/MK options CSV is kept as `page | table | cells` (semi-structured) because its many small tables share no single schema — fine for lookup, will be normalized per-option when we wire the engine.
- Currency is **not** auto-converted. FX (TL⇄EUR⇄USD) must be a system parameter (see engine design).

## Currency & payment terms
- I-MAK gearboxes + GAMAK motors + EMF (YBF) brakes: **TL**.
- I-MAK MA/MK + EMF DEX + exproof motors: **EUR / USD**.
- GAMAK term uplift (from bulletin 2026-01): TL cash→30/60/90 days **+3.98% / +8.13% / +12.45%**; Exproof USD **+0.75% / +1.50%**. These are payment-term surcharges the quote engine should apply.
