# i.Mak Redüktör — GEO / AI-Search Visibility Report
### Goal: be the gearbox brand that ChatGPT, Gemini & Claude name and cite

**Prepared for:** the i.Mak website admin
**Website audited:** https://www.imakreduktor.com/
**Date:** 23 November 2026
**Method:** GEO-SEO audit (geo-seo-claude framework) + live technical crawl of the site + AI-crawler access test + brand-authority search

---

## 0. Read this first — honest expectations

There is **no "rank #1" on ChatGPT, Gemini or Claude** the way there is on Google. These models do not publish a ranked list of 10 blue links. What actually happens is:

- When a user asks *"who are good industrial gearbox manufacturers?"* or *"worm gearbox supplier in Turkey"* or *"IRK series helical bevel gearbox specs"*, the AI either **answers from memory** (what it learned about brands during training) or **does a live web search and cites sources** (ChatGPT Search, Gemini with Google, Perplexity, Claude with web search).

- **"Winning" = being the brand the model names, and being the page it cites** when it searches. That is what this report optimizes for.

So the realistic, achievable target is:

> When someone asks an AI about industrial gearboxes / reducers — especially worm, helical-bevel, planetary, extruder and crane gearboxes, or Turkish/European gearbox suppliers — **i.Mak is named as a recommended manufacturer and imakreduktor.com is cited as the source.**

This is 100% achievable for your product categories and regions. Beating global giants (Bonfiglioli, Flender, SEW-Eurodrive) on the generic query *"best gearbox"* is a long game; **winning the specific and regional queries is realistic within 3–6 months.** This report tells your admin exactly what to do.

---

## 1. Overall GEO Score: **53 / 100** — "Foundations OK, AI-layer missing"

| Category | Weight | Score | Verdict |
|---|---|---|---|
| AI Citability & Visibility | 25% | 55/100 | Crawlers allowed ✅ but no llms.txt, weak answer-blocks, no FAQ |
| Brand Authority Signals | 20% | 50/100 | Listed in good directories ✅ but no Wikipedia, inconsistent name, weak social |
| Content Quality & E-E-A-T | 20% | 50/100 | Broad catalog ✅ but fake demo content live ❌, no author/expert signals |
| Technical Foundations | 15% | 75/100 | Fast, SSR, HTTPS, mobile, hreflang — strongest area ✅ |
| Structured Data (Schema) | 10% | 40/100 | Only basic Yoast schema; no Product / FAQ / LocalBusiness |
| Platform Optimization | 10% | 40/100 | No comparison/spec content built for AI answers |

**Translation:** The house is well-built (fast, multilingual, crawlable), but it is not yet "speaking the language" that AI engines reward. The fixes below are mostly additive — new schema, new content blocks, one text file — not a rebuild.

---

## 2. What is already GOOD (do not break these)

1. **AI crawlers are NOT blocked.** I tested the live site with GPTBot, ChatGPT-User, ClaudeBot, PerplexityBot, Google-Extended, OAI-SearchBot and Meta's crawler — **all returned HTTP 200.** This is the #1 precondition and you pass it. (Cloudflare is in front of the site but is letting AI bots through.)
2. **robots.txt is open:** `User-agent: * / Disallow:` — nothing is blocked, and the sitemap is declared.
3. **Site is fast and server-rendered.** Homepage loads in ~0.96s, served by LiteSpeed cache + Cloudflare CDN, PHP 8.3, full HTML delivered server-side (AI crawlers can read it without running JavaScript). This matters a lot — many sites fail here.
4. **Proper multilingual setup.** EN / TR / ES / FR / RU with correct `hreflang` alternates and canonical tags.
5. **Broad, well-named product catalog** — worm (IRS), helical-worm (IRSD), helical-bevel (IRK), parallel-shaft (YP), planetary (IPR/IPRK), industrial/extruder (A-AE, MAE-MKE, MA-MK), shaft-mounted (IRNX/IRO), aerator (4DS), hoist/crane (IRC), aluminium worm (S), plus application-sector pages (cement, steel, mining, food, water, forestry, etc.).
6. **Already indexed in AI-trusted B2B directories:** DirectIndustry, GearTechnology, PowerTransmission.com, GlobalSpec, EMIS, SAHA Istanbul. These are exactly the sources AI models trust for industrial-equipment answers.
7. **Real, strong entity facts exist** (from those directories): founded **1973**, Istanbul (Pendik factory + Eyüp office), **exports to ~30 countries**, distribution in ~18, two manufacturing facilities, 50+ years in business. This is excellent authority raw material — it is just **not yet on your own site in a machine-readable way.**

---

## 3. CRITICAL ISSUES — fix in priority order

Each item: **what's wrong → why it hurts AI visibility → exact fix.**

### 🔴 PRIORITY 1 — Remove the fake demo "portfolio" content (TRUST KILLER)
**Problem:** Your portfolio/case-study section contains **9 fake theme-demo entries** that were never deleted after install:
```
/portfolio/new-york-airport-system-integration/
/portfolio/berlin-central-bank/
/portfolio/singapore-logistic-port/
/portfolio/hamburg-wind-energy-plant/
/portfolio/sanfran-cisco-bridge/
/portfolio/apples-server-room/         ← obviously fake ("Apple's server room")
/portfolio/mining-plant-set-up/
/portfolio/usa-bank-building/
/portfolio/muchen-railway-station/
```
**Why it hurts:** These are live and indexable. AI models assess **trust/E-E-A-T**. Fake "Apple's server room" and "San Francisco Bridge" case studies signal low-quality/placeholder content and can get the whole domain discounted as a reliable source. It also wastes crawl budget and dilutes your real entity.
**Fix:**
- **Delete all 9** demo portfolio items (and their TR/ES/FR/RU translations), OR
- **Replace them with real projects** — real customer installations, sectors, countries, gearbox series used, torque/application. Real case studies are *gold* for AI citation.
- After removal, submit updated sitemap in Google Search Console and Bing Webmaster Tools.

### 🔴 PRIORITY 2 — Homepage has NO H1 and NO meta description
**Problem:** The homepage (`/`) has **zero `<h1>` tags** (only 10 `<h3>`s) and **no meta description**. Title is the generic *"Homepage - I-MAK Redüktör"*.
**Why it hurts:** The H1 and title are the strongest "what is this page about" signals for both Google and AI. "Homepage" tells an AI nothing. No meta description = the model/SERP invents its own snippet.
**Fix:**
- Set homepage **title** to something keyword-rich and entity-clear, e.g.
  `I-MAK Redüktör — Industrial Gearbox & Geared Motor Manufacturer Since 1973 | Turkey`
- Add a **meta description** (~150 chars), e.g.
  `I-MAK manufactures industrial gearboxes & geared motors — worm, helical-bevel, planetary, shaft-mounted & extruder units. 50+ years, exporting to 30+ countries.`
- Add a single clear **H1** on the homepage, e.g.
  `Industrial Gearboxes & Geared Motors — Engineered by I-MAK Since 1973`
- (In WordPress/Yoast: set the SEO title + meta description per page; the H1 is controlled by the page builder/theme block — ask whoever built the theme to make the top hero heading an H1.)

### 🔴 PRIORITY 3 — Enrich the Organization schema (entity recognition)
**Problem:** Your current `Organization` JSON-LD only has name, url, logo, and two `sameAs` links (Facebook + X). It is missing the facts that make an AI *confident* about who i.Mak is.
**Why it hurts:** AI models build an internal "entity" for your company. The richer and more consistent the structured data (address, phone, founding date, what you make, where you operate, authoritative profile links), the more likely the model is to recognize, trust, and recommend you.
**Fix:** Replace the Organization node with the enriched version in **Section 6 (A)** below. Add founding date, address, phones, areaServed, knowsAbout, and **add your directory profiles** (DirectIndustry, GearTechnology, PowerTransmission, GlobalSpec, LinkedIn, YouTube) to `sameAs`.

### 🔴 PRIORITY 4 — No Product schema on product pages
**Problem:** Product pages (e.g. IRS worm geared motors) have an H1 ✅ but carry **only the generic WebPage schema** — no `Product` structured data, no technical specs in machine-readable form, no H2 subheadings (heading jumps H1 → H3).
**Why it hurts:** "Which worm gearbox has X ratio / Y torque?" type questions are answered from structured specs. Without Product schema and spec tables, AI can't extract or cite your products for spec-based queries.
**Fix:**
- Add `Product` JSON-LD to each product series page (template in **Section 6 (B)**).
- Add a real **specifications table** on each product page (ratios, torque range Nm, power kW, mounting, housing material, output options). Put it in an HTML `<table>` — AI parses tables very well.
- Fix heading hierarchy: H1 (series name) → H2 (Overview / Technical Specifications / Applications / Options) → H3 (sub-points).

### 🟠 PRIORITY 5 — No llms.txt file
**Problem:** `https://www.imakreduktor.com/llms.txt` does not exist (it soft-404s to the homepage).
**Why it hurts:** `llms.txt` is the emerging standard that hands AI crawlers a clean map of your most important pages. It's low-effort, high-signal.
**Fix:** Deploy the ready-made file in **Section 7** at the site root.

### 🟠 PRIORITY 6 — Contact page has no H1 and no LocalBusiness/ContactPoint schema
**Problem:** `/en-contacts/` has a meta description ✅ but **no H1**, and no `LocalBusiness` / `ContactPoint` structured data. Phone numbers (+90 216 378 06 86, +90 216 378 03 26, +90 212 567 87 32) and the address exist only as plain text.
**Why it hurts:** "How do I contact i.Mak / where is i.Mak located / i.Mak phone number" queries, and local/regional recommendations, rely on machine-readable NAP (Name-Address-Phone).
**Fix:** Add an H1 ("Contact I-MAK Redüktör") and add `ContactPoint` to the Organization schema and/or a `LocalBusiness` block with the verified address and phone(s). **Verify the exact factory + office addresses first.**

### 🟠 PRIORITY 7 — Inconsistent brand name = entity confusion
**Problem:** Across the web you appear as *I-MAK Reduktor*, *I-mak Redüktör*, *I-MAK Gearbox*, *i.Mak*, *I-mak Reduktor Varyator San. Tic. A.Ş.* The site's own `og:locale` is `en_US` even though the company is Turkish.
**Why it hurts:** AI entity resolution works best with one consistent canonical name + known aliases. Scattered spellings split your authority.
**Fix:** Pick **one canonical brand name** (recommend: **"I-MAK Redüktör"** with legal name *I-MAK Redüktör Varyatör San. ve Tic. A.Ş.*). Use it consistently in schema (`name` + `alternateName` for the variants + `legalName`). Standardize it in every directory profile too.

### 🟡 PRIORITY 8 — Thin answer-blocks & no FAQ content (citability)
**Problem:** Pages are ~900–1,100 words but not written as **self-contained, quotable answers**. There is no FAQ content anywhere.
**Why it hurts:** AI engines prefer to cite passages that are ~40–160 words, self-contained, fact-rich, and directly answer a question. Your content reads as marketing prose, not extractable answers.
**Fix:** See the **citability playbook (Section 8)** and add `FAQPage` schema (template in **Section 6 (C)**).

### 🟡 PRIORITY 9 — 13 images missing alt text + heading gaps
**Problem:** Homepage has 58 images, only 45 with `alt`. Several product pages skip H2.
**Fix:** Add descriptive, keyword-aware alt text to every product/diagram image (e.g. `alt="I-MAK IRS series worm geared motor cutaway showing gear ratio"`). Fix heading order site-wide.

### 🟡 PRIORITY 10 — Blog/news bulk-imported with weak dates & duplication
**Problem:** 333 blog URLs, many dated `2024-11-01` (bulk import) and duplicated across 5 languages. Content is thin news items.
**Fix:** Keep real news, but build **3–6 genuinely deep technical articles** (see Section 8) that are the kind AI loves to cite. Don't chase volume; chase depth + freshness (real, honest `datePublished`/`dateModified`).

---

## 4. The REAL lever: off-site brand authority (20% weight, outsized AI impact)

> Brand mentions correlate ~**3× more strongly** with AI visibility than backlinks do. AI models learn who to recommend largely from **how often and how authoritatively a brand is mentioned across the web** — not from your own site alone.

You already have a head start (directory listings). To become a brand AI *names*, the admin + marketing should, over 3–6 months:

1. **Wikipedia / Wikidata entity.** Create a **Wikidata item** for I-MAK Redüktör (founded 1973, Istanbul, industrial gearboxes, official site, identifiers linking GearTechnology/DirectIndustry). Wikidata is read directly by AI models and is the backbone of entity recognition. A Wikipedia article (TR first, then EN) is higher effort but very high value if notability can be shown (50-yr history, exports, press).
2. **Complete & standardize every directory profile:** DirectIndustry, GearTechnology, PowerTransmission, GlobalSpec, EMIS, IndustryStock, Europages, ThomasNet, Kompass. Same canonical name, same description, link back to the site, upload real catalogs. These are **high-trust AI sources**.
3. **LinkedIn company page** — active, complete, with product posts. (Add it to `sameAs`.)
4. **YouTube** — you already have gearbox videos; a complete channel with keyword-rich titles/descriptions is a strong, AI-read signal. (Add to `sameAs`.)
5. **Get mentioned in third-party technical content:** industry publications, engineering forums, distributor sites, trade-show coverage (Hannover Messe etc. — you already attend). Each independent mention with your canonical name strengthens the entity.
6. **Comparison & "best of" lists.** AI loves to cite listicles for "best X manufacturers." Earn placement in *"top gearbox manufacturers in Turkey / Europe / for cement / for cranes"* articles. Where they exist and are editable (e.g. some directories), ensure i.Mak is included and accurate.
7. **Consistent NAP everywhere** — identical company name, address, phone across all profiles.

**This is where #1 is actually won.** On-site fixes make you *citable*; off-site authority makes you *recommended*.

---

## 5. Who AI recommends today (the competitive gap)

When asked *"best industrial gearbox / reducer manufacturers,"* AI engines currently name: **Bonfiglioli, Flender, SEW-Eurodrive, STOBER, Neugart, Benzlers,** and a wave of Chinese makers — **not i.Mak.** 

**Your winning strategy is not to fight on the generic query first.** Win the specific/long-tail queries where intent is high and giants are vague:
- *"worm geared motor manufacturer Turkey"*
- *"helical bevel geared motor IRK series"*
- *"monoblock extruder gearbox supplier"*
- *"shaft-mounted gearbox for mining / cement"*
- *"aerator drive gearbox for water treatment"*
- *"gearbox manufacturer exporting to [region] with local distribution"*

For each, you have a product + sector page. Make those pages the best, most structured, most quotable answer on the web, and AI will cite you. Then the generic recommendation follows naturally as authority compounds.

---

## 6. Ready-to-paste schema (JSON-LD)

> Install via Yoast (it generates base schema — your dev can extend it) or inject these as `<script type="application/ld+json">` blocks in the page `<head>`. **Verify every address/phone/date before publishing.**

### (A) Enriched Organization schema — site-wide (replace current)
```json
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://www.imakreduktor.com/#organization",
  "name": "I-MAK Redüktör",
  "legalName": "I-MAK Redüktör Varyatör San. ve Tic. A.Ş.",
  "alternateName": ["I-MAK Reduktor", "I-MAK Gearbox", "iMAK"],
  "url": "https://www.imakreduktor.com/",
  "logo": "https://www.imakreduktor.com/wp-content/uploads/2024/10/logo.png",
  "foundingDate": "1973",
  "description": "I-MAK is a Turkish manufacturer of industrial gearboxes and geared motors, including worm, helical, helical-bevel, planetary, shaft-mounted, extruder and hoist/crane units, exporting to more than 30 countries since 1973.",
  "slogan": "Power transmission engineered since 1973",
  "knowsAbout": [
    "Industrial gearboxes", "Geared motors", "Worm gearboxes",
    "Helical bevel geared motors", "Planetary gearboxes",
    "Shaft-mounted gearboxes", "Extruder gear units",
    "Hoist and crane gearboxes", "Mechanical power transmission", "Speed reducers"
  ],
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "VERIFY — factory address",
    "addressLocality": "Pendik",
    "addressRegion": "İstanbul",
    "postalCode": "VERIFY",
    "addressCountry": "TR"
  },
  "contactPoint": [{
    "@type": "ContactPoint",
    "telephone": "+90-216-378-06-86",
    "contactType": "sales",
    "areaServed": "Worldwide",
    "availableLanguage": ["Turkish","English","Spanish","French","Russian"]
  }],
  "areaServed": ["TR","EU","MENA","Asia","Worldwide"],
  "numberOfEmployees": { "@type": "QuantitativeValue", "value": "VERIFY" },
  "sameAs": [
    "https://www.facebook.com/imakreduktor",
    "https://x.com/imakreduktor",
    "https://www.linkedin.com/company/VERIFY",
    "https://www.youtube.com/VERIFY",
    "https://www.directindustry.com/soc/i-mak-reducteurs-159888.html",
    "https://www.geartechnology.com/companies/i-mak-reduktor",
    "https://www.powertransmission.com/companies/i-mak-reduktor",
    "https://www.emis.cn/php/company-profile/TR/I-mak_Reduktor_Varyator_AS_en_3331956.html"
  ]
}
</script>
```

### (B) Product schema — per product-series page
```json
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "I-MAK IRS Series Worm Geared Motors",
  "brand": { "@type": "Brand", "name": "I-MAK Redüktör" },
  "manufacturer": { "@id": "https://www.imakreduktor.com/#organization" },
  "category": "Worm geared motors / speed reducers",
  "description": "IRS series worm geared motors for industrial power transmission. VERIFY: ratio range, torque range (Nm), power range (kW), mounting options.",
  "image": "https://www.imakreduktor.com/VERIFY-product-image.jpg",
  "url": "https://www.imakreduktor.com/irs-series-worm-geared-motors-types/",
  "additionalProperty": [
    { "@type": "PropertyValue", "name": "Gear type", "value": "Worm" },
    { "@type": "PropertyValue", "name": "Reduction ratio range", "value": "VERIFY e.g. 7.5:1 – 100:1" },
    { "@type": "PropertyValue", "name": "Output torque range", "value": "VERIFY e.g. up to 2000 Nm" },
    { "@type": "PropertyValue", "name": "Power range", "value": "VERIFY e.g. 0.12 – 15 kW" },
    { "@type": "PropertyValue", "name": "Housing", "value": "VERIFY (cast iron / aluminium)" }
  ]
}
</script>
```

### (C) FAQPage schema — add to product & sector pages (strong AI-citation magnet)
```json
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is an IRS series worm geared motor used for?",
      "acceptedAnswer": { "@type": "Answer",
        "text": "VERIFY — 2–4 sentence factual answer: typical applications, torque range, why worm gearing suits them." }
    },
    {
      "@type": "Question",
      "name": "What reduction ratios does the I-MAK IRS series offer?",
      "acceptedAnswer": { "@type": "Answer", "text": "VERIFY — state the exact ratio range and gradations." }
    }
  ]
}
</script>
```

---

## 7. Ready-to-deploy llms.txt

Save as `https://www.imakreduktor.com/llms.txt` (plain text, UTF-8, at site root). Fill the VERIFY bits:

```
# I-MAK Redüktör

> Turkish manufacturer of industrial gearboxes and geared motors since 1973.
> Product range: worm, helical, helical-bevel, planetary, parallel-shaft,
> shaft-mounted, extruder and hoist/crane gear units. Exporting to 30+ countries.

## Company
- [About I-MAK](https://www.imakreduktor.com/about-us/): history, facilities, export reach
- [Contact](https://www.imakreduktor.com/en-contacts/): offices, phones, request form
- [Certificates](https://www.imakreduktor.com/certificates/): quality certifications
- [Catalogs](https://www.imakreduktor.com/catalogs/): downloadable product catalogs

## Products
- [All gearbox types](https://www.imakreduktor.com/products/)
- [IRS worm geared motors](https://www.imakreduktor.com/irs-series-worm-geared-motors-types/)
- [IRSD helical-worm geared motors](https://www.imakreduktor.com/irsd-series-helical-worm-geared-motors-units/)
- [IRK helical-bevel geared motors](https://www.imakreduktor.com/irk-series-helical-bevel-geared-motor-types/)
- [YP parallel-shaft geared motors](https://www.imakreduktor.com/yp-series-parallel-shaft-helical-geared-motor-types/)
- [IPR/IPRK planetary gearboxes](https://www.imakreduktor.com/ipr-iprk-series-planetary-gearboxes/)
- [A-AE industrial gear units](https://www.imakreduktor.com/a-ae-series-industrial-gear-unit/)
- [MAE-MKE monoblock extruder gear units](https://www.imakreduktor.com/mae-mke-series-monoblock-extruder-gear-units/)
- [IRNX shaft-mounted gearboxes](https://www.imakreduktor.com/irnx-series-shaft-mounted-gearboxes/)
- [IRC hoist/crane geared motors](https://www.imakreduktor.com/irc-series-hoist-drive-geared-motor-types/)
- [4DS aerator-type gearboxes](https://www.imakreduktor.com/4ds-series-aerator-type-gearboxes-types/)

## Applications
- [Cement](https://www.imakreduktor.com/cement/)
- [Steel](https://www.imakreduktor.com/steel/)
- [Mining & quarrying](https://www.imakreduktor.com/mine/)
- [Water & waste treatment](https://www.imakreduktor.com/water-purification/)
- [Food & beverage](https://www.imakreduktor.com/food-beverage/)
- [Agriculture & forestry](https://www.imakreduktor.com/agriculture-forestry/)

## Resources
- [User manual](https://www.imakreduktor.com/user-manual/)
- [Mounting positions](https://www.imakreduktor.com/mounting-positions/)
- [Oil quantities & lubrication](https://www.imakreduktor.com/oil-board/)
- [Spare parts](https://www.imakreduktor.com/spare-parts-list/)
```

---

## 8. Content & citability playbook (how to get quoted by AI)

AI engines prefer passages that are **self-contained, factual, and directly answer a question** (ideal ~40–160 words). Rewrite key pages so each opens with an **answer-first block**, then details.

**Do this on every product page:**
1. **First paragraph = the direct answer.** Start with: *"The I-MAK IRS series is a range of worm geared motors with reduction ratios of X–Y and output torque up to Z Nm, used in [applications]."* (No marketing warm-up first.)
2. **Add a specifications table** (ratios, torque, power, mounting, housing, output type). Tables are extremely AI-friendly.
3. **Add an H2 "Frequently Asked Questions"** with 4–6 real Q&As (+ FAQPage schema).
4. **Add "Where it's used"** linking to the matching sector pages.
5. **Keep a visible "Last updated: [date]"** and update it when specs change — freshness is an AI trust signal.

**Build 4–6 deep technical articles** (the kind AI cites for how-to/comparison queries), e.g.:
- *"Worm vs. helical vs. planetary gearboxes: how to choose"* (you make all three — authoritative)
- *"How to size a gearbox: service factor, torque and ratio explained"*
- *"Gearbox mounting positions and lubrication quantities — a practical guide"* (you already have the data pages)
- *"Which gearbox for cement / mining / water-treatment duty"* (ties products to sectors)
- *"Gearbox maintenance and oil-change intervals"*

Each: answer-first, data tables, author byline with real engineering credentials (E-E-A-T), internal links to products, honest dates.

**Add author/expertise signals (E-E-A-T):** give technical articles a named author with a short bio and credentials (e.g. "Mechanical engineer, 15 yrs in power transmission"). AI weights content from identifiable experts higher.

---

## 9. Action plan for the admin

### Week 1 — Quick wins (high impact, low effort)
- [ ] **Delete the 9 fake demo portfolio items** (all languages). *(P1)*
- [ ] Add homepage **title, meta description, and one H1**. *(P2)*
- [ ] Deploy **llms.txt** at site root (Section 7). *(P5)*
- [ ] Add **H1 to the contact page**; fix missing image alt text. *(P6, P9)*
- [ ] Decide the **one canonical brand name** and legal name. *(P7)*

### Weeks 2–4 — Structured data & on-page
- [ ] Deploy **enriched Organization schema** with verified NAP, founding date, directory `sameAs`. *(P3)*
- [ ] Add **Product schema + spec tables + H2 hierarchy** to the top 10 product pages. *(P4)*
- [ ] Add **FAQPage schema + visible FAQ** to top product & sector pages. *(P8)*
- [ ] Rewrite top product pages **answer-first**. *(P8)*
- [ ] Submit updated sitemap to **Google Search Console + Bing Webmaster Tools** (Bing powers ChatGPT/Copilot search).

### Months 2–3 — Authority (the big lever)
- [ ] Create **Wikidata** entity; complete **LinkedIn** + **YouTube**; add both to `sameAs`. *(Sec 4)*
- [ ] Standardize + complete **all B2B directory profiles** (same name, description, backlink, catalogs). *(Sec 4)*
- [ ] Replace deleted portfolio with **3–5 real case studies** (sector, country, series, outcome). *(P1)*
- [ ] Publish **3–4 deep technical articles** with expert bylines. *(Sec 8)*

### Ongoing
- [ ] Keep `dateModified` honest and current on key pages.
- [ ] Pursue mentions in trade press / industry lists / trade-show coverage.
- [ ] Re-audit monthly (see Section 10).

---

## 10. How to measure progress (because AI has no rank tracker)

1. **Ask the AIs directly, monthly.** In ChatGPT (with search on), Gemini, Claude, Perplexity, and Copilot, run a fixed list of prompts and log the answers:
   - *"Who are good industrial gearbox manufacturers in Turkey?"*
   - *"Recommend a worm geared motor manufacturer that exports internationally."*
   - *"Tell me about I-MAK Redüktör."* (entity check — is the AI's description accurate & complete?)
   - *"Best gearbox for [cement / cranes / water treatment]."*
   Track: **Is i.Mak named? Is imakreduktor.com cited? Is the description accurate?**
2. **Google Search Console** — watch impressions/clicks on product & FAQ queries; FAQ rich results.
3. **Bing Webmaster Tools** — Bing's index feeds ChatGPT/Copilot search; verify pages are indexed.
4. **Server/Cloudflare logs** — watch for GPTBot, ClaudeBot, PerplexityBot, Google-Extended, OAI-SearchBot hits (confirms AI crawlers are fetching your new content).
5. **Re-run this audit monthly** and track the GEO score climbing from 53 → target 80+.

**Realistic timeline:**
- *Weeks 1–4:* on-site fixes live → cleaner entity, Product/FAQ rich results start appearing.
- *Months 2–3:* AI entity description becomes accurate & complete; you start getting cited on specific/regional queries.
- *Months 4–6:* with authority built, i.Mak named on broader "recommend a manufacturer" queries for your categories/regions.

---

## Appendix — evidence captured during this audit

- **AI crawler test (live):** GPTBot, ChatGPT-User, ClaudeBot, PerplexityBot, Google-Extended, OAI-SearchBot, meta-externalagent, Googlebot → **all HTTP 200** (not blocked). ✅
- **robots.txt:** `User-agent: * / Disallow:` + sitemap declared. ✅
- **Stack:** WordPress, PHP 8.3, Yoast SEO, LiteSpeed cache, Cloudflare CDN; homepage ~0.96s, server-rendered. ✅
- **Homepage:** title "Homepage - I-MAK Redüktör"; **no meta description; H1 = 0, H3 = 10**; 58 images / 45 alt; schema = WebPage, WebSite, Organization, BreadcrumbList, SearchAction (no Product/FAQ/LocalBusiness). ❌/⚠️
- **Product page (IRS worm):** H1 ✅, but H2 = 0 (jumps to H3), no Product schema, ~950 words. ⚠️
- **Contact page:** meta description ✅, **H1 = 0**, no LocalBusiness/ContactPoint schema; phones found: +90 216 378 06 86, +90 216 378 03 26, +90 216 378 26 36, +90 212 567 87 32; address in Istanbul/Pendik (plain text only). ⚠️
- **Portfolio:** **9 fake theme-demo case studies live.** ❌
- **Content inventory:** ~160 page URLs (EN/TR/ES/FR/RU), full product-series + sector coverage; 333 blog URLs (many bulk-dated 2024-11-01, multilingual duplicates). 
- **Off-site presence:** DirectIndustry, GearTechnology, PowerTransmission, GlobalSpec, EMIS, SAHA Istanbul. **No Wikipedia/Wikidata found.** Entity facts available off-site but missing from on-site schema: founded 1973, Istanbul (Pendik factory/Eyüp office), exports to ~30 countries, distribution in ~18, two facilities.

---

*Report generated with the geo-seo-claude framework. All on-site findings are from a live crawl of imakreduktor.com on 23 Nov 2026. Verify all addresses, phone numbers, dates, and product specs with the company before publishing schema.*
