import json
import os
from typing import Dict, Any, Optional

HISTORY_FILE = "history.json"

class HistoryManager:
    @staticmethod
    def save_last_config(config: Dict[str, Any]):
        """Save the last used configuration to history.json"""
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            # Silently fail or log better in a real app
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
