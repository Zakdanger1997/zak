# 🤖 İş Başvuru Asistanı — n8n Kurulum Rehberi (Sıfırdan)

Bu sistem şunu yapar:

1. **Telegram**'dan bota bir mail listesi gönderirsiniz (örn. `ik@arcelik.com.tr, kariyer@vestel.com.tr`)
2. **Yapay zekâ (AI)** her mailin hangi firmaya ait olduğunu tespit eder
3. AI, sizin profilinize göre **o firmaya özel** bir başvuru maili yazar
4. Bot size Telegram'dan taslağı gösterir ve **"✅ Gönder / ⏭ Atla"** butonları sunar
5. **Sadece siz "Gönder"e basarsanız** mail, CV'niz ekli olarak Gmail'den gönderilir — basmazsanız hiçbir şey gönderilmez
6. Gönderilen her firma **Google Sheets'teki listeye** kaydedilir
7. **Aynı firmaya ikinci kez asla mail atılmaz** (hem liste gönderirken hem gönderim anında iki kez kontrol edilir)

## Akış Şeması

```
Telegram'a mail listesi atarsınız
        │
        ▼
Mailler ayıklanır ──► Google Sheets'ten "daha önce gönderilenler" okunur
        │
        ▼
Daha önce mail atılan firmalar ELENİR (tekrar yok!)
        │
        ▼
AI her mail için: firmayı tespit eder + size özel başvuru maili yazar
        │
        ▼
Taslak Google Sheets'e kaydedilir + Telegram'dan size sorulur:
        "Bu başvuruyu göndereyim mi?  [✅ Gönder] [⏭ Atla]"
        │
        ├── ⏭ Atla derseniz → hiçbir şey gönderilmez, taslak "ATLANDI" olur
        │
        └── ✅ Gönder derseniz:
                1. Firma tekrar kontrol edilir (zaten gönderilmişse DURUR ve sizi uyarır)
                2. CV'niz indirilir
                3. Gmail'den mail + CV eki gönderilir
                4. Firma "Gonderilenler" listesine yazılır
                5. Telegram'dan "✅ Gönderildi" mesajı gelir
```

---

## BÖLÜM 1 — Hesapları Hazırlama (yaklaşık 30 dk)

### Adım 1: n8n hesabı açın

En kolayı n8n Cloud:

1. https://n8n.io adresine gidin → **Get started** ile ücretsiz deneme hesabı açın
2. Giriş yaptığınızda karşınıza n8n paneli gelir. Buradaki her otomasyona **workflow** denir.

> Alternatif: Bilgisayarınıza Docker ile de kurabilirsiniz ama yeni başlayan biriyseniz Cloud'u öneririm — hiçbir kurulum gerektirmez.

### Adım 2: Telegram botu oluşturun

1. Telegram'da **@BotFather** kullanıcısını aratıp açın
2. `/newbot` yazın → bota bir isim verin (örn. `Is Basvuru Asistanim`) → bir kullanıcı adı verin (örn. `is_basvuru_xyz_bot`, sonu `bot` ile bitmeli)
3. BotFather size **token** verecek. Şuna benzer: `7123456789:AAHxK9...`. **Bunu kaydedin.**

### Adım 3: Kendi Chat ID'nizi öğrenin

1. Telegram'da **@userinfobot** kullanıcısını açıp `/start` yazın
2. Size `Id: 123456789` gibi bir numara verir. **Bu sizin Chat ID'niz, kaydedin.**
   (Bu sayede botunuzu sizden başka kimse kullanamaz.)
3. Son olarak **kendi botunuzu** açıp `/start` yazın (bot sizinle konuşabilsin diye bu şart).

### Adım 4: OpenAI API anahtarı alın

1. https://platform.openai.com adresine gidin, hesap açın
2. Sol menüden **API keys** → **Create new secret key** → çıkan `sk-...` anahtarını **kaydedin**
3. **Billing** bölümünden küçük bir bakiye yükleyin (5$ aylarca yeter, mail başına maliyet 1 kuruştan azdır)

### Adım 5: Google Sheets tablosunu oluşturun

1. https://sheets.google.com → boş tablo açın, adını `Is Basvurulari` koyun
2. Alttaki sekmenin adını **`Taslaklar`** yapın ve **1. satıra** şu başlıkları yazın (sırasıyla, küçük harf):

   | A | B | C | D | E | F | G | H | I |
   |---|---|---|---|---|---|---|---|---|
   | id | tarih | email | domain | firma | sektor | konu | govde | durum |

3. Alttan **+** ile ikinci bir sayfa ekleyin, adını **`Gonderilenler`** yapın ve 1. satıra:

   | A | B | C | D | E |
   |---|---|---|---|---|
   | tarih | firma | email | domain | konu |

4. Tarayıcıdaki **tablo linkini kaydedin** (https://docs.google.com/spreadsheets/d/... ile başlayan).

> ⚠️ Sayfa adlarını aynen `Taslaklar` ve `Gonderilenler` yazın (Türkçe karaktersiz), başlıkları da aynen bu şekilde yazın.

### Adım 6: CV'nizi linke dönüştürün

1. CV'nizi PDF olarak **Google Drive**'a yükleyin
2. Dosyaya sağ tık → **Paylaş** → "Bağlantıya sahip olan herkes → Görüntüleyen" yapın
3. Linki kopyalayın. Şuna benzer: `https://drive.google.com/file/d/1AbCdEfGh.../view?usp=sharing`
4. Ortadaki uzun kodu (dosya ID) alın ve şu kalıba yerleştirin:

   ```
   https://drive.google.com/uc?export=download&id=DOSYA_ID
   ```

   Örnek: `https://drive.google.com/uc?export=download&id=1AbCdEfGh...`
   **Bu linki kaydedin** — sistem CV'nizi buradan indirip maile ekleyecek.

---

## BÖLÜM 2 — n8n'i Ayarlama (yaklaşık 20 dk)

### Adım 7: Kimlik bilgilerini (Credentials) ekleyin

n8n'de sol menüden **Credentials** → **Add credential** deyip sırayla şu 4 tanesini oluşturun:

| Aranacak tür | Verilecek isim | Ne gireceksiniz |
|---|---|---|
| **Telegram API** | `Telegram Bot` | Adım 2'deki bot token'ı |
| **OpenAI** | `OpenAI Hesabım` | Adım 4'teki `sk-...` anahtarı |
| **Google Sheets OAuth2 API** | `Google Sheets Hesabım` | "Sign in with Google" ile Google hesabınıza izin verin |
| **Gmail OAuth2** | `Gmail Hesabım` | Mail atacağınız Gmail hesabıyla giriş yapın |

> Google/Gmail girişinde "Sign in with Google" butonuna basıp izinleri onaylamanız yeterli; n8n Cloud'da ekstra ayar gerekmez.

### Adım 8: Workflow'u içe aktarın

1. n8n'de **Workflows** → sağ üstten **⋯ (üç nokta)** → **Import from File**
2. Bu klasördeki `workflow/is_basvuru_asistani.json` dosyasını seçin
3. Ekrana kutucuklardan (node) oluşan akış gelecek. Her kutu bir işlem adımıdır.

### Adım 9: "Ayarlar" kutusunu kendinize göre doldurun

Akıştaki **Ayarlar** kutusuna çift tıklayın ve şu alanları kendi bilgilerinizle değiştirin:

| Alan | Ne yazacaksınız |
|---|---|
| `telegram_chat_id` | Adım 3'teki ID numaranız (örn. `123456789`) |
| `sheet_url` | Adım 5'teki Google Sheets linki |
| `cv_url` | Adım 6'daki indirme linki |
| `ad_soyad` | Adınız soyadınız |
| `meslek` | Mesleğiniz (örn. Makine Mühendisi) |
| `pozisyon` | Başvurmak istediğiniz pozisyon |
| `deneyim_ozeti` | 2-3 cümleyle deneyiminiz (AI maili buna göre yazar) |
| `yetenekler` | Bildiğiniz programlar, diller vb. |
| `telefon` | Telefon numaranız (mailin imzasına girer) |
| `linkedin` | LinkedIn adresiniz |

### Adım 10: Kutulardaki kimlik bilgilerini seçin

Import edilen dosyada kimlik bilgileri "bulunamadı" görünebilir. Şu kutulara çift tıklayıp üstteki **Credential** menüsünden Adım 7'de oluşturduklarınızı seçin:

- **Telegram Trigger, Butonu Yanıtla, Onay İste ve tüm "Bildir - ..." kutuları** → `Telegram Bot`
- **Tüm Google Sheets kutuları** (Taslağı Bul, Gönderilenleri Oku, Taslağı Kaydet, Gönderilenlere Ekle, Taslağı Güncelle...) → `Google Sheets Hesabım`
- **OpenAI Chat Model** → `OpenAI Hesabım`
- **Başvuru Mailini Gönder** → `Gmail Hesabım`

> 💡 Bir Google Sheets kutusu tabloyu bulamazsa: kutuyu açın, **Document** alanında listeden tablonuzu, **Sheet** alanında listeden `Taslaklar` veya `Gonderilenler` sayfasını elle seçin.

### Adım 11: Workflow'u aktifleştirin

Sağ üstteki **Inactive / Active** anahtarını **Active** yapın. Artık bot sizi dinliyor. 🎉

---

## BÖLÜM 3 — Kullanım

### Mail listesi gönderme

Telegram'da botunuza mail adreslerini yazın. Format serbesttir; virgülle, satır satır ya da düz metin içinde olabilir:

```
ik@firmaA.com.tr
kariyer@firmaB.com
hr@firmaC.com
```

Bot birkaç saniye içinde **her firma için ayrı bir onay mesajı** gönderir:

```
🏢 Firma: Firma A Sanayi
🏷 Sektör: Otomotiv yan sanayi
📧 Alıcı: ik@firmaA.com.tr
📌 Konu: Üretim Mühendisi Pozisyonu Başvurusu

━━━━━━━━━━━━━━
Sayın Firma A İnsan Kaynakları Ekibi, ...
━━━━━━━━━━━━━━

Bu başvuruyu göndereyim mi?
[✅ Gönder]  [⏭ Atla]
```

### Butonlar

- **✅ Gönder** → CV'niz eklenir, mail gönderilir, firma listeye yazılır, size "✅ Gönderildi" mesajı gelir.
- **⏭ Atla** → hiçbir şey gönderilmez.
- **Hiçbir butona basmazsanız** → hiçbir şey gönderilmez. Sistem sizden onay almadan asla mail atmaz.

### Tekrar koruması

- Aynı listede aynı firmadan 2 adres varsa sadece biri işlenir.
- Daha önce mail attığınız bir firmayı tekrar gönderirseniz bot "daha önce gönderilmiş" der ve eler.
- Eski bir onay mesajındaki "Gönder"e ikinci kez bassanız bile sistem son anda tekrar kontrol eder ve **aynı firmaya ikinci maili engeller**.

### Kayıtlar

Google Sheets tablonuzda:
- **Taslaklar** sayfası: AI'ın yazdığı tüm mailler ve durumları (BEKLIYOR / GONDERILDI / ATLANDI)
- **Gonderilenler** sayfası: kime, ne zaman, hangi konuyla mail attığınızın tam listesi

---

## Sorun Giderme

| Sorun | Çözüm |
|---|---|
| Bot mesajlarıma hiç cevap vermiyor | Workflow **Active** mi? Telegram Trigger'da doğru credential seçili mi? Kendi botunuza `/start` yazdınız mı? |
| "Chat ID" uyuşmuyor, bot sessiz kalıyor | `Ayarlar` kutusundaki `telegram_chat_id` alanına @userinfobot'un verdiği numarayı yazdığınızdan emin olun |
| Google Sheets hatası ("sheet not found") | Sayfa adları tam olarak `Taslaklar` ve `Gonderilenler` mi? Değilse kutuyu açıp listeden elle seçin |
| Mail gönderildi ama CV eki yok/bozuk | `cv_url` linkini tarayıcıya yapıştırın — PDF **direkt inmeli**. İnmiyorsa Adım 6'daki `uc?export=download&id=...` formatını kontrol edin ve dosyanın "linke sahip herkes" ile paylaşıldığından emin olun |
| AI saçma firma adı buldu | Normaldir; taslağı beğenmezseniz **⏭ Atla** deyin. `Ayarlar`daki `deneyim_ozeti` alanını ne kadar iyi doldurursanız mailler o kadar iyi olur |
| OpenAI hatası (429 / quota) | OpenAI hesabınızda bakiye olduğundan emin olun |
| Bir kutu kırmızı hata veriyor | Kutuya çift tıklayın; hata mesajı genelde hangi credential ya da alanın eksik olduğunu söyler |

## Maliyet

- **n8n Cloud**: deneme sonrası aylık ücretli (kendi bilgisayarınıza/sunucunuza kurarsanız ücretsiz)
- **OpenAI**: mail başına ~0,01 TL (gpt-4o-mini)
- **Telegram, Google Sheets, Gmail**: ücretsiz
