/* =============================================================
   Poupées du Monde — SITE CONFIGURATION
   -------------------------------------------------------------
   This is the ONLY file the owner needs to edit to go live.
   Replace every value marked  «À CONFIRMER / TO CONFIRM».
   ============================================================= */
window.SITE_CONFIG = {

  /* --- Contact & booking --------------------------------- */
  // WhatsApp number in international format, digits only (no +, spaces or 0).
  // Morocco example: 212600112233  ( = +212 6 00 11 22 33 )
  whatsapp: "212664935740",                 // « À CONFIRMER que ce numéro a WhatsApp »
  phoneDisplay: "+212 664-935740",          // trouvé publiquement — à confirmer
  email: "contact@poupeesdumonde.ma",       // « À CONFIRMER (email réel) »

  // ---- Reservation calendar (Calendly) ----
  // Paste your Calendly scheduling link here, e.g.
  //   "https://calendly.com/poupeesdumonde/visite"
  // When set, a live booking calendar replaces the simple form. Calendly then
  // emails BOTH you and the visitor a confirmation automatically.
  // Works with Cal.com links too. Leave empty to use the simple form below.
  calendlyUrl: "",

  // Booking form delivery.
  // Easiest: create a free form at https://formspree.io (or https://web3forms.com)
  // and paste the endpoint URL here. If left empty, the form falls back to
  // opening the visitor's email app pre-filled (mailto).
  formEndpoint: "",                         // e.g. "https://formspree.io/f/xxxxxxx"

  /* --- Location ------------------------------------------ */
  // Shown as the address text.
  address: "3 impasse Nakhla, Rue Bouqroune — Médina de Rabat 10000, Maroc",
  // Google Maps: paste the full <iframe src="..."> URL from Maps > Share > Embed.
  // If empty, a link/search button to Maps is shown instead.
  // Keyless Google Maps embed (no API key required).
  mapsEmbed: "https://www.google.com/maps?q=Exposition%20Poup%C3%A9es%20du%20Monde%2C%20Rabat&z=17&output=embed",
  mapsQuery: "Exposition Poupées du Monde, Rabat",

  /* --- Social -------------------------------------------- */
  instagram: "https://www.instagram.com/poupeesdumonderabat",
  facebook: "https://www.facebook.com/poupees.du.monde.rabat",

  /* --- Opening hours ------------------------------------- *
   * Edit the time strings. Use "" for a closed day.
   * Labels are provided per language.                        */
  hours: [
    { fr: "Lundi – Vendredi", en: "Monday – Friday",   ar: "الاثنين – الجمعة", time: "9h30 – 18h00" },
    { fr: "Samedi",           en: "Saturday",          ar: "السبت",           time: "9h30 – 18h00" },
    { fr: "Dimanche",         en: "Sunday",            ar: "الأحد",           time: "10h00 – 17h00" },
  ], // « HORAIRES À CONFIRMER »

  /* --- Admission / prices -------------------------------- */
  prices: [
    { fr: "Adulte",              en: "Adult",             ar: "بالغ",              value: "40 DH" },
    { fr: "Enfant (–12 ans)",    en: "Child (under 12)",  ar: "طفل (أقل من 12)",   value: "20 DH" },
    { fr: "Visite guidée / groupe", en: "Guided / group tour", ar: "زيارة موجّهة / مجموعة", value: "Sur demande" },
  ], // « TARIFS À CONFIRMER »

};
