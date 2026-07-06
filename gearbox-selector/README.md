# İ-MAK Redüktör Seçici / I-MAK Gearbox Selector

Uygulamaya özel redüktör seçim aracı. Her uygulamanın **kendi sayfası, kendi şeması
ve kendi formülü** vardır — tıpkı İ-MAK Ar-Ge Teknik Eğitim Sunumu'ndaki gibi.
Tamamen çevrimdışı çalışır (tek dosya, internet gerektirmez). Türkçe/İngilizce
geçişlidir.

*A per-application gearbox selection tool. Each application has its **own page, own
diagram and own formula** — just like the I-MAK R&D training deck. Fully offline
(single file), with a Turkish/English toggle.*

## Dosyalar / Files

| Dosya / File | Açıklama / Use |
|---|---|
| `imak-reduktor-3d.html` | **3B açılış / 3D hero** — interaktif dönen redüktör (Three.js gömülü, çevrimdışı); uygulamalara bağlanır / interactive rotating gearbox (Three.js embedded, offline); links into the apps |
| `imak-reduktor-secici-windows.html` | **Windows / masaüstü** — geniş yerleşim / wide desktop layout |
| `imak-reduktor-secici-phone.html` | **Telefon / phone** — tek sütun, büyük dokunma alanları / single column, large touch targets |
| `IMAK-Reduktor-Formuller.xlsx` | Tüm formüller (TR/EN) — inceleyin ve düzenleyin / all formulas, review & edit |

Bir dosyayı çift tıklayın; herhangi bir tarayıcıda açılır. / Double-click a file to
open it in any browser.

## Ne değişti / What changed

Önceki sürüm her uygulama için **aynı sayfayı** kullanıyordu. Bu sürümde her uygulama
**ayrı bir sayfadır**: kendi şeması, kendi formülü ve İ-MAK sunumundaki gibi adım
adım **canlı örnek hesap**. / The previous version used the **same page** for every
application. Now each application is its **own page**: its diagram, its formula, and
a **live step-by-step worked calculation** like the I-MAK deck.

### İ-MAK formülleri (sunumdan) / I-MAK formulas (from the deck)

| Uygulama / Application | Formül / Formula |
|---|---|
| Bantlı konveyör (yatay/eğimli) / Belt (horizontal/inclined) | `Mᴛ = k·(cosα+sinα)·m·g·r` · `n = 9,55·v/r` |
| Vinç kaldırma / Crane hoist | `Mᴛ = m·g·r` · `n = 9,55·v/r` |
| Palangalı kaldırma / Pulley hoist | `Mᴛ = m·g·r/z` · `n = 9,55·v·z/r` |
| Yürütme / Travel | `Mᴛ = [Q·f + μ·Q·(d/2)]·g` · `v = π·D·n/60000` |
| Helezon konveyör / Screw conveyor | `Pₘ = Qₜₒₚ·v/(60·75·1,36·η)` |
| Karıştırıcı (kanat) / Agitator (blade) | `Mₖ = (Ød/2)·b·kᵢ·ρ·10`, kanatların toplamı / summed |

> Doğrulama / Validation: uygulama, sunumdaki örnekleri birebir üretir — ör. vinç
> kaldırma 2 t / Ø300 mm / 10 m/dk → **Mᴛ = 2943 Nm, n = 10,6 d/dk, motor 4 kW**
> (sunum s. 24). / The app reproduces the deck's worked examples exactly — e.g. crane
> hoist 2 t / Ø300 mm / 10 m/min → **2943 Nm, 10.6 rpm, 4 kW** (deck p. 24).

### Web araştırmasıyla eklenenler / Added from web research (distinct formula each)

Kovalı elevatör, zincirli konveyör, titreşimli besleyici, döner (slewing) tahrik,
asansör, karıştırıcı (güç sayısı Np), döner fırın, ekstruder, valsli/çekiçli/**bilyalı
(Bond)** değirmen, elek/plansifter, pelet değirmeni, kırıcı, titreşimli elek, döner
tabla, santrifüj/pistonlu pompa, santrifüj fan.

## Hesap akışı / How it computes

1. Formül → çıkış momenti `Mᴛ` (Nm) veya çıkış gücü `Pₒ` (kW) + çıkış devri `n`.
2. `Mᴛ = 9550·Pₒ/n`  veya / or  `Pₒ = Mᴛ·n/9550`.
3. Motor gücü `Pₘ = Pₒ/η` → bir üst IEC güç. / next IEC size.
4. **Gerekli nominal moment `Mₙ = Mᴛ·Sf`** — katalog nominal momenti ≥ bu değer olan
   İ-MAK redüktörünü seçin. / choose an I-MAK unit with catalogue nominal moment ≥ this.

## Formülleri düzenleme / Editing the formulas

`IMAK-Reduktor-Formuller.xlsx` içindeki *Değişkenler* ve *Örnek Hesap* sayfaları her
denklemi ve varsayılanı belgeler. Değiştirip geri gönderin; her iki sürümü yeniden
üretebilirim. / Edit the *Variables* / *Worked example* sheets and send it back; both
app versions can be regenerated to match.

> Süreç sonuçları **saha tahminidir**; nihai seçimi İ-MAK kataloğu (nominal moment,
> tahvil, radyal yük, termik güç) ile doğrulayın. / Process results are **field
> estimates**; confirm against the I-MAK catalogue.
