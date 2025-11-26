import re
import os
import json
import logging
from telethon import events, Button
from telethon.errors import MessageNotModifiedError
from database import dm

# ==========================================
# BOT INTERFACE (ADVANCED MENU)
# ==========================================

async def get_main_menu():
    return [
        [Button.inline(dm.t("btn_add"), b"menu_add"), Button.inline(dm.t("btn_del"), b"menu_del")],
        [Button.inline(dm.t("btn_list"), b"menu_list"), Button.inline(dm.t("btn_settings"), b"menu_settings")],
        [Button.inline(dm.t("btn_help"), b"menu_help")]
    ]

async def bot_start(event):
    sender = await event.get_sender()
    dm.set_owner(sender.id)
    
    await event.respond(
        dm.t("welcome", name=sender.first_name),
        buttons=await get_main_menu()
    )

async def callback_handler(event):
    try:
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
                "KeyWSniper v1.6.2\nCreated by @siimsek\nGitHub: https://github.com/siimsek/KeyWSniper", 
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

    except MessageNotModifiedError:
        # Ignore if message content hasn't changed
        pass
    except Exception as e:
        logging.error(f"Callback Error: {e}")

# --- LISTEN FOR TEXT/FILE INPUTS (FOR WIZARD) ---
async def input_handler(event):
    # Only from owner and private chat
    if event.sender_id != dm.get_owner() or not event.is_private:
        return
    
    # Ignore commands (/start etc.)
    if event.message.message and event.message.message.startswith("/"):
        return

    state_data = dm.user_states.get(event.sender_id, {})
    state = state_data.get("state")

    if not state: return

    # Global Lock Check
    if state_data.get("processing"):
        return
    
    dm.user_states[event.sender_id]["processing"] = True

    try:
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
                        buttons=[[Button.inline(dm.t("btn_back"), b"main_menu")]]
                    )
                except Exception as e:
                    dm.user_states[event.sender_id]["processing"] = False # Unlock on error
                    await event.respond(
                        f"{dm.t('import_error')}\nError: {str(e)}",
                        buttons=[[Button.inline(dm.t("btn_cancel"), b"menu_settings")]]
                    )
            else:
                dm.user_states[event.sender_id]["processing"] = False # Unlock
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
            
    except Exception as e:
        logging.error(f"Input Handler Error: {e}")
        # Release lock in case of critical error
        if event.sender_id in dm.user_states:
             dm.user_states[event.sender_id]["processing"] = False

# ==========================================
# USERBOT LISTENER (BACKGROUND)
# ==========================================
async def channel_watcher(event, bot_client):
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
                
                await bot_client.send_message(
                    owner_id,
                    notification_text,
                    link_preview=False,
                    buttons=[[Button.url(dm.t("btn_goto"), msg_link)]]
                )
            except Exception as e:
                logging.error(f"Notification Error: {e}")
