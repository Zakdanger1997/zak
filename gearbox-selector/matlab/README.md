# İ-MAK Redüktör Seçici — MATLAB

Web ve C++ sürümleriyle **aynı 26 uygulama ve formülleri** kullanan MATLAB fonksiyonu.
MATLAB (R2016b+) ve büyük ölçüde **GNU Octave** ile çalışır. UTF-8 kodlamalıdır.

*MATLAB function using the **same 26 applications and formulas** as the web / C++
versions. Works in MATLAB (R2016b+) and largely in GNU Octave. UTF-8 encoded.*

## Kullanım / Usage
```matlab
imak_reduktor()                     % interaktif menü / interactive menu
r = imak_reduktor('kiln')           % programatik (varsayılan girdiler) / defaults
r = imak_reduktor('kiln', v)        % v = girdi struct'ı / struct of inputs
r = imak_reduktor('kiln', v, 'en')  % İngilizce / English
```
`v` içine uygulamanın herhangi bir değişkeni + isteğe bağlı `n1` (motor devri, 1450),
`eta` (redüktör verimi), `sf` (servis faktörü) konabilir.

Dönen `r` alanları / returned fields: `MT` (Nm), `n` (d/dk), `Pout`, `Pmotor`,
`motor_kW` (IEC), `ratio`, `sf`, `Mn` (Nm), `steps`, `name`, `formula`, `series`.

Örnekler için `demo_imak.m` dosyasını çalıştırın. / Run `demo_imak.m` for examples.

## Uygulama kimlikleri / Application ids
`belt_h belt_inc screw elevator chain feeder hoist pulley travel slew lift
mixer_b mixer_np kiln extruder roller hammer ballmill sifter pellet crusher
vibscreen rotable pump recip fan`

## Beklenen sonuçlar (varsayılan girdiler) / Expected results (default inputs)
Formüller doğrulanmış web motoruyla aynıdır; bu değerler `imak_reduktor('<id>')`
çıktısıyla eşleşmelidir. / Formulas are identical to the verified web engine; these
should match `imak_reduktor('<id>')`.

| id | Mᴛ (Nm) | n (d/dk) | motor (kW) |
|---|---:|---:|---:|
| belt_h | 1533 | 76.4 | 15 |
| belt_inc | 2037 | 76.4 | 18.5 |
| screw | 1560 | 1.3 | 0.25 |
| elevator | 568 | 57.3 | 4 |
| chain | 2943 | 25.5 | 11 |
| feeder | 12 | 750 | 1.1 |
| hoist | 2943 | 10.6 | 4 |
| pulley | 5163 | 12.7 | 7.5 |
| travel | 118 | 57.3 | 0.75 |
| slew | 1914 | 1.5 | 0.37 |
| lift | 1472 | 31.8 | 5.5 |
| mixer_b | 6188 | 20 | 15 |
| mixer_np | 7 | 60 | 0.12 |
| kiln | 123606 | 2 | 30 |
| extruder | 3820 | 100 | 45 |
| roller | 3183 | 300 | 110 |
| hammer | 478 | 1500 | 90 |
| ballmill | 124150 | 18 | 250 |
| sifter | 89 | 220 | 2.2 |
| pellet | 13752 | 250 | 355 |
| crusher | 4775 | 200 | 110 |
| vibscreen | 89 | 900 | 11 |
| rotable | 312 | 5 | 0.18 |
| pump | 38 | 1450 | 7.5 |
| recip | 122 | 300 | 5.5 |
| fan | 14 | 1450 | 2.2 |

## Formülü değiştirme / Editing a formula
İlgili `calc_*` yerel fonksiyonunu düzenleyin (ör. `calc_kiln`):
```matlab
MT = (1+v.k/100)*v.m*G*(D/2)*v.e;   % <- formülü buradan değiştirin
```

> Not: Bu ortamda MATLAB kurulu olmadığından sayısal sonuçlar doğrulanmış web
> motoruyla (aynı formüller) karşılaştırılarak doğrulanmıştır; MATLAB'de çalıştırma
> testi yapılmamıştır. / Note: MATLAB was not available here, so the numbers were
> verified against the identical, browser-tested web engine rather than executed in
> MATLAB itself.
