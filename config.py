import os
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
# Session String (For Render/Cloud)
SESSION_STRING = os.getenv("SESSION_STRING", "")

DATA_FILE = "bot_data.json"
LOCALES_FILE = "locales.json"

# Web Server Port
PORT = int(os.getenv("PORT", 8080))

# Bot Version
VERSION = "1.7.2"
