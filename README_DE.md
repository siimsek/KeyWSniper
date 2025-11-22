# KeyWSniper

Dieses Projekt ist ein leistungsstarkes Telegram-Überwachungstool, das einen **Userbot** (zum Lesen von Kanälen ohne Admin-Rechte) und eine **Bot-Schnittstelle** (zur einfachen Verwaltung über Menüs) kombiniert.

## Funktionen
- 🕵️ **Userbot:** Überwacht Kanäle, in denen Sie Mitglied sind (keine Admin-Rechte erforderlich).
- 🤖 **Bot-Schnittstelle:** Verwalten Sie Schlüsselwörter und Kanäle über ein benutzerfreundliches Menü.
- 🌐 **Mehrsprachig:** Unterstützt Englisch, Türkisch, Russisch und Deutsch.
- 🔔 **Sofortbenachrichtigungen:** Werden Sie sofort benachrichtigt, wenn ein Schlüsselwort erwähnt wird.
- 📦 **Backup & Wiederherstellung:** Exportieren und importieren Sie Ihre Tracking-Liste.
- 🗑️ **Interaktives Löschen:** Löschen Sie Schlüsselwörter einfach per Knopfdruck.

## Voraussetzungen
1. **Python 3.8+**
2. **Telegram API ID & Hash:** Erhalten Sie diese von [my.telegram.org](https://my.telegram.org).
3. **Bot Token:** Erhalten Sie einen von [@BotFather](https://t.me/BotFather).

## Installation

1. **Repository klonen:**
   ```bash
   git clone https://github.com/siimsek/KeyWSniper.git
   cd KeyWSniper
   ```

2. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Konfiguration:**
   - Öffnen Sie die Datei `.env`.
   - Geben Sie Ihre Anmeldedaten ein:
     ```ini
     API_ID=12345678
     API_HASH=ihr_api_hash_hier
     BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
     ```

4. **Bot starten:**
   ```bash
   python bot.py
   ```
   - Beim ersten Start werden Sie nach Ihrer Telefonnummer und dem an Ihr Telegram-Konto gesendeten Code gefragt, um den Userbot zu autorisieren.

## Nutzung
1. Öffnen Sie Ihren Bot in Telegram (`/start`).
2. Verwenden Sie die Schaltfläche **Hinzufügen**, um einen Kanal und ein Schlüsselwort zu folgen.
   - Sie können Kanal-Benutzernamen (`@channel`), Links (`t.me/channel`) oder IDs (`-100...`) verwenden.
3. Der Bot sendet Ihnen eine Benachrichtigung, sobald ein passendes Schlüsselwort in den überwachten Kanälen gefunden wird.

