# KeyWSniper

This project is a powerful Telegram monitoring tool that combines a **Userbot** (to read channels without admin rights) and a **Bot Interface** (for easy management via menus).

## Features
- 🕵️ **Userbot:** Monitors channels you are a member of (no admin rights needed).
- 🤖 **Bot Interface:** Manage keywords and channels with an easy-to-use menu.
- 🌐 **Multi-Language:** Supports English, Turkish, Russian, and German.
- 🔔 **Instant Notifications:** Get notified immediately when a keyword is mentioned.
- 📦 **Backup & Restore:** Export and import your tracking list.
- 🗑️ **Interactive Deletion:** Delete keywords by simply clicking buttons.

## 🚀 Deployment on Render.com (24/7 Online)

To keep the bot running 24/7 for free/cheap using Render, follow these steps:

### 1. Preparation
1. Fork this repository to your GitHub account.
2. Get your **API_ID** and **API_HASH** from [my.telegram.org](https://my.telegram.org).
3. Get your **BOT_TOKEN** from [@BotFather](https://t.me/BotFather).
4. **Generate Session String:**
   - Run `python generate_session.py` on your local computer.
   - Login with your phone number.
   - Copy the long code starting with `1BVts...`.

### 2. Render Setup
1. Create a new **Web Service** on Render.
2. Connect your GitHub repository.
3. Settings:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
4. **Environment Variables:** Add the following keys in the "Environment" tab:
   
   | Key | Value | Description |
   | :--- | :--- | :--- |
   | `API_ID` | `123456` | Your Telegram API ID |
   | `API_HASH` | `abc123...` | Your Telegram API Hash |
   | `BOT_TOKEN` | `123:ABC...` | Your Bot Token from BotFather |
   | `SESSION_STRING` | `1BVts...` | The code you got from generate_session.py |
   | `PYTHON_VERSION` | `3.10.0` | (Optional) To ensure compatibility |

### 3. 💾 Data Persistence (Important!)
On Render (and most cloud platforms), files are deleted when the bot restarts or you deploy a new version. **To keep your channel list safe:**

- **Option A (Free):** Use the **Backup** button in the bot settings before every update. After update, use **Import** to restore.
- **Option B (Automatic):** Add a **Disk** in Render settings:
  - **Mount Path:** `/opt/render/project/src`
  - This will ensure `bot_data.json` is never deleted.

## Local Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/siimsek/KeyWSniper.git
   cd KeyWSniper
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the bot:**
   ```bash
   python bot.py
   ```

## Disclaimer
This tool is for educational purposes only. Use it responsibly and in accordance with Telegram's Terms of Service.
