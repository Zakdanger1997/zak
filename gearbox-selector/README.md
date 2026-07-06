# I-MAK Gearbox Selector

A field tool that sizes an I-MAK gearbox for a given application. It works fully
offline (single self-contained HTML file, no internet needed) and now assigns a
**specific sizing formula to every application**.

## Files

| File | Use |
|------|-----|
| `imak-gearbox-selector-windows.html` | **Windows / desktop** version — wide two-column workspace |
| `imak-gearbox-selector-phone.html` | **Phone** version — single column, large touch targets, no input zoom |
| `IMAK-Gearbox-Formulas.xlsx` | Every formula, service factor, variable & default — review and edit here |

Both HTML files share the **same calculation engine**, so results are identical;
only the layout differs. Just double-click a file to open it in any browser.

## What was fixed

Previously 9 applications had **no formula** and fell back to manual entry. Every
application now has its own process calculator:

| Application | Formula added |
|-------------|---------------|
| Escalator / moving walk | `P = (1+k)·(pax/3600)·mp·g·H/1000` |
| Crane — slewing drive | `T₂ = J·α + Tf`, `J = m·r²` |
| Passenger lift / elevator | `P = Q·(1−b)·g·v/1000` |
| Rotary kiln / drying drum | `T₂ = (1+k)·m·g·(D/2)·e` |
| Extruder — plastic / rubber | `P = SME·Q`, `T₂ = 9550·P/n` |
| Sifter / plansifter drive | `P = k·m·r²·ω³/1000` |
| Vibrating screen / shaker | `P = k·m·A²·ω³/1000` |
| Rotary table / turntable | `T₂ = J·α + Tf`, `J = 0.5·m·r²` |

The existing belt, screw, bucket-elevator, hoist, travel, agitator, pump, fan and
grinding/crushing formulas were kept and verified.

## How a selection is computed

1. **Process data** → the application's formula returns output power `P_out` (kW)
   or output torque `T₂` (N·m) and output speed `n₂`.
2. `T₂ = 9550·P_out/n₂`  (or `P_out = T₂·n₂/9550`).
3. Service factor `SF = base(duty) + load adjustment` (min 1.00).
4. **Required nominal torque `Tn = T₂ × SF`** — pick an I-MAK unit with catalogue
   `Tn ≥` this value.
5. Motor `= P_out / η`, rounded up to the next IEC standard kW.

## Editing the formulas

Open `IMAK-Gearbox-Formulas.xlsx` — the *Variables & defaults* and *Formula
library* sheets document every equation and default. Change what you need and send
it back, and both app versions can be regenerated to match.

> Process-mode results are **field estimates**. Always confirm the final choice
> against the I-MAK catalogue (nominal torque, ratio, overhung-load & thermal
> rating). Cranes, hoists and lifts also need FEM/ISO duty-class and braking review.
