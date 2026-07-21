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
  whatsapp: "212600000000",                 // « À CONFIRMER »
  phoneDisplay: "+212 6 00 00 00 00",       // « À CONFIRMER »
  email: "contact@poupeesdumonde.ma",       // « À CONFIRMER »

  // Booking form delivery.
  // Easiest: create a free form at https://formspree.io (or https://web3forms.com)
  // and paste the endpoint URL here. If left empty, the form falls back to
  // opening the visitor's email app pre-filled (mailto).
  formEndpoint: "",                         // e.g. "https://formspree.io/f/xxxxxxx"

  /* --- Location ------------------------------------------ */
  // Shown as the address text.
  address: "Médina de Rabat — Rabat, Maroc",   // « À CONFIRMER (adresse exacte) »
  // Google Maps: paste the full <iframe src="..."> URL from Maps > Share > Embed.
  // If empty, a link/search button to Maps is shown instead.
  mapsEmbed: "",
  mapsQuery: "Poupées du Monde Rabat Médina",

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
