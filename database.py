import json
import os
import logging
from config import DATA_FILE, LOCALES_FILE

class DataManager:
    def __init__(self):
        self.data_path = DATA_FILE
        self.locales_path = LOCALES_FILE
        self.data = self.load_json(self.data_path, {"channels": {}, "owner_id": None, "lang": "TR"})
        self.locales = self.load_json(self.locales_path, {})
        
        # State management (Like a State Machine)
        self.user_states = {}  # {user_id: {"state": "ADDING_CHANNEL", "temp_data": {...}}}
        
        # Cache for keywords to optimize matching
        self._keywords_cache = {} # {channel_id: [keywords]}
        self._rebuild_cache()

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
            # Update cache after saving
            self._rebuild_cache()
        except Exception as e:
            logging.error(f"Data Save Error: {e}")

    def _rebuild_cache(self):
        """Rebuilds the keyword cache for faster lookup."""
        self._keywords_cache = self.data.get("channels", {}).copy()

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

    def add_keyword(self, channel, keyword, note=""):
        channels = self.data.setdefault("channels", {})
        channel = str(channel)
        if channel not in channels:
            channels[channel] = []
            
        # Helper to get keyword string from entry
        def get_kw_str(entry):
            return entry["keyword"] if isinstance(entry, dict) else entry

        # Check if keyword exists (case-insensitive)
        existing_keywords = [get_kw_str(k).lower() for k in channels[channel]]
        
        if keyword.lower() not in existing_keywords:
            # Store as object: {"keyword": "foo", "note": "bar"}
            channels[channel].append({"keyword": keyword, "note": note})
            self.save_data()
            return True
        return False

    def remove_keyword(self, channel, keyword):
        channels = self.data.get("channels", {})
        channel = str(channel)
        if channel in channels:
            initial_len = len(channels[channel])
            
            new_list = []
            for entry in channels[channel]:
                k_str = entry["keyword"] if isinstance(entry, dict) else entry
                if k_str.lower() != keyword.lower():
                    new_list.append(entry)
            
            channels[channel] = new_list
            
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
            for ch, items in new_data["channels"].items():
                for item in items:
                    # Handle both old string format and new dict format
                    if isinstance(item, dict):
                        kw = item.get("keyword")
                        note = item.get("note", "")
                    else:
                        kw = item
                        note = ""
                        
                    if kw and self.add_keyword(ch, kw, note):
                        count += 1
        return count

    def edit_channel(self, old_channel, new_channel):
        channels = self.data.get("channels", {})
        old_channel = str(old_channel)
        new_channel = str(new_channel)
        
        if old_channel not in channels:
            return False
            
        # If new channel exists, merge keywords
        if new_channel in channels:
            # This is complex, for simplicity in this version:
            # Move all keywords. If keyword exists in target, skip or duplicate?
            # Let's append and let user clean up if needed.
            channels[new_channel].extend(channels[old_channel])
        else:
            channels[new_channel] = channels[old_channel]
            
        del channels[old_channel]
        self.save_data()
        return True

    def edit_keyword(self, channel, old_keyword, new_keyword):
        channels = self.data.get("channels", {})
        channel = str(channel)
        if channel not in channels: return False
        
        # Check if new keyword already exists
        for entry in channels[channel]:
            k_str = entry["keyword"] if isinstance(entry, dict) else entry
            if k_str.lower() == new_keyword.lower():
                return False # Already exists
        
        found = False
        for i, entry in enumerate(channels[channel]):
            k_str = entry["keyword"] if isinstance(entry, dict) else entry
            if k_str.lower() == old_keyword.lower():
                if isinstance(entry, dict):
                    channels[channel][i]["keyword"] = new_keyword
                else:
                    channels[channel][i] = {"keyword": new_keyword, "note": ""}
                found = True
                break
        
        if found:
            self.save_data()
            return True
        return False

    def edit_note(self, channel, keyword, new_note):
        channels = self.data.get("channels", {})
        channel = str(channel)
        if channel not in channels: return False
        
        found = False
        for i, entry in enumerate(channels[channel]):
            k_str = entry["keyword"] if isinstance(entry, dict) else entry
            if k_str.lower() == keyword.lower():
                if isinstance(entry, dict):
                    channels[channel][i]["note"] = new_note
                else:
                    channels[channel][i] = {"keyword": k_str, "note": new_note}
                found = True
                break
        
        if found:
            self.save_data()
            return True
        return False

    def get_keyword_data(self, channel, keyword):
        channels = self.data.get("channels", {})
        channel = str(channel)
        if channel not in channels: return None
        
        for entry in channels[channel]:
            k_str = entry["keyword"] if isinstance(entry, dict) else entry
            if k_str.lower() == keyword.lower():
                if isinstance(entry, dict):
                    return entry
                else:
                    return {"keyword": k_str, "note": ""}
        return None

    def get_all_channels(self):
        return self.data.get("channels", {})
    
    def get_keywords(self, channel_id=None, channel_username=None):
        """
        Optimized keyword retrieval using cache.
        Returns list of objects: [{"keyword": "...", "note": "..."}]
        """
        raw_items = []
        
        # Check by ID
        if channel_id and str(channel_id) in self._keywords_cache:
            raw_items.extend(self._keywords_cache[str(channel_id)])
            
        # Check by Username
        if channel_username:
            u1 = f"@{channel_username}" if not channel_username.startswith("@") else channel_username
            u2 = channel_username.lstrip("@")
            
            if u1 in self._keywords_cache: raw_items.extend(self._keywords_cache[u1])
            if u2 in self._keywords_cache: raw_items.extend(self._keywords_cache[u2])
            
        # Normalize to objects and deduplicate
        # Deduplication based on keyword string to avoid duplicates from multiple ID matches
        seen_kws = set()
        normalized_items = []
        
        for item in raw_items:
            if isinstance(item, dict):
                kw = item["keyword"]
                note = item.get("note", "")
            else:
                kw = item
                note = ""
            
            if kw.lower() not in seen_kws:
                seen_kws.add(kw.lower())
                normalized_items.append({"keyword": kw, "note": note})
                
        return normalized_items

# Global DataManager instance
dm = DataManager()
