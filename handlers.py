# -*- coding: utf-8 -*-
import re
import os
import json
import logging
from telethon import events, Button
from telethon.errors import MessageNotModifiedError
from database import dm
from config import VERSION

# ==========================================
# BOT INTERFACE (ADVANCED MENU)
# ==========================================

async def get_main_menu():
    return [
        [Button.inline(dm.t("btn_add"), b"menu_add"), Button.inline(dm.t("btn_list"), b"menu_list")],
        [Button.inline(dm.t("btn_settings"), b"menu_settings"), Button.inline(dm.t("btn_help"), b"menu_help")]
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
                link_preview=False,
                buttons=[[Button.inline(dm.t("btn_cancel"), b"main_menu")]]
            )
        
        # --- LIST MENU (INTERACTIVE) ---
        elif data == "menu_list":
            channels = dm.get_all_channels()
            if not channels:
                await event.edit(dm.t("list_empty"), buttons=[[Button.inline(dm.t("btn_back"), b"main_menu")]])
                return
                
            buttons = []
            for ch, kws in channels.items():
                for kw_entry in kws:
                    # Handle both string and object formats
                    if isinstance(kw_entry, dict):
                        kw = kw_entry["keyword"]
                    else:
                        kw = kw_entry
                        
                    safe_kw = kw[:20] # Truncate long keywords
                    # Data format: view_track|CHANNEL|KEYWORD
                    btn_data = f"view_track|{ch}|{kw}".encode('utf-8')
                    buttons.append([Button.inline(f"🔎 {ch} - {safe_kw}", btn_data)])
            
            buttons.append([Button.inline(dm.t("btn_back"), b"main_menu")])
            await event.edit(dm.t("list_header"), buttons=buttons)

        # --- VIEW TRACK DETAIL ---
        elif data.startswith("view_track|"):
            _, channel, keyword = data.split("|", 2)
            data_entry = dm.get_keyword_data(channel, keyword)
            
            if not data_entry:
                await event.answer(dm.t("error_not_found"), alert=True)
                await event.edit(dm.t("list_header"), buttons=[[Button.inline(dm.t("btn_back"), b"menu_list")]])
                return

            note = data_entry.get("note", "-")
            
            msg = dm.t("track_detail", channel=channel, keyword=keyword, note=note)
            
            buttons = [
                [Button.inline(dm.t("btn_edit_channel"), f"edit_ask|channel|{channel}|{keyword}".encode('utf-8'))],
                [Button.inline(dm.t("btn_edit_keyword"), f"edit_ask|keyword|{channel}|{keyword}".encode('utf-8'))],
                [Button.inline(dm.t("btn_edit_note"), f"edit_ask|note|{channel}|{keyword}".encode('utf-8'))],
                [Button.inline(dm.t("btn_del"), f"del_ask|{channel}|{keyword}".encode('utf-8'))],
                [Button.inline(dm.t("btn_back"), b"menu_list")]
            ]
            await event.edit(msg, link_preview=False, buttons=buttons)

        # --- DELETE CONFIRMATION ---
        elif data.startswith("del_ask|"):
            _, channel, keyword = data.split("|", 2)
            await event.edit(
                dm.t("del_confirm", channel=channel, keyword=keyword),
                buttons=[
                    [Button.inline(dm.t("confirm_yes"), f"del_do|{channel}|{keyword}".encode('utf-8'))],
                    [Button.inline(dm.t("confirm_no"), f"view_track|{channel}|{keyword}".encode('utf-8'))]
                ]
            )

        elif data.startswith("del_do|"):
            _, channel, keyword = data.split("|", 2)
            dm.remove_keyword(channel, keyword)
            await event.edit(dm.t("del_success"), buttons=[[Button.inline(dm.t("btn_back"), b"menu_list")]])

        # --- EDIT ASK ---
        elif data.startswith("edit_ask|"):
            _, field, channel, keyword = data.split("|", 3)
            
            prompt_key = f"edit_prompt_{field}"
            dm.user_states[owner_id] = {
                "state": "AWAIT_EDIT_INPUT",
                "field": field,
                "channel": channel,
                "keyword": keyword
            }
            
            await event.edit(
                dm.t(prompt_key, channel=channel, keyword=keyword),
                buttons=[[Button.inline(dm.t("btn_cancel"), f"view_track|{channel}|{keyword}".encode('utf-8'))]]
            )



        # --- SETTINGS ---
        elif data == "menu_settings":
            buttons = [
                [Button.inline("🌐 Dil / Language", b"menu_lang")],
                [Button.inline(dm.t("btn_dnd"), b"menu_dnd")],
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
                f"🛡️ **KeyWSniper v{VERSION}**\n\n"
                "🚀 **Dev:** @siimsek\n"
                "📂 **GitHub:** [Source Code](https://github.com/siimsek/KeyWSniper)\n\n",
                link_preview=False,
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

        # --- DND MENU ---
        elif data == "menu_dnd":
            dnd = dm.get_dnd()
            status = dm.t("dnd_enabled") if dnd["enabled"] else dm.t("dnd_disabled")
            
            buttons = [
                [Button.inline(dm.t("btn_disable") if dnd["enabled"] else dm.t("btn_enable"), b"dnd_toggle")],
                [Button.inline(dm.t("btn_set_time"), b"dnd_set_time")],
                [Button.inline(dm.t("btn_back"), b"menu_settings")]
            ]
            
            await event.edit(
                dm.t("dnd_menu", status=status, start=dnd["start"], end=dnd["end"]),
                buttons=buttons
            )

        elif data == "dnd_toggle":
            dnd = dm.get_dnd()
            dm.set_dnd(enabled=not dnd["enabled"])
            # Refresh menu
            dnd = dm.get_dnd()
            status = dm.t("dnd_enabled") if dnd["enabled"] else dm.t("dnd_disabled")
            buttons = [
                [Button.inline(dm.t("btn_disable") if dnd["enabled"] else dm.t("btn_enable"), b"dnd_toggle")],
                [Button.inline(dm.t("btn_set_time"), b"dnd_set_time")],
                [Button.inline(dm.t("btn_back"), b"menu_settings")]
            ]
            await event.edit(
                dm.t("dnd_menu", status=status, start=dnd["start"], end=dnd["end"]),
                buttons=buttons
            )

        elif data == "dnd_set_time":
            dm.user_states[owner_id] = {"state": "AWAIT_DND_TIME"}
            await event.edit(
                dm.t("dnd_time_prompt"),
                buttons=[[Button.inline(dm.t("btn_cancel"), b"menu_dnd")]]
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

        # DND Time Setting
        if state == "AWAIT_DND_TIME":
            time_input = event.message.message.strip()
            # Validate format HH:MM-HH:MM
            match = re.match(r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]-([0-1]?[0-9]|2[0-3]):[0-5][0-9]$", time_input)
            
            if match:
                start, end = time_input.split("-")
                dm.set_dnd(start=start, end=end)
                dm.user_states[event.sender_id] = {} # Reset
                
                await event.respond(
                    dm.t("dnd_time_success", start=start, end=end),
                    buttons=[[Button.inline(dm.t("btn_back"), b"menu_dnd")]]
                )
            else:
                dm.user_states[event.sender_id]["processing"] = False # Unlock to try again
                await event.respond(
                    dm.t("dnd_time_error"),
                    buttons=[[Button.inline(dm.t("btn_cancel"), b"menu_dnd")]]
                )
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
                link_preview=False,
                buttons=[[Button.inline(dm.t("btn_cancel"), b"main_menu")]]
            )

        elif state == "AWAIT_KEYWORD":
            keyword = event.message.message.strip()
            channel = state_data.get("channel")
            
            # Move to next step: Ask for Note
            dm.user_states[event.sender_id] = {
                "state": "AWAIT_NOTE", 
                "channel": channel, 
                "keyword": keyword
            }
            
            await event.respond(
                dm.t("add_step_3", keyword=keyword),
                link_preview=False,
                buttons=[[Button.inline(dm.t("btn_cancel"), b"main_menu")]]
            )

        elif state == "AWAIT_NOTE":
            note = event.message.message.strip()
            # If user sends "-" or "skip", we can treat as empty, but let's just take input as is.
            
            channel = state_data.get("channel")
            keyword = state_data.get("keyword")
            
            if dm.add_keyword(channel, keyword, note):
                msg = dm.t("add_success", channel=channel, keyword=keyword, note=note)
            else:
                msg = dm.t("add_fail_exist")
                
            dm.user_states[event.sender_id] = {}
            
            await event.respond(msg, link_preview=False, buttons=[
                [Button.inline(dm.t("btn_add"), b"menu_add")], # Add again
                [Button.inline(dm.t("btn_back"), b"main_menu")]
            ])

        # Edit Input
        elif state == "AWAIT_EDIT_INPUT":
            new_value = event.message.message.strip()
            field = state_data.get("field")
            channel = state_data.get("channel")
            keyword = state_data.get("keyword")
            
            success = False
            
            if field == "channel":
                # Format channel input
                match = re.search(r"(?:t|telegram)\.me/(?P<username>[\w_]+)", new_value)
                if match:
                    new_value = f"@{match.group('username')}"
                elif not new_value.startswith("@") and not re.match(r"^-?\d+$", new_value):
                     new_value = f"@{new_value}"
                     
                if dm.edit_channel(channel, new_value):
                    channel = new_value # Update for redirect
                    success = True
            
            elif field == "keyword":
                if dm.edit_keyword(channel, keyword, new_value):
                    keyword = new_value # Update for redirect
                    success = True
                    
            elif field == "note":
                if dm.edit_note(channel, keyword, new_value):
                    success = True
            
            dm.user_states[event.sender_id] = {}
            
            if success:
                await event.respond(
                    dm.t("edit_success"),
                    link_preview=False,
                    buttons=[[Button.inline(dm.t("btn_back"), f"view_track|{channel}|{keyword}".encode('utf-8'))]]
                )
            else:
                await event.respond(
                    dm.t("edit_fail"),
                    buttons=[[Button.inline(dm.t("btn_cancel"), f"view_track|{channel}|{keyword}".encode('utf-8'))]]
                )
            
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
    matched_entry = None
    
    # Partial match check
    for entry in keywords:
        # keywords is now a list of objects from get_keywords
        kw = entry["keyword"]
        if kw.lower() in text_lower:
            matched_entry = entry
            break
    
    if matched_entry:
        matched_keyword = matched_entry["keyword"]
        matched_note = matched_entry.get("note", "")
        
        print(f"✅ MATCH: {chat_title} -> {matched_keyword}")
        owner_id = dm.get_owner()
        if owner_id:
            try:
                # Bot Notification
                msg_link = f"https://t.me/{chat_username}/{event.id}" if chat_username else f"https://t.me/c/{chat_id}/{event.id}"
                display_text = text[:3000] + "..." if len(text) > 3000 else text
                
                # Format:
                # Caught: KEYWORD
                # Note (if exists)
                # Source
                # Link
                # Message
                
                note_part = f"\n📝 **Not:** {matched_note}\n" if matched_note else ""
                
                notification_text = (
                    f"{dm.t('notification_title', keyword=matched_keyword.upper())}\n\n"
                    f"{note_part}"
                    f"{dm.t('notification_channel', channel=chat_title)}\n"
                    f"──────────────\n"
                    f"{display_text}"
                )
                
                # Check DND
                if dm.is_dnd_active():
                    print(f"🌙 DND Active. Silencing notification for {matched_keyword}")
                    return

                await bot_client.send_message(
                    owner_id,
                    notification_text,
                    link_preview=False,
                    buttons=[[Button.url(dm.t("btn_goto"), msg_link)]]
                )
            except Exception as e:
                logging.error(f"Notification Error: {e}")
