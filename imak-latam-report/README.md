# i.Mak — export outreach report (Latin America + Middle East) + WhatsApp proposal

`iMak_Outreach_Report_18Nov2026.pptx` — 13-slide, 16:9, fully editable deck covering **both live
Apollo campaigns** (Latin America and the Middle East) as of 18 Nov 2026, plus a proposal for a new
**1-on-1 WhatsApp channel**. A PDF copy and a one-image preview of all slides sit next to it.

| # | Slide |
|---|-------|
| 1 | Title — combined headline stats |
| 2 | Executive summary — both regions + the WhatsApp move |
| 3 | The full numbers — combined KPIs + Latin America vs Middle East vs Combined table |
| 4 | Two regions, two results — LatAm (active) vs Crane ME (stalled) + the decision |
| 5 | Combined funnel — delivery / reply / bounce (native charts) |
| 6 | Leads — 48 total, notable accounts |
| 7 | Markets & message — Latin America and Middle East maps, languages |
| 8 | Programs & tools |
| 9 | Step by step |
| 10 | Six challenges (incl. the Middle East result) |
| 11 | **New channel — a 1-on-1 WhatsApp channel** |
| 12 | Growth levers |
| 13 | Proposed next steps |

Every slide has speaker notes. Font is Calibri so it opens the same on any Office install.

## The numbers (live from Apollo, 18 Nov 2026)
- **Latin America** (i.Mak Reductores, ES, active): 1,223 sent · 1,200 delivered · 46 leads · 5.7% reply.
- **Middle East** (Crane ME, EN, stalled since 12 Nov): 377 sent · 374 delivered · 2 leads · 1.6% reply.
- **Combined:** 1,600 sent · 1,574 delivered (98.4%) · 48 leads · 26 bounced (1.6%).
- Reply rate = unique repliers per contact reached. A third template sequence exists but was never run.
- WhatsApp figures (3.3B+ users, ~95% open) are **industry benchmarks for opted-in contacts**, not guarantees.

## Updating
All figures live in the `D = dict(...)` block at the top of `build_deck.py`.

```bash
pip install python-pptx pillow
python build_deck.py                                   # rewrites the .pptx
python make_map.py countries-110m.json assets/latam_map.png latam   # only if maps change
python make_map.py countries-110m.json assets/me_map.png    me
```
