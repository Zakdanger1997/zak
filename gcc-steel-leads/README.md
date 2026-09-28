# GCC Steel Industry – Net-New Cold-Call Database (Apollo.io)

Built 2026-09-28 from the connected Apollo.io account. Every email is an Apollo `email_status = verified` work email. Every phone number is either an Apollo phone reveal (mobile/direct, `valid_number`, high confidence) or the company switchboard from the Apollo organization record. Nothing was guessed or added from outside Apollo.

## Files
| File | Content |
|---|---|
| `GCC_Steel_ColdCall_Database.xlsx` | All sections as sheets (1_Top50_ColdCall, 1b_Top50_Phone, 2_Database_200, 2b_Master_32_Fields, 3_Email_Only, 4_Data_Quality_Report, 5_Rejection_Reserve_Log, 6_Company_Master) |
| `section1_top50_coldcall_targets.csv` | Section 1 – Top 50 cold-call targets (one per company, all with a phone) |
| `section1b_top50_phone_contacts.csv` | Section 42 layout – Top 50 phone contacts |
| `section2_database_200_netnew_contacts.csv` | Section 2 / 41 – the 200 net-new contacts, ranked |
| `section2b_master_32_fields.csv` | Section 19 – the 32 required fields plus the six score components |
| `section3_email_only_export.csv` | Section 3 – Company / Contact / Title / Verified Apollo Email (200 rows, no duplicates) |
| `section4_data_quality_report.csv` | Section 4 / 43 – counts, country split, exclusions, dedup log |
| `rejection_and_reserve_log.csv` | Contacts enriched but rejected (wrong industry, unavailable email) and the 31 qualified contacts held in reserve over the 200 cap |
| `company_master_115.csv` | One row per company (115) with steel activity, products, size, HQ phone |

## Lead Priority Score (0–100)
Company Fit /30 (size band, mid-market 100–500 scores highest; service centres −3) + Industrial Scale /20 (headcount) + Steel Relevance /20 (mill/pipe 20, wire 18, foundry 16, fabrication 15, processing 14) + Decision-Maker Availability /15 (procurement/purchasing manager+ = 15, supply-chain/buyer = 12–13, maintenance/plant leadership = 12–13, engineering/ops/production management = 11, engineer-level = 8) + Verified Contact Data /10 (verified 10, verified on catch-all domain 8) + Phone /5 (Apollo mobile/direct 5, company line 3).
Tiers: A ≥ 84, B 72–83, C < 72.

## Net-new check
All 754 existing contacts in the Apollo account (347 in the GCC) were exported and compared by Apollo person ID, email, LinkedIn URL and first+last name+company / +domain. Zero matches: all 200 contacts are net-new. Existing contacts at Al Yamamah Steel Industries, Saudi Mechanical Industries and Tuwaiq Casting & Forging were avoided; the new people at those companies are different individuals.

## Notes / caveats
- 78 of the 200 emails sit on domains Apollo flags as catch-all, but Apollo still marks each address `verified`; flagged in Notes.
- 19 contacts are located outside the GCC per Apollo (e.g., a Saudi company's procurement director based in Egypt); company is in the GCC in every case; flagged in Notes.
- 7 emails are role-style mailboxes that Apollo has verified and assigned to the named person; flagged in Notes.
- 12 companies exceed 2,000 employees (e.g., Rajhi Steel, Al Ittefaq, AIC Steel, East Pipes). They are GCC-based producers with local purchasing/maintenance teams, so they were kept with a lower Company-Fit score; EMSTEEL (Emirates Steel Arkan) was excluded as too large.
- Direct-dial credits on the account are exhausted, so phone reveals were charged as 8 lead credits each. 50 attempted, 40 returned a number.
