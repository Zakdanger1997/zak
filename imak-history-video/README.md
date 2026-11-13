# i.Mak — "50 Years in Motion" (silent history video)

A clean, number-driven motion-infographic telling i.Mak's story — from one İstanbul
workshop in 1973 to a global drive-systems company. Built for LinkedIn and all
social feeds: **square 1080×1080, ~54s, silent** (all information is burned-in
on-screen text, which is what LinkedIn best-practice recommends for sound-off viewing).

Method follows the [iart-ai/data-animation-skills](https://github.com/iart-ai/data-animation-skills)
"animated-infographic" craft: design the static frame first, reveal in importance
order, count numbers up with `tabular-nums` easing, one number moving at a time,
and hold the final composed frame. Every value is a pure function of time
(`window.__seek(t)`), so renders are deterministic.

## Output
- `imak_history_1080sq.mp4` — the deliverable (H.264, yuv420p, 30 fps, no audio).

## Story beats
1. Hook — three meshing gears, "50 years in motion".
2. Origin — "1973", a small İstanbul workshop.
3. 50+ years — count-up, three generations, still family-owned.
4. Built at scale — 16,000 m² plant · 275+ team · 1M+ configurations · 17 series.
5. From Türkiye to the world — animated map, Türkiye origin + mounting/warehouse
   centers (USA, Spain, Poland, India, South Africa) and the new 2026 Egypt facility;
   40+ countries · 26 dealers · 50+ sales offices.
6. Industries served — mining, cement, food, construction, logistics, agriculture,
   quarries, oil & gas.
7. 2026 — still expanding (i·MAK Egypt).
8. End card — logo, "Engineered in Türkiye. Trusted worldwide.", imakreduktor.com.

## Numbers & sources
All figures live in `data.js` with their source. They come from i.Mak's own
site (imakreduktor.com/en — About Us + homepage counters, fetched 2026-11),
cross-checked with SAHA Istanbul and a Defensehere interview. Where sources
disagreed, the company's own conservative figure was used (e.g. "40+ countries"
rather than a news headline's 54). **Edit `data.js` to change any stat and re-render.**

## Assets
- `assets/imak_logo@4x.png` / `assets/logo.js` — the real i.Mak logo (from imakreduktor.com), inlined as a data URI so the canvas isn't tainted.
- `assets/fonts/inter-*.woff2` — Inter (400–900).
- `assets/world.js` — world country polygons (Natural Earth 110m via world-atlas),
  Türkiye isolated for the red highlight. Regenerate with `assets/convert.py`.

## Re-render
```bash
npm i -g playwright   # Chromium is already present in this environment
node render.js test   # key-beat stills -> test/   (verify before full render)
node render.js full   # all frames -> frames/
./encode.sh           # frames -> imak_history_1080sq.mp4 (silent)
```
To preview live, just open `animation.html` in a browser.

## Other aspect ratios
The layout is tuned for 1:1. For 4:5 (1080×1350) or 16:9, change the canvas size
in `animation.html` and the viewport in `render.js`, then re-tune the scene
`y` positions. Ask and this can be produced as an additional cut.
