import urllib.parse
import datetime

def generate_clash_config(links_text: str) -> str:
    proxies = []
    
    # Header
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    yaml_content = f"""# Date: {now}
port: 7890
socks-port: 7891
allow-lan: true
mode: rule
log-level: info
external-controller: 127.0.0.1:9090
dns:
  enable: true
  listen: 0.0.0.0:53
  enhanced-mode: fake-ip
  nameserver:
    - 8.8.8.8
    - 1.1.1.1
    - https://dns.cloudflare.com/dns-query
  fallback:
    - 1.0.0.1
    - 8.8.4.4
    - https://dns.google/dns-query
proxies:"""

    links = links_text.strip().split('\n')
    names = []

    for link in links:
        link = link.strip()
        if not link:
            continue
            
        try:
            parsed = urllib.parse.urlparse(link)
            query = urllib.parse.parse_qs(parsed.query)
            fragment = urllib.parse.unquote(parsed.fragment)
            
            # Common fields
            server = parsed.hostname
            port = parsed.port
            
            # WebSocket Opts
            path = query.get("path", ["/"])[0]
            host_header = query.get("host", [""])[0]
            if not host_header and "sni" in query:
                host_header = query["sni"][0]
            
            sni = query.get("sni", [""])[0]
            if not sni:
                sni = host_header

            # Construct Proxy Entry
            proxy_entry = ""
            
            if parsed.scheme == "vless":
                uuid = parsed.username
                proxy_entry = f"""
  - name: "{fragment}"
    type: vless
    server: {server}
    port: {port}
    uuid: {uuid}
    udp: true
    tls: true
    skip-cert-verify: true
    servername: {sni}
    network: ws
    ws-opts:
      path: {path}
      headers:
        Host: {host_header}"""

            elif parsed.scheme == "trojan":
                password = parsed.username
                proxy_entry = f"""
  - name: "{fragment}"
    type: trojan
    server: {server}
    port: {port}
    password: {password}
    udp: true
    skip-cert-verify: true
    sni: {sni}
    network: ws
    ws-opts:
      path: {path}
      headers:
        Host: {host_header}"""
            
            # Shadowsocks (Basic support if needed, mostly for future proofing)
            elif parsed.scheme == "ss":
                 # Decode user info (base64)
                 # This part is tricky without standard padding, skipping for now unless explicitly requested/broken
                 pass

            if proxy_entry:
                yaml_content += proxy_entry
                names.append(fragment)
                
        except Exception as e:
            # Skip invalid links silently or log? For CLI we verify output manually.
            continue

    # Proxy Groups
    yaml_content += "\n\nproxy-groups:\n  - name: \"INTERNET\"\n    type: select\n    proxies:"
    for name in names:
        yaml_content += f"\n      - \"{name}\""
    
    yaml_content += "\n      - DIRECT\n      - REJECT"

    # Rules
    yaml_content += """\nrules:
  - IP-CIDR,192.168.0.0/16,DIRECT
  - IP-CIDR,10.0.0.0/8,DIRECT
  - IP-CIDR,172.16.0.0/12,DIRECT
  - IP-CIDR,127.0.0.0/8,DIRECT
  - MATCH,INTERNET
"""

    return yaml_content
