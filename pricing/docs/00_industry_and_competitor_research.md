# I-MAK Pricing & Cross-Reference System — Industry & Competitor Research

> **Purpose of this document.** Foundation knowledge for the system we are building: a tool to (1) **price I-MAK standard units** and (2) **select the equivalent I-MAK unit** for any competitor gearbox a customer already uses. This file captures the gearbox industry, I-MAK's own portfolio, the global + local competitors, the technical detail of every gear-unit type, the special/engineered types, and the full option/accessory matrix that drives price.
>
> Everything here is compiled from public web sources + industry domain knowledge. **Exact torque/ratio/price numbers come from the catalogues and price lists you will upload** — this document is the scaffold those numbers hang on.
>
> _Last updated: 2026-07-09_

---

## 1. How the gearbox (gear reducer) industry works

A **gearbox / gear reducer / geared motor** reduces the speed of an electric motor and multiplies its torque. It is defined by a small number of parameters that also happen to be the **price drivers**:

| Parameter | Meaning | Why it matters for price |
|---|---|---|
| **Type / geometry** | helical inline, helical-bevel, parallel-shaft, worm, planetary, etc. | Sets the base casting/tooling family |
| **Size / frame** | physical case size (e.g. 63, 75, 90…) | Bigger = more material + machining |
| **Ratio (i)** | input rpm ÷ output rpm | Number of gear stages, gear cutting |
| **Nominal output torque (M₂, Nm)** | the real deliverable | The single most important sizing number |
| **Service factor (fB / SF)** | de-rating for shock/duty | Customer application-driven |
| **Input** | motor-mounted (geared motor) vs IEC/NEMA adapter vs solid shaft | Motor cost dominates on geared motors |
| **Options** | brake, backstop, cooling, seals, coating, ATEX… | Each is a price adder (see §7) |

**Two ways units are sold:**
- **Geared motor** — gearbox + electric motor as one unit (the bulk of the market, catalogue business).
- **Gear unit only** — bare shaft input or with IEC/NEMA motor adapter ("PAM"), for OEMs who fit their own motor.

**Market structure (2025-26).** The global industrial gearbox market is led by a handful of full-range groups; the top 5 together hold only ~15-20% share — it is a **fragmented market**, which is exactly why cross-reference / equivalent-selection has commercial value.

**Sources:** [Mordor Intelligence](https://www.mordorintelligence.com/industry-reports/industrial-gearbox-market), [GM Insights](https://www.gminsights.com/industry-analysis/industrial-gearbox-market), [Grand View Research](https://www.grandviewresearch.com/industry-analysis/industrial-gearbox-market-report), [Automation.com supplier landscape](https://www.automation.com/en-us/articles/june-2021/geared-motors-industrial-gears-two-trends)

---

## 2. Our company — I-MAK (İMAK Redüktör)

- **Founded:** ~1972 (50+ year history). HQ + factory in **Istanbul, Turkey** (Seyhli Sanayi Cad., 34204).
- **Scale:** ~16,000 m² production; markets itself as **1,000,000+ product references**; **exports to 40-54 countries**.
- **Positioning:** full-range modular geared-motor and industrial gear-unit maker — a **value alternative to the German/Italian premium brands** (NORD, SEW, Bonfiglioli, Flender) with directly interchangeable geometry.

### 2.1 I-MAK product portfolio (series → type)

| I-MAK series | Type | Notes |
|---|---|---|
| **IR** | Helical **inline** geared motor | Coaxial; foot/flange mount |
| **IRK** | Helical-**bevel** geared motor | Right-angle, high efficiency |
| **YP** | **Parallel-shaft** helical geared motor | Flat/shaft-mount, compact axial length |
| **IRS** | **Worm** geared motor | Compact right-angle |
| **IRSD** | **Helical-worm** geared motor | Helical pre-stage + worm (higher ratio/efficiency than plain worm) |
| **S** | **Aluminium-housing worm** geared motor | NMRV-standard geometry (see §5.3) — the interchangeable format |
| **IRC** | **Hoist / crane-drive** geared motor | Heavy-duty lifting |
| **A / AE** | **Industrial gear units** | Large helical / bevel-helical, foot or flange |
| **MA / MK** | **Monoblock** industrial gear units | One-piece housing, heavy duty |
| **MAE / MKE** | **Monobloc extruder** gear units | Thrust-bearing block for extruder screws |
| **IRN / IRNX** | **Shaft-mounted** gear units | Screw conveyor / mineral duty, torque arm |
| **IRO** | **Shaft-mounted** gear units | Alternative mounting |
| **4DS** | **Aerator** gearboxes | Water treatment / surface aerators |
| **AD / ADS / IRAEM** | **Special / engineered** units | Custom applications |
| **ADK** | **Special** gear units | Engineered |
| **IPR / IPRK** | **Planetary** gear units | IPR inline, IPRK right-angle (with bevel) |
| **ITR** | **Poultry** reducers | Niche agricultural |

**Sources:** [I-MAK homepage](https://www.imakreduktor.com/), [About](https://www.imakreduktor.com/about-us/), [Gear Technology profile](https://www.geartechnology.com/companies/i-mak-reduktor), [Defensehere profile](https://defensehere.com/en/i-mak-reduktor/)

---

## 3. Competitor landscape

### 3.1 Global / premium tier (the ones customers most often already own)

| Company | Country | Flagship / notes | Relevance to us |
|---|---|---|---|
| **SEW-Eurodrive** | 🇩🇪 Germany | Modular king; R/F/K/S/W/P/X families, DR motors. Benchmark for modularity | #1 cross-ref target |
| **Flender** (Siemens) | 🇩🇪 Germany | Global leader in *large* industrial + wind; MOTOX geared motors, SIG/SIP industrial | Big-gear benchmark |
| **NORD Drivesystems** | 🇩🇪 Germany | SK helical, NORDBLOC, MAXXDRIVE industrial, nsd tupH surface, decentralized drives | Strong distributor network (we scraped their locator) |
| **Bonfiglioli** | 🇮🇹 Italy | C/A/F/W/VF families, 300-series + planetary (TR, 700T, EVOX), mobile/wind | #2 cross-ref target |
| **Sumitomo Drive Tech.** | 🇯🇵 Japan | **Cyclo** drive (2-3× torque density), Paramax industrial; owns **Hansen** | Cyclo is a unique niche |
| **Rossi** (Habasit) | 🇮🇹 Italy | R/E helical, G industrial, EP planetary | Mid-premium |
| **Bauer Gear Motor** (Altra/Regal Rexnord) | 🇩🇪 Germany | BG/BK geared motors, IE4 PM motors | Efficiency-led |
| **Regal Rexnord** (Dodge/Falk) | 🇺🇸 USA | TXT shaft-mount, Falk industrial, Quadrant | US shaft-mount benchmark |
| **Nabtesco / Nidec / Wittenstein** | 🇯🇵/🇩🇪 | Precision cycloidal & servo planetary (robotics) | Precision niche only |
| **Brevini / Dana** | 🇮🇹 | Heavy planetary (mobile, mixer, winch) | Planetary/heavy |
| **Motovario** (TECO) | 🇮🇹 Italy | **NMRV** worm (the de-facto standard), H/B/P families | Sets the worm standard |
| **Radicon / Elecon** | 🇬🇧/🇮🇳 | Shaft-mount, industrial | Commonwealth markets |

### 3.2 Local / regional tier — Turkey & surrounding (our home turf)

| Company | Notes | Relevance |
|---|---|---|
| **Yılmaz Redüktör** | Turkey's **largest** gearbox maker (est. 1958), ~330,000 units/yr, claims top-6 worldwide, 11 series. Owns **Elk Motor** (motors) + **MES** (casting) | **Our #1 direct local rival** |
| **Elk Motor** | Yılmaz subsidiary — electric motors | Motor supply/benchmark |
| **Sitti / SITI (via distributors)**, **Varvel**, **STM**, **Transtecno** | Italian value worm/helical brands sold regionally | Overlap on price-competitive worm/helical |
| **Chinese NMRV makers** (Made-in-China "Motovario-like") | Very low-cost worm boxes | Bottom-price pressure |
| **Egypt / Gulf / Iran assemblers** | Regional assembly of Italian/Chinese kits | Regional price floor |

**Sources:** [Yılmaz Redüktör](https://www.yreduktor.eu/index.php/en/yilmaz-reduktor-en/about-yilmaz-reduktor/), [Yılmaz UK](https://www.yilmazuk.co.uk/about-us), [Elk Motor](https://elkmotor.com.tr/en/our-companies), [SEW-Eurodrive](https://www.sew-eurodrive.com/), [top-10 gearbox makers](https://www.sogears.com/blog/top-10-gearbox-manufacturers-in-world)

---

## 4. THE CROSS-REFERENCE MAP (core of the "equivalent company" engine)

This is the heart of the selection tool: given a competitor model, find the equivalent I-MAK unit. Product-family naming is remarkably consistent by **type** across the industry, which makes the mapping tractable.

| Gear-unit **type** | **I-MAK** | SEW | NORD | Bonfiglioli | Flender MOTOX | Motovario | Yılmaz |
|---|---|---|---|---|---|---|---|
| Helical **inline** | IR | **R** | SK (…) / NORDBLOC | **C** (A) | **E** | H | K/MR |
| Helical-**bevel** (right angle) | IRK | **K** | bevel SK | **A** | **B** | B | — |
| **Parallel-shaft** / flat | YP | **F** | SK …flat | **F** | **F/D** | P | — |
| **Worm** (universal) | IRS / **S** | **W** | SI / SMI | **W / VF** | — | **NMRV** | — |
| **Helical-worm** | IRSD | **S** | (worm) | VF-combined | — | S | — |
| **Planetary** | IPR / IPRK | **P / PS** | (planetary) | **300 / TR / 700T** | **P** | — | — |
| **Industrial** (heavy) | A/AE, MA/MK | **X / M** | **MAXXDRIVE** | **HDO / HDP / 300** | **SIG / H / B** | — | industrial |
| **Shaft-mount** (conveyor) | IRN/IRNX, IRO | F/M | (shaft-mount) | — | — | — | — |
| **Extruder** | MAE/MKE | — | — | HDO-extruder | — | — | — |

**Matching rules the tool must apply (not just the family letter):**
1. **Torque first** — match nominal output torque M₂ (Nm) within the same duty/service factor, *then* look at case size.
2. **Ratio band** — find the I-MAK ratio nearest the competitor's *i*, then check the resulting output rpm.
3. **Mounting & output** — foot/flange/face; solid vs hollow shaft; shaft Ø and centre height must physically fit (critical for worm NMRV, see §5.3).
4. **Motor interface** — IEC frame (B5/B14) or integral motor; kW + poles + IE class.
5. **Service factor** — a competitor unit at SF 1.4 must map to an I-MAK unit at ≥ the same SF for the application, not just equal torque.

**Interchange references exist publicly** (e.g. NORD interchange guide, Falk/Ultramite interchange, NMRV cross-refs) and confirm this letter-family logic — we will encode our own table from your in-house comparison lists.

**Sources:** [NORD interchange guide](https://www.yumpu.com/en/document/view/9556707/nord-interchange-guide), [Falk interchange](https://www.rexnord.com/contentitems/techlibrary/documents/950-501_interchangeguide), [NMRV interchange](http://www.tvtamerica.com/bfk-sfk%20wormgears.htm), [Motovario NMRV catalogue](https://my.motovario.com/uploads/pdf_static/TECHNICAL%20CATALOGUE_VSF_IEC_STD_EN_rev0_2017.pdf)

---

## 5. Gear-unit TYPES — technical detail

### 5.1 Helical inline (coaxial) — I-MAK **IR**
- **Geometry:** input and output shafts on the same axis. 2-3 helical stages.
- **Efficiency:** very high, **~96-98% per stage** (~94-96% overall).
- **Ratio:** ~1.3 : 1 up to ~290 : 1 (single family); more with extra stage.
- **Torque:** roughly **up to ~20,000 Nm** in geared-motor sizes.
- **Use:** conveyors, pumps, general machinery. The default when layout allows a straight line.

### 5.2 Helical-bevel (right-angle) — I-MAK **IRK**
- **Geometry:** spiral-bevel gear turns the drive 90°. High efficiency (**~94-97%**), unlike worm.
- **Ratio:** ~5 : 1 to ~200 : 1; torque **up to ~50,000 Nm**.
- **Use:** the premium right-angle choice — conveyors, agitators, travel drives. Directly replaces worm where efficiency matters.

### 5.3 Worm & helical-worm — I-MAK **IRS / IRSD / S**
- **Geometry:** worm screw drives a bronze worm wheel, 90° offset.
- **Efficiency:** **lower — ~45-90%** depending on ratio (high ratios lose more to friction → heat). Self-locking possible at high ratio (useful for hoists, dangerous to assume).
- **Cost:** cheapest right-angle; quiet; good shock absorption.
- **NMRV standard (critical):** aluminium worm boxes follow the **NMRV** dimensional standard — **centre distances 025, 030, 040, 050, 063, 075, 090, 110, 130, 150 mm**, output bore 11-45 mm. **These are physically interchangeable across Motovario, Bonfiglioli VF, Varvel, SITI, Transtecno, Chinese clones and I-MAK's S series** — same mounting holes, shaft heights and ratios. This is the *easiest, highest-confidence* cross-reference in the whole catalogue.
- **Helical-worm (IRSD / SEW S):** adds a helical input stage → higher efficiency and ratio than plain worm.

### 5.4 Parallel-shaft / shaft-mount — I-MAK **YP / IRN / IRNX / IRO**
- **Geometry:** offset parallel shafts; often **hollow output shaft** slid straight onto a driven shaft with a **torque arm** reacting the load (no coupling/baseplate needed).
- **Use:** belt conveyors, screw conveyors, mixers, mineral processing. Space-saving.
- **Options that matter:** shrink disk vs keyed hollow bore, taconite seals for dust, backstop for inclined conveyors.

### 5.5 Planetary — I-MAK **IPR / IPRK**
- **Geometry:** sun + planet gears + ring gear; load shared over multiple planets → **very high torque density** in a compact coaxial package.
- **Ratio:** ~3 : 1 to ~10,000 : 1 (multi-stage); torque into the **millions of Nm** for heavy series.
- **Use:** high-torque low-speed — mixers, winches, drilling, mobile machinery, slew drives. IPRK adds a bevel input for right-angle.
- **Efficiency:** ~97% per stage.

### 5.6 Industrial / heavy gear units — I-MAK **A/AE, MA/MK**
- **Geometry:** large cast or fabricated housing, helical or bevel-helical, foot or flange, solid or hollow shaft. Splash/forced lube, cooling, big anti-friction bearings.
- **Use:** cement, mining, steel, cooling towers, extruders, marine. This is where **Flender / SEW X / NORD MAXXDRIVE / Sumitomo Paramax** compete.
- **Monoblock (MA/MK):** one-piece housing for stiffness under heavy/shock loads.

---

## 6. Special / engineered types (each often quoted individually)

| I-MAK | Application | What's special |
|---|---|---|
| **IRC / IR hoist** | Crane & hoist drives | Duty cycles (FEM/ISO), brake, high radial load, often double-shaft for two drums |
| **MAE / MKE** | **Extruder** drives | Integrated **axial thrust bearing block** to take screw thrust; plastics/rubber/food |
| **4DS** | **Aerator / water treatment** | Vertical output, thrust load, weatherproof, corrosion protection |
| **Cooling-tower drives** | HVAC/process | Long slender output, wet corrosive environment, low noise |
| **Agitator / mixer drives** | Chemical/food | Vertical, dry-well seals, large overhung + thrust loads |
| **ITR** | **Poultry** feed/ventilation | Light-duty agricultural niche |
| **AD / ADS / ADK / IRAEM** | Custom / engineered | Made-to-order — priced as engineered specials, not catalogue |

> **Pricing note:** specials are usually **quotation items**, not fixed-price catalogue lines. The system should flag these for engineering review rather than auto-price.

---

## 7. OPTIONS & ACCESSORIES matrix (the price adders)

Every option below is a configurable line item that changes price. This is the option model the pricing engine needs.

### 7.1 Motor (for geared motors)
- **Power (kW)** and **poles / speed** (2p ≈ 3000, 4p ≈ 1500, 6p ≈ 1000, 8p ≈ 750 rpm).
- **Efficiency class** — **IE1, IE2, IE3 (Premium, current legal minimum in EU/US/CN/IN), IE4 (Super-Premium)** per IEC 60034-30-1. IE4 asynchronous/PM reaches ~96.8%. Higher IE = higher price, lower running cost — a **key selling argument vs cheaper rivals**.
- **Voltage / frequency / phase**, **duty type (S1-S10)**, **insulation class (F/H)**, **IP rating (IP55/IP65/IP66)**.
- **Motor brand** — I-MAK/Elk vs premium — a cost lever.

### 7.2 Braking & holding
- **Electromagnetic brake** (AC or DC), rated **brake torque (Nm)**, **hand release**, **microswitch**, **fast-acting rectifier**.
- **Backstop / anti-runback** (one-way clutch) for inclined conveyors, bucket elevators.

### 7.3 Cooling & thermal
- **Forced-cooling fan** (separately driven) for high ambient / low speed.
- **Cooling coil (water)** or **oil-cooling unit** on industrial gears.
- **Thermistors PTC / PT100 / thermostats**, **anti-condensation heater**.

### 7.4 Feedback & control
- **Encoder** (incremental / absolute), **tacho**, **proximity/speed sensor**.
- **Integrated inverter / decentralized drive** (NORD's differentiator — note for competitive positioning).

### 7.5 Output & mounting
- **Output shaft:** solid keyed, **hollow bore (keyed / shrink-disk / splined)**, single or **double extension**.
- **Mounting:** foot (B3), flange (B5/B14), face, **torque arm** + rubber buffer for shaft-mount.
- **Mounting position M1-M6** — affects **oil quantity, breather and seal layout** (must be specified; wrong position = failure).

### 7.6 Sealing & environment
- **Seals:** standard nitrile, **FKM/Viton** (high temp/chemical), **double-lip**, **taconite** (dusty/mining), **drywell** (agitators).
- **ATEX / explosion-proof:** Ex zones **1, 2, 21, 22**, categories II 2G/2D — for gas/dust hazardous areas.
- **Ambient:** tropicalization, **low-temp to −40 °C**, high-ambient.

### 7.7 Surface, hygiene & lubrication
- **Coating / corrosion class C1-C5** (ISO 12944); special paint systems; offshore.
- **Washdown / smooth-surface hygienic** finish (equiv. NORD *nsd tupH* / stainless) for food & beverage, pharma.
- **Lubricant:** mineral, **synthetic PAO/PAG**, **food-grade H1**, low-temp; oil sight glass, drain, breather config.
- **Reinforced / oversized bearings** for high overhung/axial loads.

---

## 8. What the pricing system needs (data model preview)

Boiling §1-7 down, a unit price = **base(type, size, ratio)** + **motor(kW, poles, IE, brand)** + **Σ options** + **surface/finish** − **volume discount**, with a **competitor-equivalent** field for benchmarking.

Minimum reference tables the system will hold:
1. **I-MAK catalogue** — every series × size × ratio × nominal torque × base price.
2. **Motor price table** — kW × poles × IE class × brand.
3. **Options price table** — each adder from §7 with rule (flat / % / per-size).
4. **Cross-reference table** — competitor model → I-MAK equivalent (from §4 logic + your in-house lists).
5. **Discount / margin rules** — by customer, volume, region.

---

## 9. WHAT I NEED FROM YOU (to move from research → building)

Please upload / share:

1. **I-MAK catalogues** (per series) — with **sizes, ratios, nominal torque (Nm), power (kW)** tables. PDF or Excel.
2. **I-MAK price list(s)** — base prices per unit; motor price list; and the **options/adder price list** if separate.
3. **Your in-house competitor comparison lists** — the cross-reference sheets your team already made (I-MAK ↔ SEW / NORD / Bonfiglioli / Yılmaz…).
4. **Competitor catalogues / price lists** you have (even partial) — helps calibrate positioning.
5. A few **real quote examples** (unit + options + final price) — so the engine's output matches how your team actually quotes.
6. Confirm the **currency, discount structure, and margin rules** you price in.
7. Confirm **scope**: geared motors only, or industrial/engineered specials too? And which **competitors are priority** for cross-reference.

Once I have #1-#3 I can start building the actual pricing + equivalent-selection engine.

---

## Appendix — source list
- I-MAK: [homepage](https://www.imakreduktor.com/) · [about](https://www.imakreduktor.com/about-us/) · [Gear Technology](https://www.geartechnology.com/companies/i-mak-reduktor) · [Defensehere](https://defensehere.com/en/i-mak-reduktor/)
- Yılmaz: [corporate](https://www.yreduktor.eu/index.php/en/yilmaz-reduktor-en/about-yilmaz-reduktor/) · [UK](https://www.yilmazuk.co.uk/about-us) · [Elk Motor](https://elkmotor.com.tr/en/our-companies)
- Market: [Mordor](https://www.mordorintelligence.com/industry-reports/industrial-gearbox-market) · [GM Insights](https://www.gminsights.com/industry-analysis/industrial-gearbox-market) · [Grand View](https://www.grandviewresearch.com/industry-analysis/industrial-gearbox-market-report) · [Automation.com](https://www.automation.com/en-us/articles/june-2021/geared-motors-industrial-gears-two-trends)
- Interchange: [NORD guide](https://www.yumpu.com/en/document/view/9556707/nord-interchange-guide) · [Falk](https://www.rexnord.com/contentitems/techlibrary/documents/950-501_interchangeguide) · [NMRV](http://www.tvtamerica.com/bfk-sfk%20wormgears.htm) · [Motovario catalogue](https://my.motovario.com/uploads/pdf_static/TECHNICAL%20CATALOGUE_VSF_IEC_STD_EN_rev0_2017.pdf)
- Options/efficiency: [Bauer IE guide](https://www.bauergears.com/en/products/energy-efficient-geared-motors/ie3-geared-motors) · [IEC 60034-30-1 overview](https://www.4q-systems.com/what-is-ie3-and-ie4-motor-efficiency/)
