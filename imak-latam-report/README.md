# i.Mak — Latin America outreach campaign report (PowerPoint)

`iMak_LatAm_Campaign_Report_18Nov2026.pptx` — 11-slide, 16:9, fully editable deck built from the
campaign report of 18 Nov 2026 (figures pulled live from Apollo that day). A PDF copy and a
one-image preview of all slides sit next to it.

| # | Slide |
|---|-------|
| 1 | Title — headline stats |
| 2 | Executive summary — the campaign in one slide |
| 3 | The full numbers — six KPIs and progress to the 2,000 goal |
| 4 | From send to reply — funnel and delivery / reply / bounce rates (native charts) |
| 5 | Leads — 51 replies, notable accounts |
| 6 | Market & message — map of target markets, industries, Spanish subject line |
| 7 | Programs and tools |
| 8 | Step by step — the ten steps |
| 9 | Six challenges |
| 10 | Seven levers to gain more |
| 11 | Proposed next steps |

Every slide has speaker notes. Font is Calibri, so it opens the same on any Office install.

## Updating the numbers
All figures live in the `D = dict(...)` block at the top of `build_deck.py`; percentages and
ratios are computed from them.

```bash
pip install python-pptx pillow
python build_deck.py                       # rewrites the .pptx
# only if the map needs regenerating (world-atlas countries-110m.json):
python make_map.py countries-110m.json assets/latam_map.png
```
