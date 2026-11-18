# i.Mak — İhracat Erişim Raporu (Latin Amerika + Orta Doğu) · Türkçe + WhatsApp

`iMak_Erisim_Raporu_TR_18Kasim2026.pptx` — 13 slaytlık, 16:9, tamamen düzenlenebilir **Türkçe** sunum.
Her iki aktif Apollo kampanyasını (Latin Amerika ve Orta Doğu, 18 Kasım 2026 itibarıyla) kapsar ve
yeni bir **birebir WhatsApp kanalı** önerir. Yanında PDF kopyası ve tüm slaytların tek görsel önizlemesi var.

## Bu sürümde yeni
- **Türkçe çeviri** — tüm metinler, konuşmacı notları ve harita etiketleri; Türkçe sayı biçimi (1.600, %5,2, %98,4).
- **Yeni infografikler** — Slayt 4'te "yanıt oranı — bölgeye göre" sütun grafiği; Slayt 11'de WhatsApp↔E-posta açılma-oranı çubukları.
- **Slayt geçişleri (transitions)** — kapak ve kapanışta *fade*, aradaki slaytlarda *push* (soldan).

## Slaytlar
1 Kapak · 2 Yönetici özeti · 3 Tüm rakamlar (LatAm / Orta Doğu / Toplam tablo) · 4 İki bölge (sütun grafik) ·
5 Birleşik huni (halka grafikler) · 6 Müşteri adayları · 7 Pazarlar & dil (iki harita) · 8 Araçlar ·
9 Adım adım süreç · 10 Altı zorluk · 11 **Yeni: birebir WhatsApp kanalı** · 12 Büyüme kaldıraçları · 13 Sonraki adımlar.

## Rakamlar (Apollo, 18 Kasım 2026)
- **Latin Amerika** (i.Mak Reductores, ES, aktif): 1.223 gönderildi · 1.200 iletildi · 46 aday · %5,7 yanıt.
- **Orta Doğu** (Crane ME, EN, 12 Kasım'dan beri durgun): 377 gönderildi · 374 iletildi · 2 aday · %1,6 yanıt.
- **Birleşik:** 1.600 gönderildi · 1.574 iletildi (%98,4) · 48 aday · 26 geri dönen (%1,6).
- Yanıt oranı = ulaşılan kişi başına tekil yanıtlayan. WhatsApp rakamları (3,3 Mr+ kullanıcı, ~%95 açılma)
  izin vermiş kişiler için **sektör ortalamalarıdır**, garanti değildir.

## Güncelleme
Tüm rakamlar `build_deck.py` başındaki `D = dict(...)` bloğundadır.
```bash
pip install python-pptx pillow
python build_deck.py
python make_map.py countries-110m.json assets/latam_map.png latam
python make_map.py countries-110m.json assets/me_map.png    me
```
(İngilizce sürüm git geçmişinde mevcuttur.)
