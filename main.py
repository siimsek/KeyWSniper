# -*- coding: utf-8 -*-
import logging
import asyncio
import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from aiohttp import web

from config import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING, SESSION_NAME, PORT
from handlers import bot_start, callback_handler, input_handler, channel_watcher

# Logging configuration
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Check if credentials exist
if not API_ID or not API_HASH or not BOT_TOKEN:
    print("CRITICAL ERROR: Credentials missing. Please set them in .env file or hardcode them.")
    exit(1)

# Initialize Clients
if SESSION_STRING:
    print("💻 Using String Session for Auth...")
    userbot = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
else:
    print("🏠 Using Local File Session...")
    userbot = TelegramClient(SESSION_NAME, API_ID, API_HASH)

bot = TelegramClient('bot_session', API_ID, API_HASH)

# Register Handlers
bot.add_event_handler(bot_start, events.NewMessage(pattern='/start'))
bot.add_event_handler(callback_handler, events.CallbackQuery)
bot.add_event_handler(input_handler, events.NewMessage())

# Userbot Handler
# We need to pass the bot client to the watcher so it can send notifications
@userbot.on(events.NewMessage())
async def userbot_watcher_wrapper(event):
    await channel_watcher(event, bot)

# ==========================================
# DUMMY WEB SERVER (FOR RENDER HEALTH CHECK)
# ==========================================
async def handle_health(request):
    return web.Response(text="KeyWSniper is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_health)
    app.router.add_get('/health', handle_health)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"🌍 Web server started on port {PORT}")

async def main():
    print("System starting...")
    
    # Start Web Server for Render
    await start_web_server()
    
    print("1. Connecting Userbot...")
    await userbot.connect()
    if not await userbot.is_user_authorized():
        print("⚠️ Userbot NOT authorized. Interactive login might be required.")
        print("Please check your SESSION_STRING if you expected automatic login.")
    else:
        print("✅ Userbot Authorized via Session.")
        
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
