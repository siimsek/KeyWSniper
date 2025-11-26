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
        """
        Optimized keyword retrieval using cache.
        """
        keywords = []
        
        # Check by ID
        if channel_id and str(channel_id) in self._keywords_cache:
            keywords.extend(self._keywords_cache[str(channel_id)])
            
        # Check by Username
        if channel_username:
            u1 = f"@{channel_username}" if not channel_username.startswith("@") else channel_username
            u2 = channel_username.lstrip("@")
            
            if u1 in self._keywords_cache: keywords.extend(self._keywords_cache[u1])
            if u2 in self._keywords_cache: keywords.extend(self._keywords_cache[u2])
            
        return list(set(keywords))

# Global DataManager instance
dm = DataManager()
