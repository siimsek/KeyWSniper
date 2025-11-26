# KeyWSniper

Bu proje, **Userbot** (yönetici izni olmadan kanalları okuma) ve **Bot Arayüzü** (kolay yönetim) özelliklerini birleştiren güçlü bir Telegram izleme aracıdır.

## Özellikler
- 🕵️ **Userbot:** Üye olduğunuz kanalları arka planda izler (Yönetici olmanıza gerek yok).
- 🤖 **Bot Arayüzü:** Anahtar kelimeleri ve kanalları butonlu menü ile yönetin.
- 🌐 **Çoklu Dil:** İngilizce, Türkçe, Rusça ve Almanca desteği.
- 🔔 **Anlık Bildirimler:** Kelimeniz geçtiğinde anında bildirim alın.
- 📦 **Yedekleme & Geri Yükleme:** Takip listenizi yedekleyin ve geri yükleyin.
- 🗑️ **Kolay Silme:** Tek tıkla listeden silme işlemi yapın.

## 🚀 Render.com Üzerinde Kurulum (7/24 Aktif)

Botun sürekli açık kalması için Render kullanabilirsiniz. Adımlar şöyledir:

### 1. Hazırlık
1. Bu repoyu kendi GitHub hesabınıza "Fork"layın.
2. [my.telegram.org](https://my.telegram.org) adresinden **API_ID** ve **API_HASH** alın.
3. [@BotFather](https://t.me/BotFather)'dan **BOT_TOKEN** alın.
4. **Session Kodu Oluşturma:**
   - Bilgisayarınızda `python generate_session.py` dosyasını çalıştırın.
   - Telefon numaranızla giriş yapın.
   - Size verilen `1BVts...` ile başlayan uzun kodu kopyalayın.

### 2. Render Ayarları
1. Render'da yeni bir **Web Service** oluşturun.
2. GitHub reponuzu bağlayın.
3. Ayarlar:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
4. **Environment Variables (Ortam Değişkenleri):** Şu bilgileri ekleyin:
   
   | Anahtar (Key) | Değer (Value) | Açıklama |
   | :--- | :--- | :--- |
   | `API_ID` | `123456` | Telegram API ID'niz |
   | `API_HASH` | `abc123...` | Telegram API Hash kodunuz |
   | `BOT_TOKEN` | `123:ABC...` | BotFather'dan alınan token |
   | `SESSION_STRING` | `1BVts...` | generate_session.py'den aldığınız kod |
   | `PYTHON_VERSION` | `3.10.0` | (Opsiyonel) Uyumluluk için |

### 3. 💾 Veri Kalıcılığı (Önemli!)
Render gibi bulut sistemlerinde bot yeniden başladığında dosyalar silinir (takip listeniz gider). Bunu önlemek için:

- **Seçenek A (Ücretsiz):** Bot ayarlarından ara sıra **Yedekle** butonunu kullanın. Güncelleme sonrası **İçe Aktar** ile verileri geri yükleyin.
- **Seçenek B (Otomatik):** Bot verileri otomatik olarak Telegram sohbetinize yedekler ve açılışta geri yükler.
- **Seçenek C (Disk):** Render ayarlarından bir **Disk** ekleyin (Bağlama Yolu: `/opt/render/project/src`).

## 🔄 Botu Uyutmamak (Keep Alive)

Render ücretsiz paketi, işlem yapılmadığında servisi uyku moduna alır. Bunu engellemek için:

1. Render Web Service URL adresinizi kopyalayın (Örn: `https://keywsniper.onrender.com`).
2. [UptimeRobot](https://uptimerobot.com/) sitesine gidin ve ücretsiz hesap açın.
3. **"Add New Monitor"** butonuna tıklayın.
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** KeyWSniper
   - **URL:** Render adresinizi yapıştırın
   - **Monitoring Interval:** 5 minutes (5 dakika)
4. Kaydedin. UptimeRobot botunuza 5 dakikada bir ping atarak uyumasını engelleyecektir.

## Yerel Kurulum (Kendi Bilgisayarınızda)

1. **Depoyu indirin:**
   ```bash
   git clone https://github.com/siimsek/KeyWSniper.git
   cd KeyWSniper
   ```

2. **Gerekli kütüphaneleri yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Botu çalıştırın:**
   ```bash
   python main.py
   ```

## 🐳 Docker Desteği

Botu Docker kullanarak da çalıştırabilirsiniz:

```bash
docker build -t keywsniper .
docker run --env-file .env keywsniper
```

## Sorumluluk Reddi
Bu araç sadece eğitim amaçlıdır. Telegram Hizmet Koşullarına uygun şekilde sorumlu bir şekilde kullanın.
