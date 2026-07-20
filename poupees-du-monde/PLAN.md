# Poupées du Monde Rabat — Website Build Plan

> Approved decisions (locked 2026-07-20):
> - **Build:** Static site — hand-coded HTML/CSS/vanilla JS (no framework). Free to host on GitHub Pages or Netlify, zero upkeep.
> - **Booking:** Booking form (emails the museum) + WhatsApp "Book now" button + mailto fallback. No backend.
> - **Languages:** French (primary) + English + Arabic, with correct right-to-left (RTL) layout for Arabic. JS-based language toggle.
> - **Photos:** Tasteful, correctly-sized placeholders now; owner swaps in real photos later.

---

## 0. About the business (so the copy is accurate)

**Poupées du Monde** is a private doll collection / exhibition ("musée des poupées") in the **Medina of Rabat, Morocco**.
- 2,500+ dolls in traditional folkloric costumes from 90+ countries.
- Housed in a traditional Moroccan riad with a patio garden.
- Ground-floor exhibition halls + upstairs section with miniatures by the artist-in-residence, **Mrs Haffar**.
- Positioned as a cultural attraction / hidden gem in the medina.

The website's job: **showcase the collection beautifully + let visitors book a visit or guided tour.**

⚠️ Instagram, Facebook, and LinkedIn are login-gated — their photos/design cannot be scraped automatically. Real photos + logo will be supplied by the owner.

---

## 1. Information to collect from the owner (blocking real content)

- [ ] Logo file(s) — SVG or high-res PNG (transparent background ideal)
- [ ] 10–20 real photos (exhibition halls, patio, dolls close-ups, exterior/entrance, miniatures)
- [ ] Exact address in the Medina + Google Maps pin/link
- [ ] Opening days & hours
- [ ] Ticket price(s): individual, child, group/guided-tour rates
- [ ] Phone number + WhatsApp number (with country code, e.g. +212…)
- [ ] Email address to receive booking requests
- [ ] Social links: Instagram, Facebook (and LinkedIn if any)
- [ ] Preferred domain name (e.g. poupeesdumonde.ma) — optional, for later
- [ ] Brand colors / any existing palette (else I'll design one that matches the riad aesthetic)

> Until these arrive, the site is built with clearly-marked placeholders and safe default text so it looks complete.

---

## 2. Site structure (single-page + smooth-scroll nav)

Single responsive page with anchored sections + sticky header. Sections:

1. **Header / Nav** — logo, section links, language toggle (FR · EN · ع), "Book a visit" button.
2. **Hero** — museum name, tagline, hero photo, primary CTA (Book a visit) + secondary (Discover the collection).
3. **About / Our Story** — the collection, 2,500 dolls, 90+ countries, the riad & patio, Mrs Haffar.
4. **The Experience** — 3 cards: exhibition halls · patio garden · upstairs miniatures.
5. **Gallery** — responsive photo grid with lightbox (placeholders now).
6. **Practical info** — hours, address, prices, embedded Google Map.
7. **Booking** — form (name, email, date, group size, language, message) → sends via email; WhatsApp "Book now" button; mailto fallback.
8. **Contact / Footer** — address, phone, email, social icons, copyright.

---

## 3. Technical checklist

### Scaffolding
- [ ] `poupees-du-monde/` folder with `index.html`, `assets/css/styles.css`, `assets/js/main.js`, `assets/img/`, `assets/logo/`
- [ ] `favicon` + web manifest
- [ ] `.nojekyll` (for GitHub Pages) or `netlify.toml`

### Layout & styling
- [ ] Mobile-first responsive CSS (fl/grid), no framework
- [ ] Design system: color palette (warm riad tones — terracotta, deep green, cream, gold accent), typography (elegant serif headings + clean sans body, with an Arabic-capable font like Noto Naskh/Cairo), spacing scale
- [ ] Sticky header with scroll behavior + mobile hamburger menu
- [ ] Reusable card / button / section components (CSS)
- [ ] Subtle scroll-in animations (respect `prefers-reduced-motion`)

### Internationalization (FR / EN / AR)
- [ ] All copy stored in a JS translations object (`fr`, `en`, `ar`)
- [ ] Language toggle updates text + `<html lang>` + `dir="rtl"` for Arabic
- [ ] RTL stylesheet adjustments (logical properties / mirrored layout)
- [ ] Language preference saved to `localStorage`
- [ ] Default language = French

### Gallery
- [ ] Responsive image grid, lazy-loaded
- [ ] Lightbox (vanilla JS, keyboard + swipe accessible)
- [ ] Correctly-sized placeholder images with alt text

### Booking (no backend)
- [ ] Booking form with client-side validation (name, email, preferred date, group size, tour language, message)
- [ ] Submit via a form service (Formspree/Web3Forms — free, owner adds their endpoint) → lands in museum email
- [ ] `mailto:` fallback that pre-fills the message
- [ ] WhatsApp "Book now" button that pre-fills a message to the museum number
- [ ] Success / error states + confirmation message

### Info & map
- [ ] Hours/prices table
- [ ] Embedded Google Map (owner's exact pin)
- [ ] Click-to-call phone + click-to-email links

### SEO / sharing / quality
- [ ] `<title>`, meta description, Open Graph + Twitter cards (per language where feasible)
- [ ] `hreflang` handling for FR/EN/AR
- [ ] JSON-LD structured data (`Museum` / `TouristAttraction` with hours, address, geo)
- [ ] `sitemap.xml` + `robots.txt`
- [ ] Alt text on all images
- [ ] Accessibility pass: color contrast, focus states, keyboard nav, ARIA on menu/lightbox/form
- [ ] Performance: compressed images, lazy loading, minimal JS

### Verify & ship
- [ ] Test in browser (Playwright/Chromium) at mobile + desktop widths
- [ ] Test all 3 languages incl. RTL correctness
- [ ] Test booking form, WhatsApp button, mailto, map, lightbox
- [ ] `README.md` with: how to run locally, how to swap photos/logo, how to set the Formspree/WhatsApp/email values, how to deploy
- [ ] Commit + push to `claude/business-website-booking-ftzylr`
- [ ] (Optional, on request) open a PR

---

## 4. Placeholders the owner will replace (single source of truth)

Values centralized at the top of `main.js` / a `config.js` so they're easy to edit:
- `WHATSAPP_NUMBER`
- `CONTACT_EMAIL`
- `FORM_ENDPOINT` (Formspree/Web3Forms)
- `MAPS_EMBED_URL`
- `SOCIAL_LINKS` (instagram, facebook)
- `HOURS`, `PRICES`, `ADDRESS`
- Logo file in `assets/logo/`
- Photos in `assets/img/`

---

## 5. Suggested build order (when you say "run it")

1. Scaffold files + design system + fonts.
2. Header + hero + language toggle skeleton (prove i18n + RTL early).
3. About + Experience + Gallery sections.
4. Practical info + map.
5. Booking (form + WhatsApp + mailto).
6. SEO, structured data, accessibility, animations.
7. Placeholder images + config values.
8. Browser test (3 languages, mobile/desktop), fix.
9. README + commit + push.

---

*When ready, tell me "run the plan" (or adjust anything above first).*
