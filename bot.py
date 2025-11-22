import logging
import json
import os
import asyncio
import re
from telethon import TelegramClient, events, Button
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==========================================
# CONFIGURATION
# ==========================================
# You can hardcode your credentials here OR use .env file
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION_NAME = 'userbot_session'

# Default: Your Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

DATA_FILE = "bot_data.json"
LOCALES_FILE = "locales.json"

# Logging configuration
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ==========================================
# DATA MANAGEMENT & LOCALIZATION
# ==========================================
class DataManager:
    def __init__(self):
        self.data_path = DATA_FILE
        self.locales_path = LOCALES_FILE
        self.data = self.load_json(self.data_path, {"channels": {}, "owner_id": None, "lang": "TR"})
        self.locales = self.load_json(self.locales_path, {})
        
        # State management (Like a State Machine)
        self.user_states = {}  # {user_id: {"state": "ADDING_CHANNEL", "temp_data": {...}}}

    def load_json(self, filepath, default):
        if not os.path.exists(filepath):
            return default
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"JSON Load Error ({filepath}): {e}")
            return default

    def save_data(self):
        try:
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"Data Save Error: {e}")

    def t(self, key, **kwargs):
        """Translation function"""
        lang = self.data.get("lang", "TR")
        text = self.locales.get(lang, {}).get(key, key)
        if kwargs:
            return text.format(**kwargs)
        return text

    def set_owner(self, user_id):
        self.data["owner_id"] = user_id
        self.save_data()

    def get_owner(self):
        return self.data.get("owner_id")

    def set_language(self, lang_code):
        self.data["lang"] = lang_code
        self.save_data()

    def add_keyword(self, channel, keyword):
        channels = self.data.setdefault("channels", {})
        channel = str(channel)
        if channel not in channels:
            channels[channel] = []
            
        # Case-insensitive check
        if keyword.lower() not in [k.lower() for k in channels[channel]]:
            channels[channel].append(keyword)
            self.save_data()
            return True
        return False

    def remove_keyword(self, channel, keyword):
        channels = self.data.get("channels", {})
        channel = str(channel)
        if channel in channels:
            initial_len = len(channels[channel])
            channels[channel] = [k for k in channels[channel] if k.lower() != keyword.lower()]
            if len(channels[channel]) < initial_len:
                if not channels[channel]:
                    del channels[channel]
                self.save_data()
                return True
        return False
    
    def import_data(self, new_data):
        """Merges data from a backup file"""
        count = 0
        if "channels" in new_data:
            for ch, keywords in new_data["channels"].items():
                for kw in keywords:
                    if self.add_keyword(ch, kw):
                        count += 1
        return count

    def get_all_channels(self):
        return self.data.get("channels", {})
    
    def get_keywords(self, channel_id=None, channel_username=None):
        channels = self.data.get("channels", {})
        keywords = []
        if channel_id and str(channel_id) in channels:
            keywords.extend(channels[str(channel_id)])
        if channel_username:
            u1 = f"@{channel_username}" if not channel_username.startswith("@") else channel_username
            u2 = channel_username.lstrip("@")
            if u1 in channels: keywords.extend(channels[u1])
            if u2 in channels: keywords.extend(channels[u2])
        return list(set(keywords))

dm = DataManager()

# Check if credentials exist either in env or as default fallback
if not API_ID or not API_HASH or not BOT_TOKEN:
    print("CRITICAL ERROR: Credentials missing. Please set them in .env file or hardcode them.")
    exit(1)

userbot = TelegramClient(SESSION_NAME, API_ID, API_HASH)
bot = TelegramClient('bot_session', API_ID, API_HASH)

# ==========================================
# BOT INTERFACE (ADVANCED MENU)
# ==========================================

async def get_main_menu():
    return [
        [Button.inline(dm.t("btn_add"), b"menu_add"), Button.inline(dm.t("btn_del"), b"menu_del")],
        [Button.inline(dm.t("btn_list"), b"menu_list"), Button.inline(dm.t("btn_settings"), b"menu_settings")],
        [Button.inline(dm.t("btn_help"), b"menu_help")]
    ]

@bot.on(events.NewMessage(pattern='/start'))
async def bot_start(event):
    sender = await event.get_sender()
    dm.set_owner(sender.id)
    
    await event.respond(
        dm.t("welcome", name=sender.first_name),
        buttons=await get_main_menu()
    )

@bot.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode('utf-8')
    owner_id = dm.get_owner()
    
    if event.sender_id != owner_id:
        await event.answer("⛔", alert=True)
        return

    # --- MAIN MENU ---
    if data == "main_menu":
        dm.user_states[owner_id] = {} # Clear state
        await event.edit(dm.t("menu_main"), buttons=await get_main_menu())

    # --- ADD WIZARD ---
    elif data == "menu_add":
        dm.user_states[owner_id] = {"state": "AWAIT_CHANNEL"}
        await event.edit(
            dm.t("add_step_1"),
            buttons=[[Button.inline(dm.t("btn_cancel"), b"main_menu")]]
        )
    
    # --- DELETE MENU (INTERACTIVE LIST) ---
    elif data == "menu_del":
        channels = dm.get_all_channels()
        if not channels:
            await event.edit(dm.t("list_empty"), buttons=[[Button.inline(dm.t("btn_back"), b"main_menu")]])
            return
            
        buttons = []
        for ch, kws in channels.items():
            for kw in kws:
                safe_kw = kw[:20] # Truncate long keywords
                btn_data = f"del_ask|{ch}|{kw}".encode('utf-8')
                buttons.append([Button.inline(f"❌ {ch} - {safe_kw}", btn_data)])
        
        buttons.append([Button.inline(dm.t("btn_back"), b"main_menu")])
        await event.edit(dm.t("del_menu"), buttons=buttons)

    elif data.startswith("del_ask|"):
        _, channel, keyword = data.split("|", 2)
        await event.edit(
            dm.t("del_confirm", channel=channel, keyword=keyword),
            buttons=[
                [Button.inline(dm.t("confirm_yes"), f"del_do|{channel}|{keyword}".encode('utf-8'))],
                [Button.inline(dm.t("confirm_no"), b"menu_del")]
            ]
        )

    elif data.startswith("del_do|"):
        _, channel, keyword = data.split("|", 2)
        dm.remove_keyword(channel, keyword)
        await event.edit(dm.t("del_success"), buttons=[[Button.inline(dm.t("btn_back"), b"menu_del")]])

    # --- LIST ---
    elif data == "menu_list":
        channels = dm.get_all_channels()
        if not channels:
            msg = dm.t("list_empty")
        else:
            msg = dm.t("list_header")
            for ch, kws in channels.items():
                msg += f"📢 `{ch}`\n"
                for k in kws:
                    msg += f"   🔹 {k}\n"
                msg += "\n"
        
        await event.edit(msg, buttons=[[Button.inline(dm.t("btn_back"), b"main_menu")]])

    # --- SETTINGS ---
    elif data == "menu_settings":
        buttons = [
            [Button.inline("🌐 Dil / Language", b"menu_lang")],
            [Button.inline(dm.t("btn_backup"), b"backup_create"), Button.inline(dm.t("btn_import"), b"backup_import")],
            [Button.inline(dm.t("btn_back"), b"main_menu")]
        ]
        await event.edit(dm.t("settings_menu"), buttons=buttons)

    elif data == "menu_lang":
        buttons = [
            [Button.inline("🇹🇷 Türkçe", b"set_lang_TR"), Button.inline("🇬🇧 English", b"set_lang_EN")],
            [Button.inline("🇷🇺 Русский", b"set_lang_RU"), Button.inline("🇩🇪 Deutsch", b"set_lang_DE")],
            [Button.inline(dm.t("btn_back"), b"menu_settings")]
        ]
        await event.edit(dm.t("settings_lang"), buttons=buttons)

    elif data.startswith("set_lang_"):
        lang_code = data.split("_")[2]
        dm.set_language(lang_code)
        await event.edit(dm.t("lang_set"), buttons=[[Button.inline(dm.t("btn_back"), b"menu_settings")]])
        
    elif data == "menu_help":
        await event.edit(
            "KeyWSniper v1.0\nCreated by @siimsek\nGitHub: https://github.com/siimsek/KeyWSniper", 
            buttons=[[Button.inline(dm.t("btn_back"), b"main_menu")]]
        )

    # --- BACKUP AND IMPORT ---
    elif data == "backup_create":
        # Create temp file
        backup_file = "bot_backup.json"
        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                # Backup only channels
                json.dump({"channels": dm.data.get("channels", {})}, f, ensure_ascii=False, indent=4)
            
            await event.client.send_file(
                owner_id, 
                backup_file, 
                caption=dm.t("backup_caption")
            )
            os.remove(backup_file) # Cleanup
        except Exception as e:
            logging.error(f"Backup Error: {e}")
        
        await event.answer("✅")

    elif data == "backup_import":
        dm.user_states[owner_id] = {"state": "AWAIT_IMPORT"}
        await event.edit(
            dm.t("import_intro"),
            buttons=[[Button.inline(dm.t("btn_cancel"), b"menu_settings")]]
        )

# --- LISTEN FOR TEXT/FILE INPUTS (FOR WIZARD) ---
@bot.on(events.NewMessage())
async def input_handler(event):
    # Only from owner and private chat
    if event.sender_id != dm.get_owner() or not event.is_private:
        return
    
    # Ignore commands (/start etc.)
    if event.message.message and event.message.message.startswith("/"):
        return

    state_data = dm.user_states.get(event.sender_id, {})
    state = state_data.get("state")

    # Import (File Check)
    if state == "AWAIT_IMPORT":
        if event.message.file:
            try:
                file_path = await event.download_media()
                with open(file_path, 'r', encoding='utf-8') as f:
                    new_data = json.load(f)
                
                count = dm.import_data(new_data)
                os.remove(file_path)
                dm.user_states[event.sender_id] = {} # Reset state
                
                await event.respond(
                    f"{dm.t('import_success')} (+{count})",
                    buttons=[[Button.inline(dm.t("btn_back"), b"menu_settings")]]
                )
            except Exception as e:
                await event.respond(
                    f"{dm.t('import_error')}\nError: {str(e)}",
                    buttons=[[Button.inline(dm.t("btn_cancel"), b"menu_settings")]]
                )
        else:
            await event.respond(dm.t("import_intro"))
        return

    # Add Channel (Text Check)
    if state == "AWAIT_CHANNEL":
        channel_input = event.message.message.strip()
        
        # Format channel input
        match = re.search(r"(?:t|telegram)\.me/(?P<username>[\w_]+)", channel_input)
        if match:
            channel_input = f"@{match.group('username')}"
        elif not channel_input.startswith("@") and not re.match(r"^-?\d+$", channel_input):
             channel_input = f"@{channel_input}"

        dm.user_states[event.sender_id] = {"state": "AWAIT_KEYWORD", "channel": channel_input}
        
        await event.respond(
            dm.t("add_step_2", channel=channel_input),
            buttons=[[Button.inline(dm.t("btn_cancel"), b"main_menu")]]
        )

    elif state == "AWAIT_KEYWORD":
        keyword = event.message.message.strip()
        channel = state_data.get("channel")
        
        if dm.add_keyword(channel, keyword):
            msg = dm.t("add_success", channel=channel, keyword=keyword)
        else:
            msg = dm.t("add_fail_exist")
            
        dm.user_states[event.sender_id] = {}
        
        await event.respond(msg, buttons=[
            [Button.inline(dm.t("btn_add"), b"menu_add")], # Add again
            [Button.inline(dm.t("btn_back"), b"main_menu")]
        ])

# ==========================================
# USERBOT LISTENER (BACKGROUND)
# ==========================================
@userbot.on(events.NewMessage())
async def channel_watcher(event):
    if not event.is_channel and not event.is_group:
        return

    chat = await event.get_chat()
    chat_id = str(chat.id)
    chat_username = getattr(chat, 'username', None)
    chat_title = getattr(chat, 'title', 'Channel')

    keywords = dm.get_keywords(channel_id=chat_id, channel_username=chat_username)
    if not keywords and not chat_id.startswith("-100"):
         keywords = dm.get_keywords(channel_id=f"-100{chat_id}")
    if not keywords and chat_id.startswith("-100"):
         keywords = dm.get_keywords(channel_id=chat_id[4:])

    if not keywords:
        return

    text = event.message.message or ""
    if not text and event.message.media:
         text = getattr(event.message, 'message', "") or ""

    if not text:
        return

    text_lower = text.lower()
    matched_keyword = None
    
    # Partial match check
    for k in keywords:
        if k.lower() in text_lower:
            matched_keyword = k
            break
    
    if matched_keyword:
        print(f"✅ MATCH: {chat_title} -> {matched_keyword}")
        owner_id = dm.get_owner()
        if owner_id:
            try:
                # Bot Notification
                msg_link = f"https://t.me/{chat_username}/{event.id}" if chat_username else f"https://t.me/c/{chat_id}/{event.id}"
                display_text = text[:3000] + "..." if len(text) > 3000 else text
                
                notification_text = (
                    f"{dm.t('notification_title', keyword=matched_keyword.upper())}\n\n"
                    f"{dm.t('notification_channel', channel=chat_title)}\n"
                    f"🔗 [Link]({msg_link})\n"
                    f"──────────────\n"
                    f"{display_text}"
                )
                
                await bot.send_message(
                    owner_id,
                    notification_text,
                    link_preview=False,
                    buttons=[[Button.url(dm.t("btn_goto"), msg_link)]]
                )
            except Exception as e:
                logging.error(f"Notification Error: {e}")

async def main():
    print("System starting...")
    print("1. Connecting Userbot...")
    await userbot.start()
    print("2. Connecting Bot Interface...")
    await bot.start(bot_token=BOT_TOKEN)
    print("✅ System Ready!")
    await asyncio.gather(userbot.run_until_disconnected(), bot.run_until_disconnected())

if __name__ == '__main__':
    # Asyncio loop fix for Python 3.10+
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
