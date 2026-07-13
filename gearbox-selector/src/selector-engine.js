/* ================= I-MAK Redüktör Seçici — per-application engine =================
   Each application is its OWN page: diagram + its own formula + a live worked
   calculation (like the I-MAK training deck) + result. Bilingual TR/EN.
   Formula sources: I-MAK ArGe Teknik Eğitim Sunumu + standard drive engineering. */
const G = 9.81;
const IEC = [0.12,0.18,0.25,0.37,0.55,0.75,1.1,1.5,2.2,3,4,5.5,7.5,11,15,18.5,22,30,37,45,55,75,90,110,132,160,200,250,315,355];
const iecUp = p => { for (const s of IEC) if (s >= p - 1e-9) return s; return IEC[IEC.length-1]; };

/* rounding helper for readable worked expressions */
const R = (x,d=2) => { const p=10**d; return Math.round(x*p)/p; };

/* ---- diagrams (schematic SVG per application family) ---- */
const S = '#8b939e', RD = '#e11d13';
function svg(inner){ return '<svg viewBox="0 0 240 130" width="100%" height="100%" preserveAspectRatio="xMidYMid meet">'+inner+'</svg>'; }
const DIA = {
 belt: svg(`<line x1="20" y1="105" x2="150" y2="55" stroke="${S}" stroke-width="2"/><circle cx="28" cy="105" r="14" fill="none" stroke="${RD}" stroke-width="3"/><circle cx="150" cy="55" r="10" fill="none" stroke="${RD}" stroke-width="3"/><line x1="20" y1="119" x2="150" y2="69" stroke="${S}" stroke-width="2"/><rect x="70" y="72" width="20" height="12" fill="${S}" transform="rotate(-21 80 78)"/><path d="M150 55 l18 -7" stroke="${RD}" stroke-width="2" marker-end="url(#a)"/><text x="118" y="40" fill="${S}" font-size="11">v</text><text x="40" y="122" fill="${S}" font-size="11">α</text>`),
 screw: svg(`<rect x="24" y="52" width="150" height="26" rx="13" fill="none" stroke="${S}" stroke-width="2"/>${Array.from({length:9},(_,i)=>`<ellipse cx="${40+i*15}" cy="65" rx="5" ry="13" fill="none" stroke="${RD}" stroke-width="2"/>`).join('')}<line x1="24" y1="65" x2="180" y2="65" stroke="${S}" stroke-width="1"/><rect x="60" y="30" width="24" height="14" fill="none" stroke="${S}" stroke-width="2"/><text x="60" y="26" fill="${S}" font-size="10">Q</text>`),
 elevator: svg(`<rect x="60" y="20" width="60" height="95" fill="none" stroke="${S}" stroke-width="2"/><circle cx="90" cy="30" r="9" fill="none" stroke="${RD}" stroke-width="3"/><circle cx="90" cy="105" r="9" fill="none" stroke="${RD}" stroke-width="3"/><line x1="72" y1="30" x2="72" y2="105" stroke="${S}"/><line x1="108" y1="30" x2="108" y2="105" stroke="${S}"/>${[42,62,82].map(y=>`<path d="M64 ${y} h8 v6 h-8 z" fill="${RD}"/>`).join('')}${[52,72,92].map(y=>`<path d="M108 ${y} h8 v6 h-8 z" fill="${S}"/>`).join('')}<text x="128" y="70" fill="${S}" font-size="11">H</text>`),
 chain: svg(`<line x1="20" y1="60" x2="180" y2="60" stroke="${S}" stroke-width="2"/><line x1="20" y1="90" x2="180" y2="90" stroke="${S}" stroke-width="2"/><circle cx="28" cy="75" r="15" fill="none" stroke="${RD}" stroke-width="3"/><circle cx="180" cy="75" r="12" fill="none" stroke="${RD}" stroke-width="3"/>${Array.from({length:9},(_,i)=>`<rect x="${44+i*15}" y="55" width="9" height="9" fill="none" stroke="${S}"/>`).join('')}<rect x="90" y="42" width="22" height="12" fill="${S}"/>`),
 vib: svg(`<rect x="55" y="45" width="110" height="34" rx="4" fill="none" stroke="${S}" stroke-width="2"/><line x1="60" y1="79" x2="66" y2="95" stroke="${RD}" stroke-width="2"/><line x1="66" y1="95" x2="72" y2="79" stroke="${RD}" stroke-width="2"/><path d="M72 95 l6 16 6-16 6 16 6-16 6 16 6-16 6 16 6-16" fill="none" stroke="${RD}" stroke-width="2"/><circle cx="110" cy="62" r="9" fill="none" stroke="${RD}" stroke-width="3"/><line x1="110" y1="62" x2="116" y2="56" stroke="${RD}" stroke-width="2"/><path d="M150 40 a20 12 0 0 1 14 8" fill="none" stroke="${S}" stroke-width="2" marker-end="url(#a)"/>`),
 hoist: svg(`<circle cx="70" cy="45" r="22" fill="none" stroke="${RD}" stroke-width="3"/><line x1="70" y1="45" x2="86" y2="30" stroke="${RD}" stroke-width="2"/><line x1="92" y1="45" x2="92" y2="100" stroke="${S}" stroke-width="2"/><rect x="80" y="100" width="24" height="16" fill="none" stroke="${S}" stroke-width="2"/><path d="M92 116 v8" stroke="${S}"/><path d="M88 124 a4 4 0 1 0 8 0" fill="none" stroke="${RD}" stroke-width="2"/><text x="108" y="112" fill="${S}" font-size="11">m</text><text x="60" y="80" fill="${S}" font-size="11">v</text>`),
 pulley: svg(`<circle cx="60" cy="35" r="16" fill="none" stroke="${RD}" stroke-width="3"/><circle cx="120" cy="90" r="12" fill="none" stroke="${S}" stroke-width="2"/><line x1="52" y1="45" x2="112" y2="82" stroke="${S}"/><line x1="68" y1="45" x2="128" y2="82" stroke="${S}"/><rect x="106" y="102" width="28" height="16" fill="none" stroke="${S}" stroke-width="2"/><text x="140" y="114" fill="${S}" font-size="11">m</text><text x="30" y="30" fill="${S}" font-size="10">z falls</text>`),
 travel: svg(`<rect x="60" y="40" width="90" height="30" fill="none" stroke="${S}" stroke-width="2"/><circle cx="80" cy="82" r="14" fill="none" stroke="${RD}" stroke-width="3"/><circle cx="130" cy="82" r="14" fill="none" stroke="${RD}" stroke-width="3"/><circle cx="80" cy="82" r="4" fill="${S}"/><circle cx="130" cy="82" r="4" fill="${S}"/><line x1="40" y1="98" x2="175" y2="98" stroke="${S}" stroke-width="2"/><path d="M150 45 l20 0" stroke="${RD}" stroke-width="2" marker-end="url(#a)"/><text x="155" y="40" fill="${S}" font-size="11">v</text><text x="98" y="60" fill="${S}" font-size="11">Q</text>`),
 slew: svg(`<ellipse cx="110" cy="95" rx="55" ry="16" fill="none" stroke="${S}" stroke-width="2"/><ellipse cx="110" cy="80" rx="55" ry="16" fill="none" stroke="${RD}" stroke-width="3"/><line x1="110" y1="80" x2="110" y2="35" stroke="${S}" stroke-width="2"/><rect x="95" y="25" width="60" height="12" fill="none" stroke="${S}" stroke-width="2"/><path d="M150 62 a45 14 0 0 1 -20 12" fill="none" stroke="${RD}" stroke-width="2" marker-end="url(#a)"/><text x="150" y="55" fill="${S}" font-size="11">n</text>`),
 lift: svg(`<rect x="55" y="30" width="40" height="55" fill="none" stroke="${RD}" stroke-width="2"/><rect x="135" y="60" width="26" height="45" fill="none" stroke="${S}" stroke-width="2"/><circle cx="115" cy="22" r="10" fill="none" stroke="${RD}" stroke-width="3"/><line x1="75" y1="30" x2="108" y2="22" stroke="${S}"/><line x1="148" y1="60" x2="122" y2="22" stroke="${S}"/><text x="66" y="60" fill="${S}" font-size="11">Q</text><text x="132" y="55" fill="${S}" font-size="10">cw</text>`),
 mixer: svg(`<path d="M70 30 v55 a40 30 0 0 0 80 0 v-55" fill="none" stroke="${S}" stroke-width="2"/><line x1="110" y1="18" x2="110" y2="95" stroke="${RD}" stroke-width="3"/><line x1="86" y1="60" x2="134" y2="60" stroke="${RD}" stroke-width="3"/><line x1="90" y1="80" x2="130" y2="80" stroke="${RD}" stroke-width="3"/><rect x="98" y="8" width="24" height="10" fill="none" stroke="${S}" stroke-width="2"/><text x="152" y="60" fill="${S}" font-size="11">ρ</text>`),
 kiln: svg(`<line x1="30" y1="60" x2="185" y2="85" stroke="${RD}" stroke-width="3"/><line x1="30" y1="80" x2="185" y2="105" stroke="${RD}" stroke-width="3"/><ellipse cx="30" cy="70" rx="6" ry="12" fill="none" stroke="${S}" stroke-width="2"/><ellipse cx="185" cy="95" rx="6" ry="12" fill="none" stroke="${S}" stroke-width="2"/><path d="M70 95 a30 8 0 0 1 20 6" fill="none" stroke="${S}" stroke-width="2" marker-end="url(#a)"/><text x="150" y="70" fill="${S}" font-size="11">n</text>`),
 extruder: svg(`<rect x="40" y="52" width="150" height="26" rx="4" fill="none" stroke="${S}" stroke-width="2"/>${Array.from({length:8},(_,i)=>`<path d="M${52+i*16} 55 l8 20" stroke="${RD}" stroke-width="2"/>`).join('')}<circle cx="40" cy="65" r="14" fill="none" stroke="${RD}" stroke-width="3"/><path d="M190 60 l14 0 -4 8 z" fill="${S}"/><text x="60" y="40" fill="${S}" font-size="11">Q</text>`),
 mill: svg(`<circle cx="110" cy="70" r="42" fill="none" stroke="${RD}" stroke-width="3"/><circle cx="110" cy="70" r="8" fill="${S}"/>${[20,80,140,200,260,320].map(a=>`<line x1="110" y1="70" x2="${110+38*Math.cos(a*Math.PI/180)}" y2="${70+38*Math.sin(a*Math.PI/180)}" stroke="${S}"/>`).join('')}<path d="M150 40 a45 45 0 0 1 8 20" fill="none" stroke="${RD}" stroke-width="2" marker-end="url(#a)"/><text x="70" y="30" fill="${S}" font-size="11">Q</text>`),
 ball: svg(`<circle cx="110" cy="70" r="44" fill="none" stroke="${RD}" stroke-width="3"/>${[[95,90],[112,95],[128,88],[100,72],[118,74],[105,55]].map(([x,y])=>`<circle cx="${x}" cy="${y}" r="6" fill="${S}"/>`).join('')}<path d="M152 42 a46 46 0 0 1 8 20" fill="none" stroke="${RD}" stroke-width="2" marker-end="url(#a)"/>`),
 sifter: svg(`<rect x="55" y="45" width="110" height="40" rx="6" fill="none" stroke="${S}" stroke-width="2"/><line x1="55" y1="65" x2="165" y2="65" stroke="${S}" stroke-dasharray="4 3"/><circle cx="110" cy="65" r="10" fill="none" stroke="${RD}" stroke-width="3"/><path d="M110 65 l7 -7" stroke="${RD}" stroke-width="2"/><ellipse cx="110" cy="105" rx="34" ry="9" fill="none" stroke="${RD}" stroke-width="2" stroke-dasharray="4 3"/><text x="150" y="38" fill="${S}" font-size="11">r</text>`),
 pump: svg(`<circle cx="95" cy="70" r="34" fill="none" stroke="${RD}" stroke-width="3"/>${[0,60,120,180,240,300].map(a=>`<path d="M95 70 q${18*Math.cos((a+30)*Math.PI/180)} ${18*Math.sin((a+30)*Math.PI/180)} ${30*Math.cos(a*Math.PI/180)} ${30*Math.sin(a*Math.PI/180)}" fill="none" stroke="${S}"/>`).join('')}<rect x="129" y="40" width="30" height="16" fill="none" stroke="${S}" stroke-width="2"/><text x="150" y="35" fill="${S}" font-size="11">H</text>`),
 fan: svg(`<circle cx="105" cy="70" r="36" fill="none" stroke="${S}" stroke-width="2"/>${[0,45,90,135,180,225,270,315].map(a=>`<path d="M105 70 l${30*Math.cos(a*Math.PI/180)} ${30*Math.sin(a*Math.PI/180)} q${8*Math.cos((a+70)*Math.PI/180)} ${8*Math.sin((a+70)*Math.PI/180)} 0 6" fill="none" stroke="${RD}" stroke-width="2"/>`).join('')}<circle cx="105" cy="70" r="7" fill="${S}"/><rect x="141" y="55" width="26" height="30" fill="none" stroke="${S}" stroke-width="2"/><text x="150" y="50" fill="${S}" font-size="11">Δp</text>`),
};
const MARKER = '<svg width="0" height="0" style="position:absolute"><defs><marker id="a" markerWidth="7" markerHeight="7" refX="4" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 z" fill="'+RD+'"/></marker></defs></svg>';

/* ---- variable helper ---- */
const V = (id, tr, en, u, def, step) => ({id, lab:{tr,en}, u, def, step: step||1});

/* ================= APPLICATIONS ================= */
/* Each app: group, name, diagram, I-MAK series, default Sf & η, vars, formula text, calc(). */
const APPS = [
/* ---------- Konveyör & Taşıma ---------- */
{ id:"belt_h", grp:{tr:"Konveyör & Taşıma",en:"Conveying & Handling"}, dia:"belt", sf:1.25, eta:0.96,
  name:{tr:"Bantlı konveyör — yatay",en:"Belt conveyor — horizontal"}, series:{tr:"İRK Serisi (helis-konik)",en:"İRK series (helical-bevel)"},
  formula:{tr:"Mᴛ = k·m·g·r ,  n = 9,55·v/r ,  Pm = Mᴛ·n/(9550·η)", en:"Mᴛ = k·m·g·r ,  n = 9.55·v/r ,  Pm = Mᴛ·n/(9550·η)"},
  vars:[V("m","Yük kütlesi m","Load mass m","kg",10000,100),V("D","Tambur çapı Ø","Drum Ø","mm",250,5),
        V("v","Bant hızı v","Belt speed v","m/s",1.0,0.1),V("k","Sürtünme katsayısı k","Friction coeff. k","",0.125,0.005)],
  calc:v=>{const r=v.D/2000;const MT=v.k*v.m*G*r;const n=9.55*v.v/r;
    return {MT,n,steps:[
      {lab:{tr:"Tambur yarıçapı",en:"Drum radius"},expr:`r = ${v.D}/2000`,res:R(r,3),u:"m"},
      {lab:{tr:"Tambur momenti",en:"Drum moment"},expr:`Mᴛ = ${v.k}·${v.m}·9,81·${R(r,3)}`,res:R(MT),u:"Nm"},
      {lab:{tr:"Tambur devri",en:"Drum speed"},expr:`n = 9,55·${v.v}/${R(r,3)}`,res:R(n,1),u:"d/dk"}]};}},

{ id:"belt_inc", grp:{tr:"Konveyör & Taşıma",en:"Conveying & Handling"}, dia:"belt", sf:1.25, eta:0.96,
  name:{tr:"Bantlı konveyör — eğimli",en:"Belt conveyor — inclined"}, series:{tr:"İRK Serisi (helis-konik)",en:"İRK series (helical-bevel)"},
  formula:{tr:"Mᴛ = k·(cosα+sinα)·m·g·r ,  n = 9,55·v/r", en:"Mᴛ = k·(cosα+sinα)·m·g·r ,  n = 9.55·v/r"},
  vars:[V("m","Yük kütlesi m","Load mass m","kg",10000,100),V("D","Tambur çapı Ø","Drum Ø","mm",250,5),
        V("v","Bant hızı v","Belt speed v","m/s",1.0,0.1),V("a","Eğim α","Incline α","°",25,1),V("k","Sürtünme katsayısı k","Friction coeff. k","",0.125,0.005)],
  calc:v=>{const r=v.D/2000;const rad=v.a*Math.PI/180;const fac=Math.cos(rad)+Math.sin(rad);const MT=v.k*fac*v.m*G*r;const n=9.55*v.v/r;
    return {MT,n,steps:[
      {lab:{tr:"Tambur yarıçapı",en:"Drum radius"},expr:`r = ${v.D}/2000`,res:R(r,3),u:"m"},
      {lab:{tr:"Eğim faktörü",en:"Incline factor"},expr:`cos${v.a}+sin${v.a}`,res:R(fac,3),u:""},
      {lab:{tr:"Tambur momenti",en:"Drum moment"},expr:`Mᴛ = ${v.k}·${R(fac,3)}·${v.m}·9,81·${R(r,3)}`,res:R(MT),u:"Nm"},
      {lab:{tr:"Tambur devri",en:"Drum speed"},expr:`n = 9,55·${v.v}/${R(r,3)}`,res:R(n,1),u:"d/dk"}]};}},

{ id:"screw", grp:{tr:"Konveyör & Taşıma",en:"Conveying & Handling"}, dia:"screw", sf:1.25, eta:0.96,
  name:{tr:"Helezon (vidalı) konveyör",en:"Screw (auger) conveyor"}, series:{tr:"Helis redüktörlü motor",en:"Helical geared motor"},
  formula:{tr:"n = (Q/60)/G ,  Qₜₒₚ = G·(L/h) ,  v = h·n/1000 ,  Pₘ = Qₜₒₚ·v/(60·75·1,36·η)", en:"n = (Q/60)/G ,  Qₜₒₜ = G·(L/h) ,  v = h·n/1000 ,  Pₘ = Qₜₒₜ·v/(60·75·1.36·η)"},
  vars:[V("Q","Kapasite Q","Capacity Q","kg/h",8000,100),V("Gk","Hatve yükü G","Load per pitch G","kg",100,5),
        V("L","Uzunluk L","Length L","mm",3000,50),V("h","Hatve h","Pitch h","mm",300,5),V("ho","Yükleme verimi","Loading eff.","",0.30,0.05)],
  calc:v=>{const Qdk=v.Q/60;const n=Qdk/v.Gk;const pit=v.L/v.h;const Qtop=v.Gk*pit;const vel=v.h*n/1000;const P=Qtop*vel/(60*75*1.36*v.ho);const MT=n>0?9550*P/n:NaN;
    return {MT,n,Pout:P,steps:[
      {lab:{tr:"Dakikadaki debi",en:"Flow per min"},expr:`Q/60 = ${v.Q}/60`,res:R(Qdk,1),u:"kg/dk"},
      {lab:{tr:"Helezon devri",en:"Screw speed"},expr:`n = ${R(Qdk,1)}/${v.Gk}`,res:R(n,2),u:"d/dk"},
      {lab:{tr:"Hatve sayısı",en:"No. of pitches"},expr:`${v.L}/${v.h}`,res:R(pit,1),u:""},
      {lab:{tr:"Toplam yük",en:"Total load"},expr:`Qₜₒₚ = ${v.Gk}·${R(pit,1)}`,res:R(Qtop),u:"kg"},
      {lab:{tr:"İlerleme hızı",en:"Advance speed"},expr:`v = ${v.h}·${R(n,2)}/1000`,res:R(vel,3),u:"m/dk"},
      {lab:{tr:"Güç",en:"Power"},expr:`Pₘ = ${R(Qtop)}·${R(vel,3)}/(60·75·1,36·${v.ho})`,res:R(P,2),u:"kW"}]};}},

{ id:"elevator", grp:{tr:"Konveyör & Taşıma",en:"Conveying & Handling"}, dia:"elevator", sf:1.4, eta:0.96,
  name:{tr:"Kovalı elevatör",en:"Bucket elevator"}, series:{tr:"Helis-konik + geri dönüşsüz",en:"Helical-bevel + backstop"},
  formula:{tr:"Pₒ = k·Q·H/367 ,  n = 60·v/(π·D)", en:"Pₒ = k·Q·H/367 ,  n = 60·v/(π·D)"},
  vars:[V("Q","Kapasite Q","Capacity Q","t/h",50,1),V("H","Kaldırma yüksekliği H","Lift height H","m",20,0.5),
        V("v","Hız v","Speed v","m/s",1.5,0.1),V("D","Kafa tamburu Ø","Head pulley Ø","mm",500,5),V("k","Dolum faktörü k","Fill factor k","",1.25,0.05)],
  calc:v=>{const P=v.k*v.Q*v.H/367;const D=v.D/1000;const n=60*v.v/(Math.PI*D);const MT=n>0?9550*P/n:NaN;
    return {MT,n,Pout:P,steps:[
      {lab:{tr:"Çıkış gücü",en:"Output power"},expr:`Pₒ = ${v.k}·${v.Q}·${v.H}/367`,res:R(P,2),u:"kW"},
      {lab:{tr:"Kafa tamburu devri",en:"Head pulley speed"},expr:`n = 60·${v.v}/(π·${R(D,3)})`,res:R(n,1),u:"d/dk"},
      {lab:{tr:"Çıkış momenti",en:"Output moment"},expr:`Mᴛ = 9550·${R(P,2)}/${R(n,1)}`,res:R(MT),u:"Nm"}]};}},

{ id:"chain", grp:{tr:"Konveyör & Taşıma",en:"Conveying & Handling"}, dia:"chain", sf:1.5, eta:0.95,
  name:{tr:"Zincirli / sıyırıcı konveyör",en:"Chain / drag conveyor"}, series:{tr:"İRK Serisi (helis-konik)",en:"İRK series (helical-bevel)"},
  formula:{tr:"Mᴛ = f·m·g·r ,  n = v/(π·D)", en:"Mᴛ = f·m·g·r ,  n = v/(π·D)"},
  vars:[V("m","Hareketli kütle m","Moving mass m","kg",8000,100),V("D","Zincir dişlisi Ø","Sprocket Ø","mm",250,5),
        V("v","Zincir hızı v","Chain speed v","m/min",20,1),V("f","Sürtünme katsayısı f","Friction coeff. f","",0.30,0.05)],
  calc:v=>{const r=v.D/2000;const MT=v.f*v.m*G*r;const D=v.D/1000;const n=v.v/(Math.PI*D);
    return {MT,n,steps:[
      {lab:{tr:"Dişli yarıçapı",en:"Sprocket radius"},expr:`r = ${v.D}/2000`,res:R(r,3),u:"m"},
      {lab:{tr:"Çıkış momenti",en:"Output moment"},expr:`Mᴛ = ${v.f}·${v.m}·9,81·${R(r,3)}`,res:R(MT),u:"Nm"},
      {lab:{tr:"Çıkış devri",en:"Output speed"},expr:`n = ${v.v}/(π·${R(D,3)})`,res:R(n,1),u:"d/dk"}]};}},

{ id:"feeder", grp:{tr:"Konveyör & Taşıma",en:"Conveying & Handling"}, dia:"vib", sf:1.75, eta:0.95,
  name:{tr:"Titreşimli besleyici",en:"Vibrating feeder"}, series:{tr:"Mil üstü redüktörlü motor",en:"Shaft-mounted geared motor"},
  formula:{tr:"ω = 2π·n/60 ,  Pₒ = k·m·A²·ω³/1000", en:"ω = 2π·n/60 ,  Pₒ = k·m·A²·ω³/1000"},
  vars:[V("m","Titreşen kütle m","Vibrating mass m","kg",300,10),V("A","Genlik A","Amplitude A","mm",4,0.5),
        V("n","Ekssantrik devri","Exciter speed","rpm",750,10),V("k","Güç faktörü k","Power factor k","",0.40,0.05)],
  calc:v=>{const w=2*Math.PI*v.n/60;const A=v.A/1000;const P=v.k*v.m*A*A*w*w*w/1000;const MT=v.n>0?9550*P/v.n:NaN;
    return {MT,n:v.n,Pout:P,steps:[
      {lab:{tr:"Açısal hız",en:"Angular speed"},expr:`ω = 2π·${v.n}/60`,res:R(w,1),u:"rad/s"},
      {lab:{tr:"Çıkış gücü",en:"Output power"},expr:`Pₒ = ${v.k}·${v.m}·${A}²·${R(w,1)}³/1000`,res:R(P,2),u:"kW"},
      {lab:{tr:"Çıkış momenti",en:"Output moment"},expr:`Mᴛ = 9550·${R(P,2)}/${v.n}`,res:R(MT),u:"Nm"}]};}},

/* ---------- Kaldırma & Vinç ---------- */
{ id:"hoist", grp:{tr:"Kaldırma & Vinç",en:"Lifting & Crane"}, dia:"hoist", sf:1.5, eta:0.97,
  name:{tr:"Vinç kaldırma (tambur + palanga)",en:"Crane hoist (drum + falls)"}, series:{tr:"İRC Serisi (kaldırma)",en:"İRC series (hoist)"},
  formula:{tr:"Mᴛ = m·g·r/z ,  n = 9,55·v·z/r ,  Pm = Mᴛ·n/(9550·η)", en:"Mᴛ = m·g·r/z ,  n = 9.55·v·z/r ,  Pm = Mᴛ·n/(9550·η)"},
  vars:[V("m","Kaldırılacak yük m","Load m","kg",2000,50),V("D","Tambur çapı Ø","Drum Ø","mm",300,10),
        V("v","Kaldırma hızı v","Lift speed v","m/min",10,0.5),V("z","Palanga kat sayısı z","Rope falls z","",1,1)],
  calc:v=>{const r=v.D/2000;const z=Math.max(1,v.z);const MT=v.m*G*r/z;const vms=v.v/60;const n=9.55*vms*z/r;
    return {MT,n,steps:[
      {lab:{tr:"Tambur yarıçapı",en:"Drum radius"},expr:`r = ${v.D}/2000`,res:R(r,3),u:"m"},
      {lab:{tr:"Palanga kat sayısı",en:"Rope falls"},expr:`z`,res:z,u:""},
      {lab:{tr:"Tambur momenti",en:"Drum moment"},expr:`Mᴛ = ${v.m}·9,81·${R(r,3)}/${z}`,res:R(MT),u:"Nm"},
      {lab:{tr:"Tambur devri",en:"Drum speed"},expr:`n = 9,55·${R(vms,3)}·${z}/${R(r,3)}`,res:R(n,1),u:"d/dk"}]};}},

{ id:"pulley", grp:{tr:"Kaldırma & Vinç",en:"Lifting & Crane"}, dia:"pulley", sf:1.5, eta:0.95,
  name:{tr:"Palangalı kaldırma",en:"Pulley / block-and-tackle hoist"}, series:{tr:"İRC Serisi (kaldırma)",en:"İRC series (hoist)"},
  formula:{tr:"Mᴛ = m·g·r/z ,  n = 9,55·v·z/r", en:"Mᴛ = m·g·r/z ,  n = 9.55·v·z/r"},
  vars:[V("m","Kaldırılacak yük m","Load m","kg",5000,100),V("D","Tambur çapı Ø","Drum Ø","mm",400,10),
        V("v","Kaldırma hızı v","Lift speed v","m/min",8,0.5),V("z","Palanga kat sayısı z","Rope falls z","",2,1),V("re","Palanga verimi","Reeving eff.","",0.95,0.01)],
  calc:v=>{const r=v.D/2000;const z=Math.max(1,v.z);const MT=v.m*G*r/z/v.re;const vms=v.v/60;const n=9.55*vms*z/r;
    return {MT,n,steps:[
      {lab:{tr:"Tambur yarıçapı",en:"Drum radius"},expr:`r = ${v.D}/2000`,res:R(r,3),u:"m"},
      {lab:{tr:"Tambur momenti",en:"Drum moment"},expr:`Mᴛ = ${v.m}·9,81·${R(r,3)}/(${z}·${v.re})`,res:R(MT),u:"Nm"},
      {lab:{tr:"Tambur devri",en:"Drum speed"},expr:`n = 9,55·${R(vms,3)}·${z}/${R(r,3)}`,res:R(n,1),u:"d/dk"}]};}},

{ id:"travel", grp:{tr:"Kaldırma & Vinç",en:"Lifting & Crane"}, dia:"travel", sf:1.25, eta:0.95,
  name:{tr:"Yürütme (köprü/araba)",en:"Travel (bridge / trolley)"}, series:{tr:"Yürütme redüktörlü motor",en:"Travel geared motor"},
  formula:{tr:"Mᴛ = [Q·f + μ·Q·(d/2)]·g ,  v = π·D·n/60000", en:"Mᴛ = [Q·f + μ·Q·(d/2)]·g ,  v = π·D·n/60000"},
  vars:[V("Q","Yük Q","Load Q","kg",5000,100),V("D","Tekerlek çapı Ø","Wheel Ø","mm",500,10),V("d","Rulman çapı Ø","Bearing Ø","mm",100,5),
        V("v","Yürütme hızı v","Travel speed v","m/s",1.5,0.1),V("f","Yuvarlanma katsayısı f","Rolling coeff. f","",0.002,0.001),V("mu","Rulman sürtünmesi μ","Bearing friction μ","",0.008,0.001)],
  calc:v=>{const MTkgm=v.Q*v.f + v.mu*v.Q*(v.d/2000);const MT=MTkgm*G;const D=v.D;const n=60000*v.v/(Math.PI*D);
    return {MT,n,steps:[
      {lab:{tr:"Tekerlek momenti",en:"Wheel moment"},expr:`Mᴛ = [${v.Q}·${v.f}+${v.mu}·${v.Q}·${R(v.d/2000,3)}]·9,81`,res:R(MT),u:"Nm"},
      {lab:{tr:"Tekerlek devri",en:"Wheel speed"},expr:`n = 60000·${v.v}/(π·${D})`,res:R(n,1),u:"d/dk"}]};}},

{ id:"slew", grp:{tr:"Kaldırma & Vinç",en:"Lifting & Crane"}, dia:"slew", sf:1.5, eta:0.94,
  name:{tr:"Döner (slewing) tahrik",en:"Slewing drive"}, series:{tr:"Helis-konik redüktörlü motor",en:"Helical-bevel geared motor"},
  formula:{tr:"J = m·r² ,  α = (2π·n/60)/t ,  Mᴛ = J·α + Tf", en:"J = m·r² ,  α = (2π·n/60)/t ,  Mᴛ = J·α + Tf"},
  vars:[V("m","Dönen kütle m","Slewing mass m","kg",5000,100),V("r","Kütle yarıçapı r","Mass radius r","m",3,0.1),
        V("n","Dönme devri","Slew speed","rpm",1.5,0.1),V("t","Hızlanma süresi t","Accel time t","s",5,0.5),V("Tf","Sürtünme momenti Tf","Friction torque Tf","Nm",500,10)],
  calc:v=>{const J=v.m*v.r*v.r;const w=2*Math.PI*v.n/60;const al=v.t>0?w/v.t:0;const MT=J*al+v.Tf;
    return {MT,n:v.n,steps:[
      {lab:{tr:"Atalet momenti",en:"Inertia"},expr:`J = ${v.m}·${v.r}²`,res:R(J),u:"kg·m²"},
      {lab:{tr:"Açısal ivme",en:"Ang. accel"},expr:`α = (2π·${v.n}/60)/${v.t}`,res:R(al,3),u:"rad/s²"},
      {lab:{tr:"Çıkış momenti",en:"Output moment"},expr:`Mᴛ = ${R(J)}·${R(al,3)}+${v.Tf}`,res:R(MT),u:"Nm"}]};}},

{ id:"lift", grp:{tr:"Kaldırma & Vinç",en:"Lifting & Crane"}, dia:"lift", sf:1.75, eta:0.95,
  name:{tr:"Asansör (halatlı)",en:"Passenger lift (traction)"}, series:{tr:"Sertifikalı asansör tahriki",en:"Certified lift drive"},
  formula:{tr:"F = Q·(1−b)·g ,  Pₒ = F·v/1000 ,  n = 60·rf·v/(π·D)", en:"F = Q·(1−b)·g ,  Pₒ = F·v/1000 ,  n = 60·rf·v/(π·D)"},
  vars:[V("Q","Kabin yükü Q","Car load Q","kg",1000,50),V("v","Hız v","Speed v","m/s",1.0,0.1),V("b","Denge oranı b","Balance b","",0.5,0.05),
        V("D","Kasnak çapı Ø","Sheave Ø","mm",600,10),V("rf","Askı oranı (1/2)","Roping factor (1/2)","",1,1)],
  calc:v=>{const F=v.Q*(1-v.b)*G;const P=F*v.v/1000;const D=v.D/1000;const rf=Math.max(1,v.rf);const n=60*rf*v.v/(Math.PI*D);const MT=n>0?9550*P/n:NaN;
    return {MT,n,Pout:P,steps:[
      {lab:{tr:"Dengesiz kuvvet",en:"Out-of-balance force"},expr:`F = ${v.Q}·(1−${v.b})·9,81`,res:R(F),u:"N"},
      {lab:{tr:"Çıkış gücü",en:"Output power"},expr:`Pₒ = ${R(F)}·${v.v}/1000`,res:R(P,2),u:"kW"},
      {lab:{tr:"Kasnak devri",en:"Sheave speed"},expr:`n = 60·${rf}·${v.v}/(π·${R(D,3)})`,res:R(n,1),u:"d/dk"}]};}},

/* ---------- Karıştırma & Proses ---------- */
{ id:"mixer_b", grp:{tr:"Karıştırma & Proses",en:"Mixing & Process"}, dia:"mixer", sf:1.5, eta:0.95,
  name:{tr:"Karıştırıcı — kanat yöntemi",en:"Agitator — blade method"}, series:{tr:"Helis redüktörlü motor (karıştırıcı)",en:"Helical geared motor (agitator)"},
  formula:{tr:"Mₖ = (Ød/2)·b·kᵢ·ρ·10 ,  Mᴛ = ΣMₖ ,  Pm = Mᴛ·n/(9550·η)", en:"Mₖ = (Ød/2)·b·kᵢ·ρ·10 ,  Mᴛ = ΣMₖ ,  Pm = Mᴛ·n/(9550·η)"},
  vars:[V("Dd","Pervane çapı Ød","Impeller Ø","mm",1500,10),V("b","Pervane genişliği b","Blade width b","mm",100,5),
        V("k1","1. kanat sıvı yük. k₁","Blade-1 liquid h. k₁","mm",3500,50),V("k2","2. kanat k₂","Blade-2 k₂","mm",2500,50),
        V("k3","3. kanat k₃","Blade-3 k₃","mm",1500,50),V("n","Mil devri n","Shaft speed n","rpm",20,1),V("ro","Yoğunluk ρ","Density ρ","gr/cm³",1.1,0.05)],
  calc:v=>{const rd=v.Dd/2000, bb=v.b/1000, rho=v.ro*1000;
    const blade=k=>k>0?rd*bb*(k/1000)*rho*10:0;
    const M1=blade(v.k1),M2=blade(v.k2),M3=blade(v.k3);const MT=M1+M2+M3;
    return {MT,n:v.n,steps:[
      {lab:{tr:"1. kanat momenti",en:"Blade-1 moment"},expr:`M₁ = ${R(rd,3)}·${R(bb,3)}·${v.k1/1000}·${rho}·10`,res:R(M1),u:"Nm"},
      {lab:{tr:"2. kanat momenti",en:"Blade-2 moment"},expr:`M₂`,res:R(M2),u:"Nm"},
      {lab:{tr:"3. kanat momenti",en:"Blade-3 moment"},expr:`M₃`,res:R(M3),u:"Nm"},
      {lab:{tr:"Toplam moment",en:"Total moment"},expr:`Mᴛ = ${R(M1)}+${R(M2)}+${R(M3)}`,res:R(MT),u:"Nm"}]};}},

{ id:"mixer_np", grp:{tr:"Karıştırma & Proses",en:"Mixing & Process"}, dia:"mixer", sf:1.5, eta:0.96,
  name:{tr:"Karıştırıcı — güç sayısı (Np)",en:"Agitator — power number (Np)"}, series:{tr:"Helis redüktörlü motor",en:"Helical geared motor"},
  formula:{tr:"N = n/60 ,  Pₒ = Np·ρ·N³·D⁵/1000  (türbülanslı)", en:"N = n/60 ,  Pₒ = Np·ρ·N³·D⁵/1000  (turbulent)"},
  vars:[V("Np","Güç sayısı Np","Power number Np","",1.5,0.1),V("ro","Yoğunluk ρ","Density ρ","kg/m³",1000,10),
        V("D","Pervane çapı Ø","Impeller Ø","mm",500,10),V("n","Mil devri n","Shaft speed n","rpm",60,1)],
  calc:v=>{const N=v.n/60;const D=v.D/1000;const P=v.Np*v.ro*N*N*N*Math.pow(D,5)/1000;const MT=v.n>0?9550*P/v.n:NaN;
    return {MT,n:v.n,Pout:P,steps:[
      {lab:{tr:"Devir (1/s)",en:"Rev/s"},expr:`N = ${v.n}/60`,res:R(N,3),u:"1/s"},
      {lab:{tr:"Çıkış gücü",en:"Output power"},expr:`Pₒ = ${v.Np}·${v.ro}·${R(N,3)}³·${R(D,3)}⁵/1000`,res:R(P,2),u:"kW"},
      {lab:{tr:"Çıkış momenti",en:"Output moment"},expr:`Mᴛ = 9550·${R(P,2)}/${v.n}`,res:R(MT),u:"Nm"}]};}},

{ id:"kiln", grp:{tr:"Karıştırma & Proses",en:"Mixing & Process"}, dia:"kiln", sf:1.5, eta:0.95,
  name:{tr:"Döner fırın / kurutma tamburu",en:"Rotary kiln / drying drum"}, series:{tr:"Helis-konik redüktörlü motor",en:"Helical-bevel geared motor"},
  formula:{tr:"Mᴛ = (1+k)·m·g·(D/2)·e ,  Pm = Mᴛ·n/(9550·η)", en:"Mᴛ = (1+k)·m·g·(D/2)·e ,  Pm = Mᴛ·n/(9550·η)"},
  vars:[V("D","İç çap Ø","Internal Ø","mm",3000,50),V("m","Dönen yük m","Rotating load m","kg",20000,500),
        V("e","Eksantriklik e","Eccentricity e","",0.35,0.01),V("n","Dönme devri n","Rotation speed n","rpm",2,0.1),V("k","Sürtünme payı k","Friction allow. k","%",20,5)],
  calc:v=>{const D=v.D/1000;const MT=(1+v.k/100)*v.m*G*(D/2)*v.e;
    return {MT,n:v.n,steps:[
      {lab:{tr:"Çıkış momenti",en:"Output moment"},expr:`Mᴛ = ${1+v.k/100}·${v.m}·9,81·${R(D/2,3)}·${v.e}`,res:R(MT),u:"Nm"}]};}},

{ id:"extruder", grp:{tr:"Karıştırma & Proses",en:"Mixing & Process"}, dia:"extruder", sf:1.5, eta:0.96,
  name:{tr:"Ekstruder (vida)",en:"Extruder (screw)"}, series:{tr:"Helis redüktörlü motor (yüksek eksenel)",en:"Helical geared motor (high axial)"},
  formula:{tr:"Pₒ = SME·Q ,  Mᴛ = 9550·Pₒ/n", en:"Pₒ = SME·Q ,  Mᴛ = 9550·Pₒ/n"},
  vars:[V("Q","Debi Q","Throughput Q","kg/h",200,5),V("SME","Özgül mek. enerji","Specific mech. energy","kWh/kg",0.20,0.01),V("n","Vida devri n","Screw speed n","rpm",100,5)],
  calc:v=>{const P=v.SME*v.Q;const MT=v.n>0?9550*P/v.n:NaN;
    return {MT,n:v.n,Pout:P,steps:[
      {lab:{tr:"Çıkış gücü",en:"Output power"},expr:`Pₒ = ${v.SME}·${v.Q}`,res:R(P,2),u:"kW"},
      {lab:{tr:"Çıkış momenti",en:"Output moment"},expr:`Mᴛ = 9550·${R(P,2)}/${v.n}`,res:R(MT),u:"Nm"}]};}},

/* ---------- Değirmen & Öğütme ---------- */
{ id:"roller", grp:{tr:"Değirmen & Öğütme",en:"Milling & Grinding"}, dia:"mill", sf:1.5, eta:0.96,
  name:{tr:"Valsli değirmen (un)",en:"Roller mill (flour)"}, series:{tr:"Helis redüktörlü motor",en:"Helical geared motor"},
  formula:{tr:"Pₒ = E·Q ,  Mᴛ = 9550·Pₒ/n", en:"Pₒ = E·Q ,  Mᴛ = 9550·Pₒ/n"},
  vars:[V("Q","Kapasite Q","Capacity Q","t/h",10,0.5),V("E","Özgül enerji E","Specific energy E","kWh/t",10,0.5),V("n","Çıkış devri n","Output speed n","rpm",300,5)],
  calc:v=>{const P=v.E*v.Q;const MT=v.n>0?9550*P/v.n:NaN;
    return {MT,n:v.n,Pout:P,steps:[
      {lab:{tr:"Çıkış gücü",en:"Output power"},expr:`Pₒ = ${v.E}·${v.Q}`,res:R(P,2),u:"kW"},
      {lab:{tr:"Çıkış momenti",en:"Output moment"},expr:`Mᴛ = 9550·${R(P,2)}/${v.n}`,res:R(MT),u:"Nm"}]};}},

{ id:"hammer", grp:{tr:"Değirmen & Öğütme",en:"Milling & Grinding"}, dia:"mill", sf:1.75, eta:0.96,
  name:{tr:"Çekiçli değirmen",en:"Hammer mill"}, series:{tr:"Helis redüktörlü motor (darbe)",en:"Helical geared motor (shock)"},
  formula:{tr:"Pₒ = E·Q ,  Mᴛ = 9550·Pₒ/n", en:"Pₒ = E·Q ,  Mᴛ = 9550·Pₒ/n"},
  vars:[V("Q","Kapasite Q","Capacity Q","t/h",5,0.5),V("E","Özgül enerji E","Specific energy E","kWh/t",15,0.5),V("n","Çıkış devri n","Output speed n","rpm",1500,10)],
  calc:v=>{const P=v.E*v.Q;const MT=v.n>0?9550*P/v.n:NaN;
    return {MT,n:v.n,Pout:P,steps:[
      {lab:{tr:"Çıkış gücü",en:"Output power"},expr:`Pₒ = ${v.E}·${v.Q}`,res:R(P,2),u:"kW"},
      {lab:{tr:"Çıkış momenti",en:"Output moment"},expr:`Mᴛ = 9550·${R(P,2)}/${v.n}`,res:R(MT),u:"Nm"}]};}},

{ id:"ballmill", grp:{tr:"Değirmen & Öğütme",en:"Milling & Grinding"}, dia:"ball", sf:1.75, eta:0.95,
  name:{tr:"Bilyalı değirmen (Bond)",en:"Ball mill (Bond)"}, series:{tr:"Değirmen tipi redüktör",en:"Mill-duty geared drive"},
  formula:{tr:"E = 10·Wi·(1/√P₈₀ − 1/√F₈₀) ,  Pₒ = E·Q", en:"E = 10·Wi·(1/√P₈₀ − 1/√F₈₀) ,  Pₒ = E·Q"},
  vars:[V("Q","Kapasite Q","Capacity Q","t/h",20,1),V("Wi","İş indeksi Wi","Work index Wi","kWh/t",13,0.5),
        V("F","Besleme F₈₀","Feed F₈₀","µm",10000,100),V("Pp","Ürün P₈₀","Product P₈₀","µm",100,5),V("n","Değirmen devri n","Mill speed n","rpm",18,0.5)],
  calc:v=>{const E=10*v.Wi*(1/Math.sqrt(v.Pp)-1/Math.sqrt(v.F));const P=E*v.Q;const MT=v.n>0?9550*P/v.n:NaN;
    return {MT,n:v.n,Pout:P,steps:[
      {lab:{tr:"Özgül enerji (Bond)",en:"Specific energy (Bond)"},expr:`E = 10·${v.Wi}·(1/√${v.Pp}−1/√${v.F})`,res:R(E,2),u:"kWh/t"},
      {lab:{tr:"Çıkış gücü",en:"Output power"},expr:`Pₒ = ${R(E,2)}·${v.Q}`,res:R(P,2),u:"kW"},
      {lab:{tr:"Çıkış momenti",en:"Output moment"},expr:`Mᴛ = 9550·${R(P,2)}/${v.n}`,res:R(MT),u:"Nm"}]};}},

{ id:"sifter", grp:{tr:"Değirmen & Öğütme",en:"Milling & Grinding"}, dia:"sifter", sf:1.5, eta:0.96,
  name:{tr:"Elek / plansifter",en:"Sifter / plansifter"}, series:{tr:"Helis redüktörlü motor",en:"Helical geared motor"},
  formula:{tr:"ω = 2π·n/60 ,  Pₒ = k·m·r²·ω³/1000", en:"ω = 2π·n/60 ,  Pₒ = k·m·r²·ω³/1000"},
  vars:[V("m","Salınan kütle m","Gyrating mass m","kg",300,10),V("r","Salınım yarıçapı r","Gyration throw r","mm",40,1),
        V("n","Devir n","Speed n","rpm",220,5),V("k","Sönüm faktörü k","Damping factor k","",0.35,0.05)],
  calc:v=>{const w=2*Math.PI*v.n/60;const r=v.r/1000;const P=v.k*v.m*r*r*w*w*w/1000;const MT=v.n>0?9550*P/v.n:NaN;
    return {MT,n:v.n,Pout:P,steps:[
      {lab:{tr:"Açısal hız",en:"Angular speed"},expr:`ω = 2π·${v.n}/60`,res:R(w,1),u:"rad/s"},
      {lab:{tr:"Çıkış gücü",en:"Output power"},expr:`Pₒ = ${v.k}·${v.m}·${r}²·${R(w,1)}³/1000`,res:R(P,2),u:"kW"},
      {lab:{tr:"Çıkış momenti",en:"Output moment"},expr:`Mᴛ = 9550·${R(P,2)}/${v.n}`,res:R(MT),u:"Nm"}]};}},

{ id:"pellet", grp:{tr:"Değirmen & Öğütme",en:"Milling & Grinding"}, dia:"mill", sf:1.75, eta:0.95,
  name:{tr:"Pelet değirmeni",en:"Pellet mill"}, series:{tr:"Helis-konik redüktör (ağır)",en:"Helical-bevel (heavy)"},
  formula:{tr:"Pₒ = E·Q ,  Mᴛ = 9550·Pₒ/n", en:"Pₒ = E·Q ,  Mᴛ = 9550·Pₒ/n"},
  vars:[V("Q","Kapasite Q","Capacity Q","t/h",8,0.5),V("E","Özgül enerji E","Specific energy E","kWh/t",45,1),V("n","Çıkış devri n","Output speed n","rpm",250,5)],
  calc:v=>{const P=v.E*v.Q;const MT=v.n>0?9550*P/v.n:NaN;
    return {MT,n:v.n,Pout:P,steps:[
      {lab:{tr:"Çıkış gücü",en:"Output power"},expr:`Pₒ = ${v.E}·${v.Q}`,res:R(P,2),u:"kW"},
      {lab:{tr:"Çıkış momenti",en:"Output moment"},expr:`Mᴛ = 9550·${R(P,2)}/${v.n}`,res:R(MT),u:"Nm"}]};}},

/* ---------- Kırma & Titreşim ---------- */
{ id:"crusher", grp:{tr:"Kırma & Titreşim",en:"Crushing & Vibrating"}, dia:"mill", sf:1.75, eta:0.95,
  name:{tr:"Kırıcı (taş / cevher)",en:"Crusher (stone / ore)"}, series:{tr:"Helis-konik redüktör (ağır)",en:"Helical-bevel (heavy duty)"},
  formula:{tr:"Pₒ = E·Q ,  Mᴛ = 9550·Pₒ/n", en:"Pₒ = E·Q ,  Mᴛ = 9550·Pₒ/n"},
  vars:[V("Q","Kapasite Q","Capacity Q","t/h",50,1),V("E","Özgül enerji E","Specific energy E","kWh/t",2,0.5),V("n","Çıkış devri n","Output speed n","rpm",200,5)],
  calc:v=>{const P=v.E*v.Q;const MT=v.n>0?9550*P/v.n:NaN;
    return {MT,n:v.n,Pout:P,steps:[
      {lab:{tr:"Çıkış gücü",en:"Output power"},expr:`Pₒ = ${v.E}·${v.Q}`,res:R(P,2),u:"kW"},
      {lab:{tr:"Çıkış momenti",en:"Output moment"},expr:`Mᴛ = 9550·${R(P,2)}/${v.n}`,res:R(MT),u:"Nm"}]};}},

{ id:"vibscreen", grp:{tr:"Kırma & Titreşim",en:"Crushing & Vibrating"}, dia:"vib", sf:1.75, eta:0.95,
  name:{tr:"Titreşimli elek",en:"Vibrating screen"}, series:{tr:"Mil üstü redüktörlü motor",en:"Shaft-mounted geared motor"},
  formula:{tr:"ω = 2π·n/60 ,  Pₒ = k·m·A²·ω³/1000", en:"ω = 2π·n/60 ,  Pₒ = k·m·A²·ω³/1000"},
  vars:[V("m","Titreşen kütle m","Vibrating mass m","kg",800,10),V("A","Genlik A","Amplitude A","mm",5,0.5),
        V("n","Ekssantrik devri","Exciter speed","rpm",900,10),V("k","Güç faktörü k","Power factor k","",0.5,0.05)],
  calc:v=>{const w=2*Math.PI*v.n/60;const A=v.A/1000;const P=v.k*v.m*A*A*w*w*w/1000;const MT=v.n>0?9550*P/v.n:NaN;
    return {MT,n:v.n,Pout:P,steps:[
      {lab:{tr:"Açısal hız",en:"Angular speed"},expr:`ω = 2π·${v.n}/60`,res:R(w,1),u:"rad/s"},
      {lab:{tr:"Çıkış gücü",en:"Output power"},expr:`Pₒ = ${v.k}·${v.m}·${A}²·${R(w,1)}³/1000`,res:R(P,2),u:"kW"},
      {lab:{tr:"Çıkış momenti",en:"Output moment"},expr:`Mᴛ = 9550·${R(P,2)}/${v.n}`,res:R(MT),u:"Nm"}]};}},

{ id:"rotable", grp:{tr:"Kırma & Titreşim",en:"Crushing & Vibrating"}, dia:"slew", sf:1.5, eta:0.95,
  name:{tr:"Döner tabla / turntable",en:"Rotary table / turntable"}, series:{tr:"Helis-konik redüktörlü motor",en:"Helical-bevel geared motor"},
  formula:{tr:"J = 0,5·m·r² ,  α = (2π·n/60)/t ,  Mᴛ = J·α + Tf", en:"J = 0.5·m·r² ,  α = (2π·n/60)/t ,  Mᴛ = J·α + Tf"},
  vars:[V("m","Tabla + yük m","Table + load m","kg",2000,50),V("r","Yarıçap r","Radius r","mm",800,10),
        V("n","Çalışma devri n","Operating speed n","rpm",5,0.5),V("t","Hızlanma süresi t","Accel time t","s",3,0.5),V("Tf","Sürtünme momenti Tf","Friction torque Tf","Nm",200,10)],
  calc:v=>{const r=v.r/1000;const J=0.5*v.m*r*r;const w=2*Math.PI*v.n/60;const al=v.t>0?w/v.t:0;const MT=J*al+v.Tf;
    return {MT,n:v.n,steps:[
      {lab:{tr:"Atalet momenti",en:"Inertia"},expr:`J = 0,5·${v.m}·${R(r,3)}²`,res:R(J),u:"kg·m²"},
      {lab:{tr:"Açısal ivme",en:"Ang. accel"},expr:`α = (2π·${v.n}/60)/${v.t}`,res:R(al,3),u:"rad/s²"},
      {lab:{tr:"Çıkış momenti",en:"Output moment"},expr:`Mᴛ = ${R(J)}·${R(al,3)}+${v.Tf}`,res:R(MT),u:"Nm"}]};}},

/* ---------- Pompa & Fan ---------- */
{ id:"pump", grp:{tr:"Pompa & Fan",en:"Pumps & Fans"}, dia:"pump", sf:1.25, eta:0.97,
  name:{tr:"Santrifüj pompa",en:"Centrifugal pump"}, series:{tr:"Helis redüktörlü motor",en:"Helical geared motor"},
  formula:{tr:"Pₒ = Q·H·SG/(367·ηp) ,  Mᴛ = 9550·Pₒ/n", en:"Pₒ = Q·H·SG/(367·ηp) ,  Mᴛ = 9550·Pₒ/n"},
  vars:[V("Q","Debi Q","Flow Q","m³/h",50,1),V("H","Basma yüksekliği H","Head H","m",30,1),V("SG","Özgül ağırlık SG","Specific gravity SG","",1.0,0.05),
        V("pe","Pompa verimi ηp","Pump eff. ηp","",0.70,0.01),V("n","Pompa devri n","Pump speed n","rpm",1450,10)],
  calc:v=>{const P=v.pe>0?v.Q*v.H*v.SG/(367*v.pe):NaN;const MT=v.n>0?9550*P/v.n:NaN;
    return {MT,n:v.n,Pout:P,steps:[
      {lab:{tr:"Çıkış gücü",en:"Output power"},expr:`Pₒ = ${v.Q}·${v.H}·${v.SG}/(367·${v.pe})`,res:R(P,2),u:"kW"},
      {lab:{tr:"Çıkış momenti",en:"Output moment"},expr:`Mᴛ = 9550·${R(P,2)}/${v.n}`,res:R(MT),u:"Nm"}]};}},

{ id:"recip", grp:{tr:"Pompa & Fan",en:"Pumps & Fans"}, dia:"pump", sf:1.5, eta:0.96,
  name:{tr:"Pistonlu / pozitif deplasmanlı pompa",en:"Reciprocating / PD pump"}, series:{tr:"Helis redüktörlü motor (darbe)",en:"Helical geared motor (shock)"},
  formula:{tr:"Pₒ = Q·H·SG/(367·ηp) ,  Mᴛ = 9550·Pₒ/n", en:"Pₒ = Q·H·SG/(367·ηp) ,  Mᴛ = 9550·Pₒ/n"},
  vars:[V("Q","Debi Q","Flow Q","m³/h",20,1),V("H","Basma yüksekliği H","Head H","m",60,1),V("SG","Özgül ağırlık SG","Specific gravity SG","",1.0,0.05),
        V("pe","Pompa verimi ηp","Pump eff. ηp","",0.85,0.01),V("n","Pompa devri n","Pump speed n","rpm",300,5)],
  calc:v=>{const P=v.pe>0?v.Q*v.H*v.SG/(367*v.pe):NaN;const MT=v.n>0?9550*P/v.n:NaN;
    return {MT,n:v.n,Pout:P,steps:[
      {lab:{tr:"Çıkış gücü",en:"Output power"},expr:`Pₒ = ${v.Q}·${v.H}·${v.SG}/(367·${v.pe})`,res:R(P,2),u:"kW"},
      {lab:{tr:"Çıkış momenti",en:"Output moment"},expr:`Mᴛ = 9550·${R(P,2)}/${v.n}`,res:R(MT),u:"Nm"}]};}},

{ id:"fan", grp:{tr:"Pompa & Fan",en:"Pumps & Fans"}, dia:"fan", sf:1.25, eta:0.97,
  name:{tr:"Santrifüj fan / körük",en:"Centrifugal fan / blower"}, series:{tr:"Helis redüktörlü motor",en:"Helical geared motor"},
  formula:{tr:"Pₒ = (Q/3600)·Δp/(1000·ηf) ,  Mᴛ = 9550·Pₒ/n", en:"Pₒ = (Q/3600)·Δp/(1000·ηf) ,  Mᴛ = 9550·Pₒ/n"},
  vars:[V("Q","Hava debisi Q","Air flow Q","m³/h",5000,100),V("dp","Basınç artışı Δp","Pressure rise Δp","Pa",1000,50),
        V("fe","Fan verimi ηf","Fan eff. ηf","",0.65,0.01),V("n","Fan devri n","Fan speed n","rpm",1450,10)],
  calc:v=>{const P=v.fe>0?(v.Q/3600)*v.dp/1000/v.fe:NaN;const MT=v.n>0?9550*P/v.n:NaN;
    return {MT,n:v.n,Pout:P,steps:[
      {lab:{tr:"Çıkış gücü",en:"Output power"},expr:`Pₒ = (${v.Q}/3600)·${v.dp}/(1000·${v.fe})`,res:R(P,2),u:"kW"},
      {lab:{tr:"Çıkış momenti",en:"Output moment"},expr:`Mᴛ = 9550·${R(P,2)}/${v.n}`,res:R(MT),u:"Nm"}]};}},
];

/* ================= UI text ================= */
const UI = {
 tagline:{tr:"Uygulamaya özel redüktör seçim aracı · çevrimdışı çalışır",en:"Per-application gearbox selection tool · works offline"},
 pickApp:{tr:"Uygulama",en:"Application"},
 diagram:{tr:"Şema",en:"Diagram"},
 formula:{tr:"Formül",en:"Formula"},
 inputs:{tr:"Girdiler",en:"Inputs"},
 steps:{tr:"Hesap adımları",en:"Calculation steps"},
 result:{tr:"Sonuç",en:"Result"},
 motorRpm:{tr:"Motor devri n₁",en:"Motor speed n₁"},
 eta:{tr:"Redüktör verimi η",en:"Gearbox efficiency η"},
 sf:{tr:"Servis faktörü Sf",en:"Service factor Sf"},
 MT:{tr:"Çıkış momenti Mᴛ",en:"Output moment Mᴛ"},
 nout:{tr:"Çıkış devri n",en:"Output speed n"},
 ratio:{tr:"Tahvil i",en:"Ratio i"},
 motor:{tr:"Motor gücü",en:"Motor power"},
 Mn:{tr:"Gerekli nominal moment",en:"Required nominal moment"},
 rec:{tr:"Önerilen İ-MAK ürünü",en:"Suggested I-MAK product"},
 recline:{tr:"Nominal momenti Mₙ ≥ %s Nm ve tahvili i ≈ %r olan bir İ-MAK redüktörü seçin.",en:"Choose an I-MAK unit with nominal moment Mₙ ≥ %s Nm at ratio i ≈ %r."},
 copy:{tr:"Özeti kopyala",en:"Copy summary"},
 print:{tr:"PDF / yazdır",en:"Save PDF / print"},
 reset:{tr:"Sıfırla",en:"Reset"},
 disc:{tr:"Uygulamaya özel seçim kılavuzu (İ-MAK formülleri + standart tahrik hesapları). Süreç sonuçları saha tahminidir — nihai seçimi İ-MAK kataloğu (nominal moment, tahvil, radyal yük, termik güç) ile doğrulayın.",
       en:"Per-application selection guide (I-MAK formulas + standard drive maths). Process results are field estimates — confirm the final choice against the I-MAK catalogue (nominal moment, ratio, overhung load, thermal power)."},
 copied:{tr:"✓ Kopyalandı",en:"✓ Copied"},
};

/* ================= state ================= */
let lang = 'tr';
let cur = 0;
let vals = {};        // current variable values for the selected app
let n1V = 1450, etaV = APPS[0].eta, sfV = APPS[0].sf;
const $ = id => document.getElementById(id);
const t = o => (o && typeof o==='object' && !Array.isArray(o)) ? (o[lang] ?? o.en ?? o.tr) : o;
const nf = (v,d=0) => isFinite(v) ? Number(v).toLocaleString(lang==='tr'?'tr-TR':'en-US',{maximumFractionDigits:d,minimumFractionDigits:0}) : '—';

function loadDefaults(){ const a=APPS[cur]; vals={}; a.vars.forEach(v=>vals[v.id]=v.def); etaV=a.eta; sfV=a.sf; }

/* ---- build the application dropdown ---- */
function buildAppSelect(){
  const sel=$("appSel"); sel.innerHTML="";
  const groups={};
  APPS.forEach((a,i)=>{ const g=t(a.grp); (groups[g]=groups[g]||[]).push(i); });
  Object.keys(groups).forEach(g=>{ const og=document.createElement("optgroup"); og.label=g;
    groups[g].forEach(i=>{ const o=document.createElement("option"); o.value=i; o.textContent=t(APPS[i].name); if(i===cur)o.selected=true; og.appendChild(o); });
    sel.appendChild(og); });
}

/* ---- render the dedicated page for the current app ---- */
function renderPage(){
  const a=APPS[cur];
  $("dia").innerHTML = DIA[a.dia]||"";
  $("appTitle").textContent = t(a.name);
  $("appGroup").textContent = t(a.grp);
  $("appSeries").textContent = t(a.series);
  $("formulaBox").textContent = t(a.formula);
  $("lblDiagram").textContent = t(UI.diagram);
  $("lblFormula").textContent = t(UI.formula);
  $("lblInputs").textContent = t(UI.inputs);
  $("lblSteps").textContent = t(UI.steps);
  $("lblResult").textContent = t(UI.result);
  // variable inputs
  let html="";
  a.vars.forEach(v=>{ const unit=v.u?` (${v.u})`:""; const val=vals[v.id]??v.def;
    html+=`<label class="f"><span class="lab">${t(v.lab)}${unit}</span><input type="number" id="v_${v.id}" value="${val}" step="${v.step}" inputmode="decimal"></label>`; });
  // global inputs
  html+=`<label class="f"><span class="lab">${t(UI.motorRpm)} (d/dk)</span><input type="number" id="g_n1" value="${n1V}" step="10" inputmode="decimal"></label>`;
  html+=`<label class="f"><span class="lab">${t(UI.eta)}</span><input type="number" id="g_eta" value="${etaV}" step="0.01" min="0.4" max="1" inputmode="decimal"></label>`;
  html+=`<label class="f"><span class="lab">${t(UI.sf)}</span><input type="number" id="g_sf" value="${sfV}" step="0.05" min="1" inputmode="decimal"></label>`;
  $("inputs").innerHTML=html;
  a.vars.forEach(v=>$("v_"+v.id).addEventListener("input",onInput));
  ["g_n1","g_eta","g_sf"].forEach(id=>$(id).addEventListener("input",onInput));
  recompute();
}

function onInput(){
  const a=APPS[cur];
  a.vars.forEach(v=>{ const el=$("v_"+v.id); vals[v.id]=parseFloat(el.value); });
  n1V=parseFloat($("g_n1").value); etaV=parseFloat($("g_eta").value); sfV=parseFloat($("g_sf").value);
  recompute();
}

let last=null;
function recompute(){
  const a=APPS[cur]; const r=a.calc(vals); last=r;
  let MT=r.MT, n=r.n, Pout=r.Pout;
  if(!isFinite(MT) && isFinite(Pout) && n>0) MT=9550*Pout/n;
  if(!isFinite(Pout) && isFinite(MT) && n>0) Pout=MT*n/9550;
  const eta=etaV>0?etaV:1;
  const Pmotor=isFinite(Pout)?Pout/eta:NaN;
  const rec=isFinite(Pmotor)?iecUp(Pmotor):NaN;
  const ratio=(n1V>0&&n>0)?n1V/n:NaN;
  const sf=Math.max(1,sfV||1);
  const Mn=isFinite(MT)?MT*sf:NaN;
  // steps
  let sh="";
  (r.steps||[]).forEach(s=>{ sh+=`<div class="step"><span class="sl">${t(s.lab)}</span><span class="se">${s.expr} = <b>${nf(s.res, s.res<10?2:s.res<100?1:0)} ${s.u}</b></span></div>`; });
  // add motor + required-moment step
  sh+=`<div class="step"><span class="sl">${t(UI.motor)}</span><span class="se">Pₘ = ${nf(Pout,2)}/${nf(eta,2)} = <b>${nf(Pmotor,2)} kW → ${nf(rec, rec<10?1:0)} kW</b></span></div>`;
  sh+=`<div class="step"><span class="sl">${t(UI.Mn)}</span><span class="se">Mₙ = ${nf(MT,0)}·${sf.toFixed(2)} = <b>${nf(Mn,0)} Nm</b></span></div>`;
  $("steps").innerHTML=sh;
  // result cards
  $("rMT").innerHTML = nf(MT,0)+' <small>Nm</small>';
  $("rn").innerHTML = nf(n, n<10?1:0)+' <small>d/dk</small>';
  $("ri").innerHTML = nf(ratio,1)+' <small>:1</small>';
  $("rP").innerHTML = nf(rec, rec<10?1:0)+' <small>kW</small>';
  $("rSf").innerHTML = sf.toFixed(2);
  $("rMn").innerHTML = nf(Mn,0)+' <small>Nm</small>';
  const rl=t(UI.recline).replace("%s", nf(Mn,0)).replace("%r", nf(ratio,1)+":1");
  $("recLine").textContent = rl;
}

/* ---- language ---- */
function applyLang(){
  document.documentElement.lang=lang;
  $("tagline").innerHTML=t(UI.tagline);
  $("btnLangTr").classList.toggle("on",lang==='tr');
  $("btnLangEn").classList.toggle("on",lang==='en');
  $("lblApp").textContent=t(UI.pickApp);
  $("lblMT").textContent=t(UI.MT); $("lblN").textContent=t(UI.nout); $("lblI").textContent=t(UI.ratio);
  $("lblP").textContent=t(UI.motor); $("lblSf").textContent=t(UI.sf); $("lblMn").textContent=t(UI.Mn);
  $("lblRec").textContent=t(UI.rec);
  $("copyBtn").innerHTML="&#9106; "+t(UI.copy);
  $("printBtn").innerHTML="&#9143; "+t(UI.print);
  $("resetBtn").innerHTML="&#8635; "+t(UI.reset);
  $("disc").textContent=t(UI.disc);
  buildAppSelect();
  renderPage();
}

/* ---- wiring ---- */
$("appSel").addEventListener("change",e=>{ cur=+e.target.value; loadDefaults(); renderPage(); });
$("btnLangTr").addEventListener("click",()=>{ lang='tr'; applyLang(); });
$("btnLangEn").addEventListener("click",()=>{ lang='en'; applyLang(); });
$("resetBtn").addEventListener("click",()=>{ loadDefaults(); renderPage(); });
if($("printBtn")) $("printBtn").addEventListener("click",()=>window.print());
$("copyBtn").addEventListener("click",()=>{
  const a=APPS[cur]; recompute(); const r=last;
  let MT=r.MT,n=r.n,Pout=r.Pout;
  if(!isFinite(MT)&&isFinite(Pout)&&n>0)MT=9550*Pout/n; if(!isFinite(Pout)&&isFinite(MT)&&n>0)Pout=MT*n/9550;
  const eta=etaV>0?etaV:1;const Pmotor=Pout/eta;const rec=iecUp(Pmotor);const ratio=(n1V>0&&n>0)?n1V/n:NaN;const sf=Math.max(1,sfV);const Mn=MT*sf;
  const L=lang;
  const txt=(L==='tr'?"İ-MAK REDÜKTÖR SEÇİMİ":"I-MAK GEARBOX SELECTION")+"\n------------------------------------\n"+
    (L==='tr'?"Uygulama":"Application")+" : "+t(a.name)+"\n"+
    (L==='tr'?"Formül":"Formula")+"   : "+t(a.formula)+"\n"+
    (L==='tr'?"Çıkış momenti Mᴛ":"Output moment Mᴛ")+" : "+nf(MT,0)+" Nm\n"+
    (L==='tr'?"Çıkış devri n":"Output speed n")+" : "+nf(n,1)+" d/dk\n"+
    (L==='tr'?"Tahvil i":"Ratio i")+" : "+nf(ratio,1)+":1\n"+
    (L==='tr'?"Servis faktörü":"Service factor")+" : "+sf.toFixed(2)+"\n"+
    (L==='tr'?"Gerekli nominal moment Mₙ":"Required nominal moment Mₙ")+" : "+nf(Mn,0)+" Nm\n"+
    (L==='tr'?"Motor gücü":"Motor power")+" : "+nf(rec,1)+" kW ("+(L==='tr'?"min":"min")+" "+nf(Pmotor,2)+" kW)\n"+
    (L==='tr'?"Önerilen ürün":"Suggested product")+" : "+t(a.series)+"\n"+
    "------------------------------------";
  navigator.clipboard.writeText(txt).then(()=>{ const b=$("copyBtn"),o=b.innerHTML; b.textContent=t(UI.copied); setTimeout(()=>b.innerHTML=o,1400); }).catch(()=>window.prompt("Copy:",txt));
});

/* ---- init ---- */
$("marker").innerHTML = MARKER;
loadDefaults();
applyLang();
