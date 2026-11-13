# i.Mak — "The price tag is the smallest cost" (drive-selection ROI video)

A silent, number-driven motion-infographic on **how selecting the right industrial
drive/gearbox decides long-term cost** — total cost of ownership, energy, gear
efficiency, downtime and right-sizing. Square **1080×1080, ~49s, silent** (all info
is burned-in text), for LinkedIn and all social. Keeps the i.Mak logo throughout,
and prints the **source of each figure in a small line in-frame**.

Built on the same deterministic canvas pipeline as `imak-history-video`
(method from [iart-ai/data-animation-skills](https://github.com/iart-ai/data-animation-skills)).

## Output
- `imak_cost_of_selection_1080sq.mp4` — the deliverable (H.264, yuv420p, 30 fps, no audio).

## Story beats
1. Hook — "The price tag is the smallest cost."
2. ~53% of the world's electricity runs through electric motors (why efficiency = money).
3. Lifetime cost donut — energy ≈ 90%, service & downtime ≈ 7%, purchase ≈ 3%.
4. The lever — a 1–2% efficiency gain saves more than the drive's price.
5. Gear efficiency — helical up to ~98% vs worm 50–90%.
6. Downtime — ~$125,000/hr average ($2.3M/hr automotive).
7. Right-sizing — undersized vs oversized vs the right service factor.
8. End card — "Select it right — once." + logo, i-Guide, website, combined sources.

## Figures & sources (also printed in the video)
All numbers live in `data.js` with their source:
- Motors ≈ **53%** of global electricity — IEA-4E Electric Motor Systems Annex, 2023.
- **Energy ≈ 90%** of a drive's 15–20 yr cost; **purchase ≈ 2–3%** — U.S. DOE motor life-cycle data.
- **Helical ~98%/stage vs worm 50–90%** — published gear-efficiency data.
- **~$125,000/hr** avg industrial downtime; **$2.3M/hr** automotive — ABB Value of Reliability 2023 · Siemens True Cost of Downtime 2024.

Edit `data.js` to change any figure and re-render.

## Re-render
```bash
node render.js test   # key-beat stills -> test/
node render.js full   # frames -> frames/
./encode.sh           # -> imak_cost_of_selection_1080sq.mp4 (silent)
```
Open `animation.html` in a browser for a live preview.
