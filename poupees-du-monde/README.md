# Poupées du Monde — Website

Showcase + booking website for **Poupées du Monde**, the private doll museum in the
Médina of Rabat (2,500+ folk-costume dolls from 90+ countries). Static site —
HTML/CSS/vanilla JS, trilingual **Français · English · العربية** (with RTL).

## Run locally
No build step. Just serve the folder:
```bash
cd poupees-du-monde
python3 -m http.server 8000
# open http://localhost:8000
```
(Opening `index.html` directly works too, but a local server is recommended.)

## Go live — edit ONE file: `config.js`
Replace every value marked « À CONFIRMER »:
| Key | What it is |
|-----|------------|
| `whatsapp` | WhatsApp number, digits only, e.g. `212600112233` |
| `phoneDisplay` | Phone shown on the page |
| `email` | Address that receives booking requests |
| `formEndpoint` | Free form endpoint (see below). Empty = falls back to opening the visitor's mail app |
| `address` | Exact street address in the medina |
| `mapsEmbed` | Google Maps embed `src` (Maps → Share → Embed a map) |
| `instagram`, `facebook` | Social links |
| `hours` | Opening hours per day |
| `prices` | Admission prices |

### Booking form delivery
1. Create a free form at **https://formspree.io** (or https://web3forms.com).
2. Paste its endpoint URL into `formEndpoint` in `config.js`.
3. Submissions now land in your inbox. Until then, the form opens the visitor's
   email app pre-filled, and the **WhatsApp** button works immediately.

## Photos & logo
- Photos live in `assets/img/` (`*.jpg` full + `*-thumb.jpg` gallery). Replace with
  same filenames to swap images — no code changes needed.
- Logo processed into `assets/logo/` (badge, transparent mark, white mark, favicons)
  from the supplied artwork.

## Deploy (free)
- **Netlify:** drag the `poupees-du-monde` folder onto app.netlify.com — done.
- **GitHub Pages:** push, then Settings → Pages → deploy from branch. `.nojekyll` is included.

## Translations
All UI text is in `assets/js/i18n.js` (`fr`, `en`, `ar` objects). Edit values there;
keys are wired to the HTML via `data-i18n`.
