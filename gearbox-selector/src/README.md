# Kaynak kod / Source code

Uygulamanın okunabilir kaynağı. Yayınlanan tek dosya (`imak-reduktor-secici-3d.html`)
bu parçaları + küçültülmüş Three.js kütüphanesini tek dosyada birleştirir.
*Readable source of the app. The shipped single file bundles these pieces + the
minified Three.js library inline.*

| Dosya / File | İçerik / Contents |
|---|---|
| `selector-engine.js` | **Ana kod** — 26 uygulama, tüm formüller, hesap adımları, TR/EN arayüz mantığı / **the main code** — 26 applications, all formulas, worked steps, TR/EN UI logic |
| `hero-3d.js` | 3B redüktör sahnesi (Three.js) / the 3D gearbox scene |
| `styles.css` | Tüm stiller / all styles |
| `index.html` | HTML iskeleti (yer tutucularla) / HTML skeleton (with placeholders) |
| `build.py` | Tek dosyayı üreten betik / builds the single self-contained file |
| `make_excel.py` | Excel formül kitabını üretir / generates the formulas workbook |

## Yeniden derleme / Rebuild
`three.min.js` ve `OrbitControls.js` (Three.js r128) dosyalarını aynı klasöre koyup
`python3 build.py` çalıştırın. / Put `three.min.js` and `OrbitControls.js` (Three.js
r128) in the folder and run `python3 build.py`.

Bir formülü değiştirmek için `selector-engine.js` içindeki ilgili uygulamanın `calc`
fonksiyonunu düzenleyin. / To change a formula, edit that application's `calc`
function in `selector-engine.js`.
