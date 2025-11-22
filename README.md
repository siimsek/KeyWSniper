# KeyWSniper

This project is a powerful Telegram monitoring tool that combines a **Userbot** (to read channels without admin rights) and a **Bot Interface** (for easy management via menus).

## Features
- 🕵️ **Userbot:** Monitors channels you are a member of (no admin rights needed).
- 🤖 **Bot Interface:** Manage keywords and channels with an easy-to-use menu.
- 🌐 **Multi-Language:** Supports English, Turkish, Russian, and German.
- 🔔 **Instant Notifications:** Get notified immediately when a keyword is mentioned.
- 📦 **Backup & Restore:** Export and import your tracking list.
- 🗑️ **Interactive Deletion:** Delete keywords by simply clicking buttons.

## Prerequisites
1. **Python 3.8+**
2. **Telegram API ID & Hash:** Get them from [my.telegram.org](https://my.telegram.org).
3. **Bot Token:** Get one from [@BotFather](https://t.me/BotFather).

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/siimsek/KeyWSniper.git
   cd KeyWSniper
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration:**
   - Open the `.env` file.
   - Fill in your credentials:
     ```ini
     API_ID=12345678
     API_HASH=your_api_hash_here
     BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
     ```

4. **Run the bot:**
   ```bash
   python bot.py
   ```
   - On the first run, it will ask for your phone number and the code sent to your Telegram account to authorize the Userbot.

## Usage
1. Open your bot in Telegram (`/start`).
2. Use the **Add Track** button to follow a channel and keyword.
   - You can use channel username (`@channel`), link (`t.me/channel`), or ID (`-100...`).
3. The bot will send you a notification message whenever a matching keyword is found in the monitored channels.

## Disclaimer
This tool is for educational purposes only. Use it responsibly and in accordance with Telegram's Terms of Service.
