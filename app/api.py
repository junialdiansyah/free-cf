import requests
from typing import Dict, Any, List, Optional
import urllib.parse

class WorkerAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    def get_regions(self) -> Dict[str, Any]:
        """Fetch available regions from the worker."""
        try:
            response = requests.get(f"{self.base_url}/api/v1/regions", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def get_my_ip(self) -> Dict[str, Any]:
        """Fetch client IP details."""
        try:
            response = requests.get(f"{self.base_url}/api/v1/myip", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def generate_config(self, 
                        bug_host: str, 
                        protocols: List[str], 
                        ports: List[str], 
                        regions: List[str], 
                        orgs: List[str], 
                        limit: int = 10,
                        format_type: str = 'raw') -> str:
        
        params = {
            "domain": bug_host,
            "vpn": ",".join(protocols),
            "port": ",".join(ports),
            "limit": limit,
            "format": format_type,
            "cc": ",".join(regions) if "ALL" not in regions else "",
            "org": ",".join(orgs) if "ALL" not in orgs else ""
        }
        
        # Clean up empty params
        params = {k: v for k, v in params.items() if v}
        
        query_string = urllib.parse.urlencode(params)
        url = f"{self.base_url}/api/v1/sub?{query_string}"
        
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            return f"Error generating config: {str(e)}"
