# Batch 1 delivered — 200 verified emails

**File:** `gearbox-leads-batch1.csv`
**Date:** 2026-07-28
**Source:** Apollo.io, enriched 2026-07-28

## What's in it

200 contacts, **every one with a verified work email**. No guessed or
pattern-generated addresses — Apollo confirmed all 200.

| Country | Contacts |
|---|---:|
| Zambia | 81 |
| Angola | 71 |
| Botswana | 48 |

| Segment | Contacts |
|---|---:|
| Mining | 50 |
| Distributors & dealers | 46 |
| Agro / cement / food | 43 |
| Energy / oil & gas | 27 |
| Energy / logistics | 20 |
| Mining / construction | 14 |

Spread across **134 companies** — no single account dominates the send.
Largest are First Quantum (12), Debswana (10), Konkola Copper (9), Mopani (6).

## Priority tiers (column in the CSV)

- **A — 46 distributors and dealers.** Resellers who buy repeatedly and stock.
  Highest lifetime value. Work these first.
- **B — 64 mining contacts.** Highest gearbox spend per account. Downtime is
  measured in dollars per hour, so they buy on availability, not price.
- **C — 90 other end users.** Agro, cement, energy, logistics, ports.

## Columns

`First name | Last name | Title | Company | Country | City | Segment | Email |
Email status | Language | Priority tier | LinkedIn | Company domain |
Company phone | Employees | Industry | Suggested angle | Flag`

- **Language** — 71 Angolan contacts are marked Portuguese. Send them English
  and you waste them.
- **Suggested angle** — the opening argument that fits that segment.
- **Flag** — 101 rows are marked "HQ abroad". This is **not** a defect. The
  person is in-country; their employer is a multinational (Komatsu, Liebherr,
  Sulzer, TotalEnergies, GEA). It means confirm whether that person buys
  locally or has to route the order through a regional office. Worth knowing
  before the call, not a reason to drop them.

## What was excluded and why

Screened out during selection: IT managers, HR, security, aviation, geology
and geophysics, NGOs, banks, relocation firms, and government trade agencies.
They appeared in the raw searches on job-title matches but do not buy
gearboxes.

Per-account contact counts were capped on purpose. First Quantum has hundreds
of matching engineers; sending to all of them from a cold domain gets the
domain flagged as spam and kills deliverability for the whole batch.

## Known gaps

- **1 contact dropped:** Ernesto at Zeepack International (Angola) — Apollo
  returned no email. Replaced, so the count is still 200.
- **1 contact worth a second look:** Tshegofatso Mosweu is listed in Botswana
  but the employer (SPTC) is a Saudi transformer manufacturer. Verify before
  sending.
- **No phone numbers.** Emails only, as agreed. Direct dials are a separate
  credit pool (4,000 available) and can be pulled later for whoever engages.

## Credits

200 enrichments, 1 credit per match. Unmatched records cost nothing.
Searching and screening was free.

## Next batches

The pool supports roughly 2,000–3,000 quality contacts before quality drops:

- Batch 2 — remaining mining and energy depth in all three countries
- Batch 3 — second and third contacts at accounts that engage in batch 1
- Batch 4 — adjacent markets on the same industrial logic (Namibia, DRC
  Copperbelt, Mozambique, Zimbabwe)
