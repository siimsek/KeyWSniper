# KeyWSniper

Bu proje, **Userbot** (yönetici izni olmadan kanalları okuma) ve **Bot Arayüzü** (kolay yönetim) özelliklerini birleştiren güçlü bir Telegram izleme aracıdır.

## Özellikler
- 🕵️ **Userbot:** Üye olduğunuz kanalları arka planda izler (Yönetici olmanıza gerek yok).
- 🤖 **Bot Arayüzü:** Anahtar kelimeleri ve kanalları butonlu menü ile yönetin.
- 🌐 **Çoklu Dil:** İngilizce, Türkçe, Rusça ve Almanca desteği.
- 🔔 **Anlık Bildirimler:** Kelimeniz geçtiğinde anında bildirim alın.
- 📦 **Yedekleme & Geri Yükleme:** Takip listenizi yedekleyin ve geri yükleyin.
- 🗑️ **Kolay Silme:** Tek tıkla listeden silme işlemi yapın.

## Gereksinimler
1. **Python 3.8+**
2. **Telegram API ID & Hash:** [my.telegram.org](https://my.telegram.org) adresinden alın.
3. **Bot Token:** [@BotFather](https://t.me/BotFather) üzerinden alın.

## Kurulum

1. **Depoyu indirin:**
   ```bash
   git clone https://github.com/siimsek/KeyWSniper.git
   cd KeyWSniper
   ```

2. **Gerekli kütüphaneleri yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ayarlar:**
   - `.env` dosyasını açın.
   - Bilgilerinizi girin:
     ```ini
     API_ID=12345678
     API_HASH=api_hash_kodunuz
     BOT_TOKEN=bot_token_kodunuz
     ```

4. **Botu çalıştırın:**
   ```bash
   python bot.py
   ```
   - İlk çalıştırmada telefon numaranızı girip Telegram'dan gelen kodu onaylamanız istenecektir.

## Kullanım
1. Telegram'da botunuzu başlatın (`/start`).
2. **Takip Ekle** butonunu kullanarak kanal ve kelime ekleyin.
3. Bot, eşleşen bir mesaj bulduğunda size anında bildirim gönderecektir.
