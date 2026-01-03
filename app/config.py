# Cloudflare Worker URL
WORKER_URL = "https://free.baloenk.my.id"

class ConfigManager:
    @staticmethod
    def get_worker_url() -> str:
        return WORKER_URL
