# GCC Cement Industry Cold-Call Database – Data Quality Report

Built 2026-09-28 from the connected Apollo.io account. One contact per company, Apollo-verified work emails only, no guessed emails, no existing Apollo contacts.

## Headline numbers

| Metric | Result |
|---|---|
| Companies delivered | **100** (target 100) |
| Unique companies (Apollo org id / domain) | 100 / 100 – zero duplicates |
| Contacts (exactly one per company) | 100 |
| Apollo-verified professional emails | **100 / 100** (email_status = verified) |
| Guessed / pattern emails | 0 |
| Existing Apollo contacts found in list | **0** (checked by person id, email, LinkedIn, name+company against 754 existing contacts) |
| Top-50 phone list | **50 companies, 50 usable Apollo phone numbers** |
| – personal mobile / direct (Apollo reveal) | 36 mobile + 3 office line |
| – company switchboard (Apollo) | 11 |
| Rows with any phone in the full 100 | 86 |
| Contacts located in GCC | 100 / 100 |
| Catch-all email domains (still Apollo-verified) | 25 – flagged in Notes |
| Average / min / max lead score | 77.6 / 58 / 100 |

## Company mix – honest breakdown

Apollo indexes roughly 50 genuine cement manufacturers across the GCC. After removing duplicates, traders, companies with no verified-email decision-maker, and contacts based outside the GCC, **42 primary cement manufacturers** qualified. The remaining **58 companies are secondary cement-products / concrete manufacturers** (precast, AAC, concrete pipes, blocks, large ready-mix), used only because the primary pool was exhausted, exactly as the brief allowed. Every secondary row is flagged in the Notes column.

| Cement activity type | Companies |
|---|---|
| Cement manufacturer (integrated plant) | 34 |
| Precast concrete manufacturer | 32 |
| Concrete pipes & products manufacturer | 9 |
| Ready-mix concrete producer | 7 |
| Cement (white cement plant) | 6 |
| Concrete / building materials manufacturer | 4 |
| AAC / lightweight concrete manufacturer | 3 |
| Cement / cementitious products | 3 |
| Cement (grinding / blended) | 2 |

| Category | Companies |
|---|---|
| Secondary – cement products / concrete | 58 |
| Primary – cement manufacturer | 42 |

## Country distribution (100 companies)

| Country | Companies |
|---|---|
| United Arab Emirates | 44 |
| Saudi Arabia | 36 |
| Oman | 7 |
| Bahrain | 5 |
| Kuwait | 4 |
| Qatar | 4 |

Top-50 phone list by country: United Arab Emirates 20, Saudi Arabia 18, Oman 4, Kuwait 3, Bahrain 3, Qatar 2. Top-50 by category: Primary – cement manufacturer 38, Secondary – cement products / concrete 12.

## Company size

| Apollo est. employees | Companies |
|---|---|
| 200-999 | 34 |
| 50-199 | 28 |
| 1000+ | 21 |
| <50 | 17 |

## Contact priority mix

| Priority | Contacts |
|---|---|
| P1 Procurement/Purchasing | 34 |
| P3 Plant/Operations/Production | 24 |
| P2 Maintenance/Engineering | 22 |
| P4 Buyer/Specialist/Engineer | 16 |
| P5 GM/COO (plant-level exec) | 4 |

## Tiers

| Tier | Companies |
|---|---|
| B | 36 |
| A | 32 |
| C | 32 |

Tier A = score 85+, Tier B = 70–84, Tier C = below 70.

## Scoring model (/100)

| Component | Max | How scored |
|---|---|---|
| Cement Industry Fit | 30 | Integrated cement plant 30 · white cement 28 · grinding/blended 26 · cement products 22 · precast/AAC 18 · pipes/blocks 16–17 · ready-mix 14 |
| Industrial Scale | 20 | 1000+ staff 20 · 500–999 17 · 200–499 14 · 100–199 11 · 50–99 8 · 20–49 5 · <20 2 |
| Equipment Intensity | 20 | Kilns/mills/crushers 20 · white cement 18 · grinding 16 · precast/AAC/pipes 13 · blocks 11 · ready-mix 10 |
| Contact Quality | 15 | P1 procurement 15 · P2 maintenance/engineering 13 · P3 plant/ops/production 11 · P5 GM/COO 9 · P4 buyer/engineer 8 |
| Verified Data | 10 | Verified email 6 · LinkedIn 2 · company phone 1 · non-catch-all domain 1 |
| GCC Market Relevance | 5 | Company and contact both in GCC 5 |

## Phone list method

Phone reveals were run for the top-ranked companies (one contact each). Apollo returned a personal number for 39 of 53 reveal attempts; where no personal number exists the Apollo company switchboard number is supplied instead. Two companies inside the top 52 (AL KHALIJ CEMENT COMPANY, Baitak Group For Construction Materials) have neither a personal nor a company number in Apollo, so the phone list is the 50 highest-ranked companies **with** a usable number (ranks 1–52 minus those two). Those two companies remain in the master list with email only.

5 revealed mobiles are non-GCC numbers (contact's roaming/home-country mobile; Apollo places the contact in the GCC) – flagged in Phone Type: Al Tasnim Enterprises LLC; Cemex UAE; Umm AlQura Cement Co. (UACC); Northern Region Cement Company; Super Cement Manufacturing Company L.L.C.

## Rejected / reserve

| Rejection reason | Count |
|---|---|
| title not a procurement/maintenance/plant role | 10 |
| company HQ outside GCC (India) | 1 |
| contact based outside GCC (United States) | 1 |
| contact based outside GCC (Egypt) | 1 |
| contact based outside GCC (India) | 1 |
| supervisor-level only | 1 |

Plus 5 qualified reserve companies ranked below 100 (see file 4).

## Final audit

- ✅ Exactly 100 rows
- ✅ 100 unique companies (Apollo org id)
- ✅ 100 unique company domains/names
- ✅ 100 unique contacts (Apollo person id)
- ✅ 100 unique emails
- ✅ All emails Apollo-verified
- ✅ No guessed/pattern emails (all from Apollo enrichment)
- ✅ Zero existing Apollo contacts (id/email/LinkedIn/name+org)
- ✅ All companies HQ in GCC
- ✅ All contacts located in GCC
- ✅ Every row has a cement/concrete manufacturing category
- ✅ Score components sum to Lead Score
- ✅ Top-50 phone list has 50 rows, one per company
- ✅ Every top-50 row has a usable Apollo phone
- ✅ Every row has Apollo contact + company URL
- ✅ Rank order matches descending score

## Apollo credit usage

Cement project: 181 enrichment credits + 320 phone-reveal credits = ~510 lead credits. Balance after this project: **2,629 lead credits** (cycle resets 2026-10-23). Direct-dial credits remain at 0, so phone reveals draw from lead credits at 8 each.
