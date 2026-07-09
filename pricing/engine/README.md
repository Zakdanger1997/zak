# I-MAK Pricing Engine

A working price-calculation engine over `pricing/data/imak_pricing.db`.

## Buildup

```
  base unit (gearbox+motor, foot or flange)   ← imak_geared_motors (TL/EUR/USD native)
+ brake                                        ← emf_brakes (matched by output torque + mounting)
+ option adders (%-based)                      ← config.json option_rules
= list subtotal
→ margin        (discount off list  OR  cost + markup)   ← config.json margin / customer_tiers
→ payment term  (surcharge % for deferred payment)       ← config.json payment_terms
→ VAT           (optional)
= customer total  (in TL / EUR / USD)
```

## Usage

```bash
cd pricing/engine

# find matching units
python pricer.py search "İRM 82" --currency TL

# a plain list-price quote
python pricer.py quote --type "İRM 82 İR 63 / 71 M4a" --currency TL --mount foot

# full quote: dealer discount tier, brake (200 Nm), special shaft, 30-day term, VAT
python pricer.py quote --type "İRM 82 İR 63 / 71 M4a" --currency TL \
    --brake --brake-torque 200 --option special_output_shaft \
    --customer DEALER_A --term 30d --vat
```

`build_quote()` is also importable for a web/n8n/Excel front-end later — it returns a
structured dict (line items + each stage total), not just text.

## Configuration — `config.json` (all rates ADJUSTABLE)

- **`margin.mode`** — `discount` (list price − discount%) or `markup` (cost + markup%). Supports **both** so you can switch when you confirm your model.
- **`customer_tiers`** — per-customer margin overrides (example DEALER_A −25%, OEM_B +18%).
- **`payment_terms`** — deferred-payment surcharge %. Seeded from the GAMAK 2026-01 bulletin; **replace with I-MAK's own term rates**.
- **`option_rules`** — %-adders from I-MAK catalogue notes (special shaft +6%, İRAF +5%, MA/MK Atex +10%, …).
- **`vat_pct`**, **`brake_default_variant`**.

## Current assumptions (correct me and I'll change)
1. **Margin model defaults to `discount` at 0%** → output = list price until you set real rates. (Question was: discount-off-list vs cost+markup — engine supports both.)
2. **TL / EUR / USD are stored natively** (parallel I-MAK lists) — no FX conversion for standard/MA-MK ranges.
3. Geared-motor base price **already includes the motor** (İRM/İRKM/… rows). For bare gear + separate motor use `imak_iec_units` + `gamak_motors` (buildup path to be added).

## Known limitations / next steps
- **Brake auto-sizing needs the unit's rated output torque**, which lives in the *catalogues*, not the price list — so pass `--brake-torque` for now. Next: extract the torque/ratio rating tables from the catalogue PDFs and join them so the engine sizes brakes (and validates service factor) automatically.
- **IEC/PAM + separate GAMAK motor buildup** path not yet wired (data is present).
- **Competitor cross-reference** (`comp_yilmaz_*`) not yet linked into a "competitor model → I-MAK equivalent → price" flow — needs the in-house comparison sheets to encode the mapping.
- EMF brake cooled/uncooled prices share one extracted variant string — verify against source before quoting brakes.
