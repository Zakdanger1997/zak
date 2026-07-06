# İ-MAK Redüktör Seçici — C++ / C++ console version

Web uygulamasıyla **aynı 26 uygulama ve aynı formülleri** kullanan konsol programı.
Uygulamayı seçersiniz, değişkenleri girersiniz (Enter = varsayılan), program çıkış
momentini, devri, motor gücünü (bir üst IEC), tahvili, servis faktörünü ve gerekli
nominal momenti hesaplar. Türkçe/İngilizce.

*A console program using the **same 26 applications and formulas** as the web app.
Pick an application, enter the variables (Enter = default), and it computes output
moment, speed, motor power (next IEC size), ratio, service factor and required
nominal moment. Turkish/English.*

## Derleme / Build
```
g++ -std=c++17 -O2 -o imak_reduktor imak_reduktor.cpp
```
Windows (MSVC): `cl /std:c++17 /EHsc imak_reduktor.cpp`

## Çalıştırma / Run
```
./imak_reduktor          # Linux/macOS
imak_reduktor.exe        # Windows
```

## Doğrulama / Validation
Web uygulaması ve İ-MAK sunumuyla birebir aynı sonuçları verir. Örnekler:
- Vinç kaldırma (varsayılan) → Mᴛ = 2943 Nm, n = 10,6 d/dk, motor 4 kW (sunum s. 24)
- Döner fırın → Mᴛ = 123606 Nm, Mₙ = 185409 Nm, 30 kW
- Bilyalı değirmen (Bond) → E = 11,7 kWh/t, Mₙ = 217263 Nm, 250 kW

## Bir formülü değiştirme / Editing a formula
Her uygulamanın `calc` lambda'sını `imak_reduktor.cpp` içinde düzenleyin; örn. döner fırın:
```cpp
double MT = (1+v["k"]/100)*v["m"]*G*(D/2)*v["e"];   // <- formülü buradan değiştirin
```
