# I-MAK Pricing Data (extracted from price lists)

Structured price data extracted from 14 official/competitor price-list PDFs. Extraction scripts live in `pricing/scripts/`; re-run them to refresh. Everything is also loaded into **`imak_pricing.db`** (SQLite).

> **Source PDFs are proprietary** and are **not** committed (git-ignored in `pricing/pricelists/`).

## Tables (~10,060 priced rows)

### I-MAK own products
| Table / CSV | Rows | Currency | Content |
|---|---|---|---|
| `imak_geared_motors` | 5,259 | **TL + EUR + USD** | Geared-motor SKUs (İRM/İRKM/YPM/İRSM/İRSDM/İRCM). Each row = gearbox+motor combo, foot & flange price. 1,753 SKUs × 3 currencies |
| `imak_iec_units` | 1,855 | TL/EUR/USD | Gear units + IEC/PAM motor adapter (İRP/İRKP/YPP…), B5/B14 flange |
| `imak_simple_types` | 337 | TL/EUR/USD | Industrial A, shaft-mount İRNX/İRO, specials AD/ADS/ADK, IP67 |
| `imak_mamk_options` | 737 | TL/EUR/USD | MA/MK & MAE/MKE monoblock/extruder + options (backstop, cooling coil, fan, heat exchangers, expansion tanks, Atex adders) |
| `imak_planetary` | 931 | EUR | IPR/IPRK planetary matrix: size × input-config (FS/FC/HS/HC…) × stage (S1–S5) |

### Suppliers (buildup components)
| Table | Rows | Currency | Content |
|---|---|---|---|
| `gamak_motors` | 327 | TL (Ex=USD) | Electric motors by IE class (IE1–IE4 + ATEX/Ex): power, frame/pole, price |
| `emf_brakes` | 401 | TL (+DEX €) | Brakes/clutches (YBF/DEX/dusty/servo), torque, bare vs motor-mounted variants |
| `kaplin_couplings` | 51 | TL | Coupling prices (semi-structured) |

### Distributor / customer-specific I-MAK lists
| Table | Rows | Currency | Content |
|---|---|---|---|
| `cema_customer_options` | 34 | USD | CEMA customer: output-shaft (standard/stainless) + flange adders for İRK/YP |
| `redservis_s_series` | 30 | EUR | Redservis Russia: S-series worm — gearbox, flange, single/double shaft, torque arm |

### Competitor
| Table | Rows | Currency | Content |
|---|---|---|---|
| `comp_yilmaz_planetary_units` | 68 | TL | **Yılmaz** planetary PT/RT bare units, L (→our IPR) & K (→our IPRK) variants, dated 08.09.2025 |
| `comp_yilmaz_planetary_options` | 33 | TL | Yılmaz twin-shaft, shrink-disk, drum-flange, single/double torque-arm adders |

## Key column notes
- **`imak_geared_motors`**: `currency, series, page, power_kw, power_hp, output_rpm, type_full, gearbox, motor, price_foot, price_flange`. `type_full` e.g. `İRM 143 IR 73 / 71 M4a` → gearbox `İRM 143 IR 73`, motor `71 M4a`. `Standart`=standard-fit, `-`=not offered.
- **`imak_planetary`**: `size, series(IPR/IPRK), stage(S1–S5), input_config(FS/FC/HS/HC…), price_eur`.
- **`gamak_motors`**: `ie_class ∈ {IE1,IE2,IE3,IE4,IE-}`, `motor_type` e.g. `M22D 71 M 2a`.
- **`comp_yilmaz_planetary_units`**: `model_base` (e.g. 2302), `variant` L/K, `imak_equiv_series` (IPR/IPRK), `pt_price_tl`, `rt_price_tl`.

## Currency & terms
- **TL / EUR / USD parallel lists** — the engine stores all three natively (no conversion needed for I-MAK standard/MA-MK).
- Only-EUR: I-MAK Planetary, Redservis. Only-USD: CEMA. TL(+€): EMF. TL(+USD Ex): GAMAK.
- GAMAK payment-term uplift (bulletin 2026-01): TL cash→30/60/90d **+3.98% / +8.13% / +12.45%**; Exproof USD **+0.75% / +1.50%**.

## Extraction caveats (verify against source before quoting)
- **Yılmaz competitor** data is transcribed from a **rotated scanned PDF** (no text layer) — the PT/RT bare-unit table (p5) + options are captured; the dense **PN/RN geared-motor** tables (pp1–4, ~1,200 values) are **not yet transcribed** — get a digital copy or request full OCR. Treat transcribed numbers as verify-before-quote.
- I-MAK hoist İRCM uses a doubled side-by-side layout — split programmatically; spot-check.
- `imak_mamk_options` & `kaplin_couplings` kept semi-structured (`cells`) — normalized per-option when wiring the engine.
