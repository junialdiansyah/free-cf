import json
import os
from typing import Dict, Any, Optional

HISTORY_FILE = "history.json"
PROFILES_FILE = "profiles.json"

class HistoryManager:
    @staticmethod
    def save_last_config(config: Dict[str, Any]):
        """Save the last used configuration to history.json"""
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Warning: Failed to save history: {e}")

    @staticmethod
    def load_last_config() -> Optional[Dict[str, Any]]:
        """Load the last used configuration from history.json"""
        if not os.path.exists(HISTORY_FILE):
            return None
            
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    @staticmethod
    def save_profile(name: str, config: Dict[str, Any]) -> bool:
        """Save a configuration as a named profile"""
        profiles = HistoryManager.load_profiles()
        profiles[name] = config
        
        try:
            with open(PROFILES_FILE, "w", encoding="utf-8") as f:
                json.dump(profiles, f, indent=4)
            return True
        except Exception as e:
            print(f"Warning: Failed to save profile: {e}")
            return False

    @staticmethod
    def load_profiles() -> Dict[str, Dict[str, Any]]:
        """Load all saved profiles"""
        if not os.path.exists(PROFILES_FILE):
            return {}
            
        try:
            with open(PROFILES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def delete_profile(name: str) -> bool:
        """Delete a named profile"""
        profiles = HistoryManager.load_profiles()
        if name in profiles:
            del profiles[name]
            try:
                with open(PROFILES_FILE, "w", encoding="utf-8") as f:
                    json.dump(profiles, f, indent=4)
                return True
            except Exception:
                return False
        return False
