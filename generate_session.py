import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

# Load .env if exists
load_dotenv()

print("="*50)
print("🔐 Telegram String Session Generator")
print("="*50)
print("This tool generates the 'SESSION_STRING' required to keep your session")
print("active on platforms like Render.\n")

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

if not api_id or not api_hash:
    print("⚠️ API_ID or API_HASH not found in .env file.")
    print("Please enter them manually below:")
    api_id = input("API ID: ").strip()
    api_hash = input("API HASH: ").strip()

try:
    with TelegramClient(StringSession(), int(api_id), api_hash) as client:
        print("\n✅ Login Successful!")
        session_string = client.session.save()
        print("\n👇 COPY THE CODE BELOW 👇\n")
        print(session_string)
        print("\n👆 COPY THE CODE ABOVE 👆\n")
        print("Add this to 'Environment Variables' on Render.com:")
        print("Key: SESSION_STRING")
        print("Value: (The code you copied)")
        
        # Optional: Save to file
        with open("session_string.txt", "w") as f:
            f.write(session_string)
        print("\n(Also saved to session_string.txt)")
        
except Exception as e:
    print(f"\n❌ Error occurred: {e}")

input("\nPress Enter to exit...")
