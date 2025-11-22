from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

if not API_ID or not API_HASH:
    print("Error: Please make sure API_ID and API_HASH are set in your .env file.")
    exit()

print("--- TELEGRAM SESSION GENERATOR ---")
print("Connecting to Telegram servers...")
print("You will be asked to enter your phone number and the code you receive.")
print("------------------------------------")

with TelegramClient(StringSession(), int(API_ID), API_HASH) as client:
    session_string = client.session.save()
    print("\n⬇️ COPY THE CODE BELOW (Add this to Render) ⬇️\n")
    print(session_string)
    print("\n⬆️ COPY THE CODE ABOVE ⬆️")
    print("\nAdd this code to Render.com Environment Variables as 'SESSION_STRING'.")
