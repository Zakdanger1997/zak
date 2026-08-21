# Poupées du Monde — Developer Handoff

Everything needed to maintain and edit the **Poupées du Monde** website (doll museum, Médina de Rabat). No build tools, no framework — plain HTML/CSS/JS. Anyone comfortable with a text editor and cPanel can edit it.

---

## 1. Live site & current status

| | |
|---|---|
| **Live URL** | http://poupeesdumonderabat.com  *(http only for now — see SSL below)* |
| **Domain registrar + hosting** | güzelhosting (guzel.net.tr) — cPanel |
| **cPanel user** | `poupeesd` |
| **Primary domain** | `poupeesdumonderabat.com` (Ana Etki Alanı) |
| **Document root** | `/public_html` |
| **Server IP** | 89.252.180.243 |
| **Git repo** | `github.com/Zakdanger1997/zak` — branch `claude/business-website-booking-ftzylr`, folder `poupees-du-monde/` |

**⚠️ Outstanding items (see section 7):**
1. **SSL certificate not installed yet** → `https://` shows "Not Private". `Force HTTPS Redirect` is currently **OFF** so the site works over http. Fix = güzelhosting installs free AutoSSL, then re-enable the redirect.
2. **Opening hours are placeholder values** — need the real ones.
3. **Booking uses a form + WhatsApp + email** — a Calendly calendar can be switched on (optional).

---

## 2. What the site is

A single-page, responsive, **6-language** brochure + booking site:
- Languages: **Français, English, Español, Italiano, Русский, العربية** (Arabic is full right-to-left).
- Sections: Hero → Our story → The collection → Gallery (with lightbox) → Practical info (hours/prices/map) → Booking → Footer.
- Booking = a form (emails the museum) + a **WhatsApp** button + `mailto` fallback.

---

## 3. File structure

```
poupees-du-monde/
├── index.html              # Page structure (sections, elements)
├── config.js               # ⭐ EDIT ME: all business data (prices, hours, phone, email, map, social, Calendly)
├── assets/
│   ├── css/styles.css      # All styling / design system
│   ├── js/
│   │   ├── i18n.js         # ⭐ EDIT ME: all text, in 6 languages
│   │   └── main.js         # Behavior (language switch, gallery, booking, menu)
│   ├── img/                # Photos (both full + -thumb versions)
│   └── logo/               # Logo (badge, marks, favicons)
├── CNAME, robots.txt, sitemap.xml   # SEO / domain files
├── README.md               # Quick start
└── poupees-du-monde.html   # Auto-generated SINGLE-FILE build (everything inlined) — do not hand-edit
```

**The two files you edit 95% of the time: `config.js` and `assets/js/i18n.js`.**

---

## 4. How to edit common things

### 4.1 Business data — `config.js`
Open `config.js`. It's plain, commented JavaScript. Edit the values:
- `whatsapp` — WhatsApp number, digits only (e.g. `212664935740`)
- `phoneDisplay` — phone shown on page
- `email` — where booking form requests go (`poupeesdumonderabat@gmail.com`)
- `formEndpoint` — paste a free Formspree/Web3Forms URL to make the booking form email you (empty = opens visitor's mail app)
- `calendlyUrl` — paste a Calendly link here to replace the form with a live booking calendar
- `address`, `mapsEmbed`, `mapsQuery` — location + Google Map
- `instagram`, `facebook` — social links
- `hours` — array of `{fr, en, ar, es, it, ru, time}` rows. **← update the real opening hours here**
- `prices` — array of `{fr, en, ar, es, it, ru, value}` rows

Prices/hours labels must be provided in all 6 languages (fr, en, ar, es, it, ru). `value`/`time` are language-neutral.

### 4.2 Text / wording — `assets/js/i18n.js`
All on-screen text lives here as key→string, one block per language (`fr`, `en`, `ar`, `es`, `it`, `ru`). To change a headline, find its key (e.g. `"hero.title"`) and edit the string **in every language block**. Keys are wired to HTML via `data-i18n="key"` attributes in `index.html`.

### 4.3 Photos — `assets/img/`
Each photo has two files: `name.jpg` (full) and `name-thumb.jpg` (gallery grid). To swap a photo, replace both files keeping the **same filenames** — no code change needed. To add/remove gallery items, edit the `<figure class="g-item">` list inside the `#gallery-grid` section of `index.html` (and add matching `gal.*` text keys in `i18n.js`).
Recommended: keep JPGs ≤ 1600px wide, quality ~82, to stay fast.

### 4.4 Logo — `assets/logo/`
`logo-badge.png` (header, circular), `logo-mark-white.png` (footer), `favicon-*.png`, `apple-touch-icon.png`. Replace with same filenames/sizes to rebrand.

### 4.5 Add or remove a language
1. In `i18n.js`, add a new language object (copy `en`, translate every key).
2. In `index.html`, add a `<li><button data-lang="xx" data-code="XX">Name</button></li>` inside `#lang-menu`, and an `<option>` in the booking `#bf-lang` select.
3. In `config.js`, add the language key to each `hours`/`prices` row.
4. For RTL languages, add the code to the `RTL` set in `main.js`.

### 4.6 Colors / design
All in `assets/css/styles.css` under `:root` (CSS variables: `--cream`, `--terracotta`, `--teal`, `--gold`, etc.). Fonts load from Google Fonts in `index.html` `<head>`.

---

## 5. How to deploy changes (cPanel)

The live site is the copy in **`/public_html`**. After editing files:

1. Log into **cPanel** (güzelhosting) → **File Manager** → `public_html`.
2. Upload the changed file(s) (or a zip of the whole folder) via **Upload**.
3. If you uploaded a zip, select it → **Extract** → choose **Overwrite**.
4. Hard-refresh the site (Cmd/Ctrl+Shift+R) or use incognito to bypass cache.

**FTP** works too (same `poupeesd` credentials, upload into `public_html`).

Tip: to edit a single file quickly, cPanel File Manager → right-click the file → **Edit** → change → Save.

---

## 6. The single-file build (`poupees-du-monde.html`)

`poupees-du-monde.html` is an **auto-generated** copy of the whole site inlined into one file (CSS, JS, config, and images as base64) — handy for previewing by double-click or emailing. It is **generated from the source files**, so:
- **Do not hand-edit it.** Edit `index.html` / `config.js` / `i18n.js` / `styles.css` / `main.js`, then regenerate.
- The build script (Python + Pillow) inlines the assets. If you don't have it, the multi-file version in `public_html` is the source of truth; the single file is just a convenience export.
- For normal hosting, you deploy the **multi-file** version (section 5), not this single file.

---

## 7. Outstanding tasks / known issues

### 7.1 SSL certificate (most important)
- Status: **not installed.** `https://` shows "This Connection Is Not Private" (self-signed cert only).
- `Force HTTPS Redirect` is **OFF** so the site is reachable over http.
- **Fix:** güzelhosting must run **AutoSSL / free Let's Encrypt** for `poupeesdumonderabat.com`. Their panel hides the "Run AutoSSL" button and pushes paid certs, so it usually needs a **support ticket** ("please install free AutoSSL/Let's Encrypt for poupeesdumonderabat.com, user poupeesd").
  - Alternative DIY: generate a free cert at **zerossl.com** (HTTP file validation via `public_html/.well-known/pki-validation/`), then cPanel → **SSL/TLS → Install and Manage SSL** → paste cert + key + CA bundle.
- **After the cert is installed:** cPanel → Domains → turn **Force HTTPS Redirect ON** for the full `https://` padlock.

### 7.2 Opening hours
`config.js` `hours` are placeholder (Mon–Fri 9:30–18:00, Sat 9:30–18:00, Sun 10:00–17:00). Replace with the real schedule.

### 7.3 Booking delivery
- Currently: form opens the visitor's mail app (no `formEndpoint` set) + WhatsApp button works.
- To make the form email the museum automatically: create a free form at **formspree.io** or **web3forms.com**, paste the endpoint into `config.calendlyUrl`… no — into `config.formEndpoint`.
- To use a real booking **calendar** (auto-confirms to museum + visitor): create a free **Calendly** account, set availability, paste the scheduling link into `config.calendlyUrl`. The form is then replaced by the live calendar automatically.

### 7.4 Prices (already updated)
Current admission prices in `config.js`: Adult Resident **20 DH**, Adult Non-resident **40 DH**, Child under 12 **10 DH**.

### 7.5 Corporate firewall note
Some office networks (FortiGate/Fortinet) temporarily block the domain as a "Newly Observed Domain" because it's newly registered. This clears itself within a few days–weeks. Not a site problem — test on mobile data if blocked.

---

## 8. Contact data currently in the site
- Email: `poupeesdumonderabat@gmail.com`
- Phone/WhatsApp: `+212 664-935740` *(confirm it has WhatsApp)*
- Address: `3 impasse Nakhla, Rue Bouqroune — Médina de Rabat 10000`
- Instagram: `@poupeesdumonderabat` · Facebook: `poupees.du.monde.rabat`

---

## 9. Quick reference — "I want to change X"

| I want to change… | Edit this |
|---|---|
| Prices / opening hours | `config.js` (`prices`, `hours`) |
| Phone / WhatsApp / email | `config.js` |
| Any on-screen text | `assets/js/i18n.js` (all 6 language blocks) |
| A photo | replace file in `assets/img/` (same name, + `-thumb`) |
| Logo | replace files in `assets/logo/` |
| Google Map | `config.js` `mapsEmbed` |
| Colors / fonts | `assets/css/styles.css` (`:root`), `index.html` `<head>` |
| Turn on booking calendar | `config.js` `calendlyUrl` |
| Publish changes | upload edited files to `public_html` via cPanel File Manager |

---

*Built as a static site so it stays fast, free to host, and easy to maintain. Source of truth = the files in `/public_html` (mirrored in the GitHub repo). No compilation step required.*
