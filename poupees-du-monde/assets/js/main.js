/* =============================================================
   Poupées du Monde — Interactions
   ============================================================= */
(function () {
  "use strict";
  const CFG = window.SITE_CONFIG || {};
  const I18N = window.I18N || {};
  const $  = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const RTL = new Set(["ar"]);
  let lang = localStorage.getItem("pdm_lang") || "fr";
  if (!I18N[lang]) lang = "fr";

  /* ---------------- i18n ---------------- */
  function t(key) { return (I18N[lang] && I18N[lang][key]) || (I18N.fr && I18N.fr[key]) || ""; }

  function applyLang() {
    const dict = I18N[lang] || {};
    document.documentElement.lang = lang;
    document.documentElement.dir = RTL.has(lang) ? "rtl" : "ltr";

    $$("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      const val = dict[key];
      if (val == null) return;
      const attr = el.getAttribute("data-i18n-attr");
      if (attr) el.setAttribute(attr, val.replace(/<[^>]+>/g, ""));
      else el.innerHTML = val;
    });

    // <title> + meta description
    if (dict["doc.title"]) document.title = dict["doc.title"];

    // active state + current label on the language dropdown
    const menuBtns = $$("#lang-menu button");
    menuBtns.forEach((b) => b.classList.toggle("is-active", b.dataset.lang === lang));
    const active = menuBtns.find((b) => b.dataset.lang === lang);
    const cur = $("#lang-current");
    if (cur && active) cur.textContent = active.dataset.code || lang.toUpperCase();

    renderConfigContent();
    localStorage.setItem("pdm_lang", lang);
  }

  const langSwitch = $("#lang-switch"), langToggle = $("#lang-toggle");
  function closeLangMenu() {
    if (langSwitch) langSwitch.classList.remove("open");
    if (langToggle) langToggle.setAttribute("aria-expanded", "false");
  }
  if (langToggle) langToggle.addEventListener("click", (e) => {
    e.stopPropagation();
    const open = !langSwitch.classList.contains("open");
    langSwitch.classList.toggle("open", open);
    langToggle.setAttribute("aria-expanded", String(open));
  });
  $$("#lang-menu button").forEach((btn) =>
    btn.addEventListener("click", () => { lang = btn.dataset.lang; applyLang(); closeLangMenu(); })
  );
  document.addEventListener("click", (e) => {
    if (langSwitch && !langSwitch.contains(e.target)) closeLangMenu();
  });

  /* ---------------- Inject config-driven content ---------------- */
  function pickLabel(obj) { return obj[lang] || obj.fr || obj.en || ""; }

  function renderConfigContent() {
    // Hours
    const ht = $("#hours-table");
    if (ht) ht.innerHTML = (CFG.hours || []).map((h) =>
      `<tr><td>${pickLabel(h)}</td><td>${h.time || "—"}</td></tr>`).join("");

    // Prices
    const pt = $("#prices-table");
    if (pt) pt.innerHTML = (CFG.prices || []).map((p) =>
      `<tr><td>${pickLabel(p)}</td><td>${p.value || ""}</td></tr>`).join("");

    // Address
    const addr = $("#address-line");
    if (addr) addr.textContent = CFG.address || "";

    // Maps link + embed
    const mapsHref = CFG.mapsEmbed
      ? "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(CFG.mapsQuery || CFG.address || "Rabat")
      : "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(CFG.mapsQuery || CFG.address || "Rabat");
    const ml = $("#maps-link"); if (ml) ml.href = mapsHref;

    const me = $("#map-embed");
    if (me) {
      if (CFG.mapsEmbed) {
        me.innerHTML = `<iframe src="${CFG.mapsEmbed}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="Map"></iframe>`;
      } else {
        me.innerHTML = `<a class="map-fallback" href="${mapsHref}" target="_blank" rel="noopener"><span>📍</span><span>${t("info.mapbtn")}</span></a>`;
      }
    }

    // Contact links
    const tel = $("#tel-link");
    if (tel) { tel.textContent = CFG.phoneDisplay || ""; tel.href = "tel:" + (CFG.phoneDisplay || "").replace(/[^\d+]/g, ""); }
    const em = $("#email-link");
    if (em) { em.textContent = CFG.email || ""; em.href = "mailto:" + (CFG.email || ""); }

    // WhatsApp button
    const wa = $("#whatsapp-btn");
    if (wa) wa.href = buildWhatsAppLink();

    // Footer contact/social
    const fTel = $("#footer-tel");
    if (fTel) { fTel.textContent = CFG.phoneDisplay || ""; fTel.href = "tel:" + (CFG.phoneDisplay || "").replace(/[^\d+]/g, ""); }
    const fIg = $("#footer-ig"); if (fIg) fIg.href = CFG.instagram || "#";
    const fFb = $("#footer-fb"); if (fFb) fFb.href = CFG.facebook || "#";

    const soc = $("#footer-social");
    if (soc) soc.innerHTML = `
      <a href="${CFG.instagram || "#"}" target="_blank" rel="noopener" aria-label="Instagram"><svg viewBox="0 0 24 24"><path d="M12 2.16c3.2 0 3.58.01 4.85.07 1.17.05 1.8.25 2.23.41.56.22.96.48 1.38.9.42.42.68.82.9 1.38.16.42.36 1.06.41 2.23.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.05 1.17-.25 1.8-.41 2.23-.22.56-.48.96-.9 1.38-.42.42-.82.68-1.38.9-.42.16-1.06.36-2.23.41-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-1.17-.05-1.8-.25-2.23-.41a3.7 3.7 0 0 1-1.38-.9 3.7 3.7 0 0 1-.9-1.38c-.16-.42-.36-1.06-.41-2.23C2.17 15.58 2.16 15.2 2.16 12s.01-3.58.07-4.85c.05-1.17.25-1.8.41-2.23.22-.56.48-.96.9-1.38.42-.42.82-.68 1.38-.9.42-.16 1.06-.36 2.23-.41C8.42 2.17 8.8 2.16 12 2.16Zm0 1.62c-3.15 0-3.5.01-4.74.07-.9.04-1.38.19-1.7.32-.43.16-.73.36-1.05.68-.32.32-.52.62-.68 1.05-.13.32-.28.8-.32 1.7-.06 1.24-.07 1.6-.07 4.74s.01 3.5.07 4.74c.04.9.19 1.38.32 1.7.16.43.36.73.68 1.05.32.32.62.52 1.05.68.32.13.8.28 1.7.32 1.24.06 1.6.07 4.74.07s3.5-.01 4.74-.07c.9-.04 1.38-.19 1.7-.32.43-.16.73-.36 1.05-.68.32-.32.52-.62.68-1.05.13-.32.28-.8.32-1.7.06-1.24.07-1.6.07-4.74s-.01-3.5-.07-4.74c-.04-.9-.19-1.38-.32-1.7a2.8 2.8 0 0 0-.68-1.05 2.8 2.8 0 0 0-1.05-.68c-.32-.13-.8-.28-1.7-.32-1.24-.06-1.6-.07-4.74-.07Zm0 2.76a5.3 5.3 0 1 1 0 10.6 5.3 5.3 0 0 1 0-10.6Zm0 1.62a3.68 3.68 0 1 0 0 7.36 3.68 3.68 0 0 0 0-7.36Zm5.5-1.06a1.24 1.24 0 1 1-2.48 0 1.24 1.24 0 0 1 2.48 0Z"/></svg></a>
      <a href="${CFG.facebook || "#"}" target="_blank" rel="noopener" aria-label="Facebook"><svg viewBox="0 0 24 24"><path d="M22 12a10 10 0 1 0-11.56 9.88v-6.99H7.9V12h2.54V9.8c0-2.5 1.49-3.89 3.78-3.89 1.09 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56V12h2.78l-.44 2.89h-2.34v6.99A10 10 0 0 0 22 12Z"/></svg></a>`;
  }

  function buildWhatsAppLink() {
    const num = (CFG.whatsapp || "").replace(/[^\d]/g, "");
    const msg = {
      fr: "Bonjour, je souhaite réserver une visite au musée Poupées du Monde.",
      en: "Hello, I'd like to book a visit to the Poupées du Monde museum.",
      ar: "مرحبًا، أودّ حجز زيارة إلى متحف عرائس العالم.",
    }[lang];
    return `https://wa.me/${num}?text=${encodeURIComponent(msg)}`;
  }

  /* ---------------- Header scroll state ---------------- */
  const header = $("#header");
  const onScroll = () => header.classList.toggle("scrolled", window.scrollY > 40);
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------------- Mobile nav ---------------- */
  const nav = $("#nav"), burger = $("#hamburger");
  function toggleNav(force) {
    const open = force != null ? force : !nav.classList.contains("open");
    nav.classList.toggle("open", open);
    burger.setAttribute("aria-expanded", String(open));
    document.body.style.overflow = open ? "hidden" : "";
  }
  burger.addEventListener("click", () => toggleNav());
  $$("#nav a").forEach((a) => a.addEventListener("click", () => toggleNav(false)));

  /* ---------------- Reveal on scroll ---------------- */
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
  }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
  $$(".reveal").forEach((el) => io.observe(el));

  /* ---------------- Lightbox ---------------- */
  const lb = $("#lightbox"), lbImg = $("#lb-img"), lbCap = $("#lb-cap");
  let gItems = [], idx = 0;
  function collectItems() { gItems = $$("#gallery-grid img"); }
  function openLb(i) {
    idx = (i + gItems.length) % gItems.length;
    const img = gItems[idx];
    lbImg.src = img.dataset.full || img.src;
    lbImg.alt = img.alt || "";
    lbCap.textContent = img.alt || "";
    lb.classList.add("open"); lb.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }
  function closeLb() { lb.classList.remove("open"); lb.setAttribute("aria-hidden", "true"); document.body.style.overflow = ""; }
  collectItems();
  $("#gallery-grid").addEventListener("click", (e) => {
    const fig = e.target.closest(".g-item"); if (!fig) return;
    const img = fig.querySelector("img"); if (!img) return;
    collectItems(); openLb(gItems.indexOf(img));
  });
  $("#lb-close").addEventListener("click", closeLb);
  $("#lb-next").addEventListener("click", () => openLb(idx + 1));
  $("#lb-prev").addEventListener("click", () => openLb(idx - 1));
  lb.addEventListener("click", (e) => { if (e.target === lb) closeLb(); });
  document.addEventListener("keydown", (e) => {
    if (!lb.classList.contains("open")) return;
    if (e.key === "Escape") closeLb();
    else if (e.key === "ArrowRight") openLb(idx + 1);
    else if (e.key === "ArrowLeft") openLb(idx - 1);
  });

  /* ---------------- Booking form ---------------- */
  const form = $("#booking-form"), statusEl = $("#form-status");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    statusEl.className = "form-status";
    const name = $("#bf-name").value.trim();
    const email = $("#bf-email").value.trim();
    if (!name) { statusEl.textContent = t("book.reqname"); statusEl.classList.add("err"); return; }
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { statusEl.textContent = t("book.reqemail"); statusEl.classList.add("err"); return; }

    const data = {
      name, email,
      phone: $("#bf-phone").value.trim(),
      date: $("#bf-date").value,
      people: $("#bf-people").value,
      tour_language: $("#bf-lang").value,
      message: $("#bf-msg").value.trim(),
      _subject: `Réservation — Poupées du Monde — ${name}`,
    };

    const btn = $("#bf-submit");
    const original = btn.textContent;
    btn.disabled = true; btn.textContent = t("book.sending");

    try {
      if (CFG.formEndpoint) {
        const res = await fetch(CFG.formEndpoint, {
          method: "POST",
          headers: { "Accept": "application/json", "Content-Type": "application/json" },
          body: JSON.stringify(data),
        });
        if (!res.ok) throw new Error("bad response");
        statusEl.textContent = t("book.success"); statusEl.classList.add("ok");
        form.reset();
      } else {
        // Fallback: open the visitor's mail app pre-filled.
        const body = [
          `${t("book.name")}: ${data.name}`,
          `${t("book.email")}: ${data.email}`,
          `${t("book.phone")}: ${data.phone}`,
          `${t("book.date")}: ${data.date}`,
          `${t("book.people")}: ${data.people}`,
          `${t("book.lang")}: ${data.tour_language}`,
          `${t("book.msg")}: ${data.message}`,
        ].join("\n");
        window.location.href = `mailto:${CFG.email}?subject=${encodeURIComponent(data._subject)}&body=${encodeURIComponent(body)}`;
        statusEl.textContent = t("book.success"); statusEl.classList.add("ok");
      }
    } catch (err) {
      statusEl.textContent = t("book.error"); statusEl.classList.add("err");
    } finally {
      btn.disabled = false; btn.textContent = original;
    }
  });

  /* ---------------- Calendly reservation calendar ---------------- */
  (function initCalendly() {
    const url = CFG.calendlyUrl;
    if (!url) return;                       // no link yet → keep the simple form
    if (form) form.hidden = true;           // hide the fallback form
    const wrap = $("#calendly-embed");
    if (!wrap) return;
    wrap.hidden = false;
    const sep = url.includes("?") ? "&" : "?";
    const full = url + sep + "hide_gdpr_banner=1";
    wrap.innerHTML =
      `<div class="calendly-inline-widget" data-url="${full}" style="min-width:320px;height:720px;"></div>`;
    const s = document.createElement("script");
    s.src = "https://assets.calendly.com/assets/external/widget.js";
    s.async = true;
    document.body.appendChild(s);
  })();

  /* ---------------- Init ---------------- */
  $("#year").textContent = new Date().getFullYear();
  applyLang();
})();
