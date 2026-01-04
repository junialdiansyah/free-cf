import json
import urllib.parse
import datetime

def generate_singbox_config(links_text: str) -> str:
    """
    Parses VLESS/Trojan links and returns a Sing-box JSON configuration.
    """
    outbounds = []
    proxy_tags = []
    
    links = links_text.strip().split('\n')
    
    for link in links:
        link = link.strip()
        if not link:
            continue
            
        try:
            parsed = urllib.parse.urlparse(link)
            query = urllib.parse.parse_qs(parsed.query)
            tag = urllib.parse.unquote(parsed.fragment) if parsed.fragment else "proxy"
            
            # Ensure unique tags
            original_tag = tag
            counter = 1
            while tag in proxy_tags:
                tag = f"{original_tag} {counter}"
                counter += 1
            
            server = parsed.hostname
            port = parsed.port if parsed.port else 443
            
            # Common Transport Options (WS)
            path = query.get("path", ["/"])[0]
            host_header = query.get("host", [""])[0]
            sni = query.get("sni", [""])[0]
            
            if not sni: sni = host_header
            if not host_header: host_header = sni
            
            outbound = {}
            
            if parsed.scheme == "vless":
                uuid = parsed.username
                outbound = {
                    "type": "vless",
                    "tag": tag,
                    "server": server,
                    "server_port": port,
                    "uuid": uuid,
                    "tls": {
                        "enabled": True,
                        "server_name": sni,
                        "insecure": True
                    },
                    "transport": {
                        "type": "ws",
                        "path": path,
                        "headers": {
                            "Host": host_header
                        }
                    }
                }
                
            elif parsed.scheme == "trojan":
                password = parsed.username
                outbound = {
                    "type": "trojan",
                    "tag": tag,
                    "server": server,
                    "server_port": port,
                    "password": password,
                    "tls": {
                        "enabled": True,
                        "server_name": sni,
                        "insecure": True
                    },
                    "transport": {
                        "type": "ws",
                        "path": path,
                        "headers": {
                            "Host": host_header
                        }
                    }
                }
            
            if outbound:
                # Handle non-TLS ports (usually 80)
                if port == 80 or query.get("security", [""])[0] == "none":
                     if "tls" in outbound:
                         del outbound["tls"]
                
                outbounds.append(outbound)
                proxy_tags.append(tag)
                
        except Exception:
            continue

    # Create Structure
    # Selector Group
    selector = {
        "type": "selector",
        "tag": "SELECT",
        "outbounds": ["URLTEST"] + proxy_tags + ["DIRECT"]  # Added DIRECT for fallback
    }
    
    # URLTest Group
    urltest = {
        "type": "urltest",
        "tag": "URLTEST",
        "outbounds": proxy_tags,
        "url": "http://cp.cloudflare.com",
        "interval": "10m"
    }
    
    # Direct Outbound
    direct = {
        "type": "direct",
        "tag": "DIRECT"
    }
    
    # DNS Outbound (required for some setups)
    dns_out = {
        "type": "dns",
        "tag": "dns-out"
    }

    final_config = {
        "log": {
            "level": "info",
            "timestamp": True
        },
        "dns": {
            "servers": [
                {"tag": "google", "address": "8.8.8.8", "detour": "DIRECT"},
                {"tag": "local", "address": "local", "detour": "DIRECT"}
            ],
            "rules": [
                {"outbound": "any", "server": "google"}
            ]
        },
        "inbounds": [], # No inbounds needed for client file usually, or mixed
        "outbounds": [selector, urltest] + outbounds + [direct, dns_out],
        "route": {
            "rules": [
                {"protocol": "dns", "outbound": "dns-out"},
                {"clash_mode": "Direct", "outbound": "DIRECT"},
                {"clash_mode": "Global", "outbound": "SELECT"}
            ],
            "auto_detect_interface": True
        }
    }
    
    return json.dumps(final_config, indent=2)
