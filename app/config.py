import json
import os
from typing import Optional

CONFIG_FILE = "config.json"

class ConfigManager:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../", CONFIG_FILE)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def save_worker_url(self, url: str):
        self.config['worker_url'] = url.rstrip('/')
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get_worker_url(self) -> Optional[str]:
        return self.config.get('worker_url')
