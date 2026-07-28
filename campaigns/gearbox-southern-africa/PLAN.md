# Gearbox Leads — Botswana, Zambia, Angola (Batch 1: 200 contacts)

**Status:** Plan — awaiting approval before any credits are spent
**Source:** Apollo.io (connected, live)
**Date:** 2026-07-28

---

## 1. Assumption I'm working from

You sell / supply **industrial gearboxes** (gear units, reducers, drive
components) and want to open Botswana, Zambia and Angola. Buyers are therefore
two different animals:

- **Resellers** — distributors, dealers, spare-parts traders, engineering
  suppliers. They stock and resell. Lower volume of targets, highest lifetime
  value, they buy repeatedly.
- **End users** — mines, sugar/agro plants, cement, breweries, oil & gas,
  ports, construction and haulage fleets. They buy for replacement and
  breakdown. Bigger pool, faster first order.

Batch 1 covers both. If this assumption is wrong (e.g. you only want
distributors, or you make gearboxes for a specific application), say so and I
re-cut the targeting before building.

---

## 2. What Apollo actually has — verified, not estimated

I ran live searches. These are real counts from the database today:

**Raw pool, technical + procurement titles, by country**

| Country  | Contacts available |
|----------|-------------------:|
| Zambia   | 2,565 |
| Angola   | 1,793 |
| Botswana | 1,103 |
| **Total**| **5,461** |

**By buying segment, across all three countries**

| Segment | Pool | Read |
|---|---:|---|
| Energy / oil & gas / construction / logistics / marine | 2,160 | Deepest pool, Angola-heavy |
| Mining, minerals, quarrying, copper, diamond | 640 | Highest gearbox spend per account |
| Agro-processing, sugar, milling, cement, brewery | 269 | Steady replacement demand |
| Industrial distributors, power transmission, bearings, spares | 169 | Small but the highest-leverage list |

**Live accounts already confirmed sitting in these results:** Debswana Diamond,
Lucara Diamond, First Quantum Minerals, Zambia Sugar, Azule Energy, Zambeef,
BIA Group, Blumaq, DP World, TechnipFMC, Nors Group, Unitrans, BME (Omnia).

Conclusion: 200 is comfortably available, and so is the rest of the list later.
The pool supports roughly 2,000–3,000 quality contacts total before we start
scraping the bottom.

---

## 3. The 200 — how I'd split it

| Segment | Botswana | Zambia | Angola | Total |
|---|---:|---:|---:|---:|
| Mining & minerals | 25 | 35 | 10 | **70** |
| Energy / construction / logistics / marine | 10 | 10 | 30 | **50** |
| Distributors & spare-parts dealers | 10 | 15 | 15 | **40** |
| Agro / sugar / cement / food | 5 | 20 | 15 | **40** |
| **Total** | **50** | **80** | **70** | **200** |

Why this shape:

- **Zambia gets the most (80)** — copper mining plus a real agro-processing
  base, and the deepest data coverage of the three.
- **Angola gets 70** — the industrial base is oil & gas, ports and
  construction, so the mix tilts away from mining.
- **Botswana gets 50** — smaller economy, but diamond mining (Debswana,
  Lucara) is concentrated, high-spend and easy to name-target.
- **Distributors capped at 40** — the pool is only 169 and I want the best of
  it, not all of it. These are the accounts worth a phone call, not just email.

---

## 4. Who exactly gets pulled

Two contacts maximum per company — one technical, one commercial — so we
multithread instead of betting the account on one inbox.

**Tier A — technical / specifies the part**
Maintenance Manager, Engineering Manager, Plant Manager, Workshop Manager,
Reliability Engineer, Mechanical Engineer, Technical Manager

**Tier B — buys the part**
Procurement Manager, Purchasing Manager, Supply Chain Manager, Stores Manager,
Spare Parts Manager

**Tier C — distributor principals**
Managing Director, General Manager, Sales Director, Branch Manager, Technical
Sales Manager

Quality gates applied before anything is enriched:
- Contact must be physically located in BW / ZM / AO (not a regional HQ
  elsewhere claiming the territory)
- Company must be industrial — no banks, telcos, NGOs, consultancies
- Dedupe by company domain, max 2 per account
- Prefer records Apollo flags as having a verified email

---

## 5. Build steps once you approve

1. Run the segmented searches (free — no credits).
2. Screen the raw results against the quality gates above; drop the noise.
3. Load the survivors into an Apollo record collection so the work persists,
   is resumable, and exports cleanly. List label: `Gearbox SA — Batch 1`.
4. Enrich for **verified work email** — this is the step that costs credits.
5. Reveal **direct dials for the top ~60 only** (distributors + the largest
   mining accounts). Phone credits are a separate pool and we have plenty, but
   there's no point buying numbers for people we'll only email.
6. Export the finished CSV.

---

## 6. What it costs

Your Apollo account right now: **3,251 unified credits**, **3,455 lead credits
remaining**, **4,000 direct-dial credits**, and waterfall enrichment (email +
phone) is enabled.

| Step | Cost |
|---|---|
| All searching and screening | 0 credits |
| 200 email enrichments | ~200 lead credits |
| ~60 direct dials | from the separate 4,000 direct-dial pool |
| **Batch 1 total** | **~200 of 3,455 lead credits (~6%)** |

Leaves roughly 3,250 lead credits — enough for the next 3,000-odd contacts
without topping up. Waterfall fills gaps where Apollo's own data is thin;
its cost varies by provider, so I'll only switch it on for records that come
back empty, and I'll tell you the count before I do.

---

## 7. What you get

A CSV, one row per contact:

`First | Last | Title | Company | Country | City | Segment | Email |
Email status | Direct dial | LinkedIn | Company domain | Company phone |
Employees | Industry | Priority tier | Suggested angle`

Plus the same 200 sitting in an Apollo list, ready to drop straight into a
sequence.

---

## 8. Attack angles per segment

Not part of the 200, but this is how I'd hit them — worth agreeing now because
it changes which contact in each account we lead with.

- **Mining** — downtime cost. A failed mill or conveyor drive is measured in
  dollars per hour. Lead technical, lead with lead time and availability.
- **Distributors** — margin and stocking terms. Lead with the MD/GM, lead with
  the commercial offer, not the spec sheet.
- **Agro / sugar** — seasonality. Crushing season is fixed; they buy spares
  before it, not during. Timing beats price.
- **Energy / ports / construction** — fleet and materials handling drives.
  Lead procurement, lead with a parts catalogue and turnaround time.

**Language:** Angola is Portuguese. Those 70 contacts get Portuguese emails or
they get deleted. Botswana and Zambia are English.

---

## 9. Two decisions I need from you

1. **Is the assumption in section 1 right?** If you only want distributors, the
   200 changes shape completely — I'd widen the title net and go deeper into a
   smaller account list.
2. **Direct dials — top 60, or all 200?** Top 60 is my recommendation. All 200
   is affordable, it's just mostly wasted on people who'll never pick up a cold
   call from abroad.

Everything else I'll run on the defaults above.

---

## 10. After batch 1

The pool supports 2,000–3,000 quality contacts. Natural next cuts, in the
order I'd take them:

- Batch 2 — remaining mining + energy depth in all three countries
- Batch 3 — second and third contacts at accounts that engaged in batch 1
- Batch 4 — adjacent markets on the same industrial logic (Namibia, DRC
  Copperbelt, Mozambique, Zimbabwe)
