# KeyWSniper

Dieses Projekt ist ein leistungsstarkes Telegram-Überwachungstool, das einen **Userbot** (zum Lesen von Kanälen ohne Admin-Rechte) und eine **Bot-Schnittstelle** (zur einfachen Verwaltung über Menüs) kombiniert.

## Funktionen
- 🕵️ **Userbot:** Überwacht Kanäle, in denen Sie Mitglied sind (keine Admin-Rechte erforderlich).
- 🤖 **Bot-Schnittstelle:** Verwalten Sie Schlüsselwörter und Kanäle über ein benutzerfreundliches Menü.
- 🌐 **Mehrsprachig:** Unterstützt Englisch, Türkisch, Russisch und Deutsch.
- 🔔 **Sofortbenachrichtigungen:** Werden Sie sofort benachrichtigt, wenn ein Schlüsselwort erwähnt wird.
- 📦 **Backup & Wiederherstellung:** Exportieren und importieren Sie Ihre Tracking-Liste.
- 🗑️ **Interaktives Löschen:** Löschen Sie Schlüsselwörter einfach per Knopfdruck.

## 🚀 Bereitstellung auf Render.com (24/7 Online)

Damit der Bot rund um die Uhr läuft, folgen Sie diesen Schritten:

### 1. Vorbereitung
1. Forken Sie dieses Repository.
2. Holen Sie sich **API_ID** und **API_HASH** von [my.telegram.org](https://my.telegram.org).
3. Holen Sie sich **BOT_TOKEN** von [@BotFather](https://t.me/BotFather).
4. **Sitzungscode generieren:**
   - Führen Sie `python generate_session.py` lokal aus.
   - Melden Sie sich an.
   - Kopieren Sie den langen Code (`1BVts...`).

### 2. Render-Einstellungen
1. Erstellen Sie einen neuen **Web Service** auf Render.
2. Verbinden Sie Ihr GitHub-Repository.
3. Einstellungen:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
4. **Umgebungsvariablen:**
   
   | Schlüssel | Wert | Beschreibung |
   | :--- | :--- | :--- |
   | `API_ID` | `123456` | Ihre Telegram API ID |
   | `API_HASH` | `abc123...` | Ihr Telegram API Hash |
   | `BOT_TOKEN` | `123:ABC...` | Bot-Token von BotFather |
   | `SESSION_STRING` | `1BVts...` | Code von generate_session.py |

### 3. 💾 Datenpersistenz (Wichtig!)
Auf Render werden Dateien beim Neustart gelöscht. Um Ihre Daten zu sichern:

- **Option A (Kostenlos):** Nutzen Sie die **Backup**-Taste im Bot. Nach dem Update nutzen Sie **Import**.
- **Option B (Automatisch):** Der Bot sichert Daten automatisch im Telegram-Chat und stellt sie beim Start wieder her.
- **Option C (Disk):** Fügen Sie in den Render-Einstellungen eine **Disk** hinzu (Mount Path: `/opt/render/project/src`).

## 🔄 Wachhalten (Keep Alive)

Render versetzt Dienste im kostenlosen Tarif bei Inaktivität in den Ruhezustand. Um dies zu verhindern:

1. Kopieren Sie Ihre Render Web Service URL (z. B. `https://keywsniper.onrender.com`).
2. Gehen Sie zu [UptimeRobot](https://uptimerobot.com/) und erstellen Sie ein kostenloses Konto.
3. Klicken Sie auf **"Add New Monitor"**.
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** KeyWSniper
   - **URL:** Fügen Sie Ihre Render URL ein
   - **Monitoring Interval:** 5 minutes (5 Minuten)
4. Speichern Sie. UptimeRobot pingt Ihren Bot alle 5 Minuten an, um ihn wach zu halten.

## Lokale Installation

1. **Repository klonen:**
   ```bash
   git clone https://github.com/siimsek/KeyWSniper.git
   cd KeyWSniper
   ```

2. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Bot starten:**
   ```bash
   python bot.py
   ```
