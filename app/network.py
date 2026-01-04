import socket
import time
import ssl
import urllib.parse
import requests
from typing import Tuple, Dict

def parse_proxy_url(url: str) -> Dict[str, str]:
    """
    Parse vless:// or trojan:// url to extract connection details.
    Returns dict with keys: host, port, net, type, security, sni, path
    """
    try:
        # Standardize standard scheme for parsing
        parsed = urllib.parse.urlparse(url)
        
        # Extract basic info
        netloc_parts = parsed.netloc.split("@")[-1].split(":")
        host = netloc_parts[0]
        port = int(netloc_parts[1]) if len(netloc_parts) > 1 else 443
        
        # Parse query params
        query = urllib.parse.parse_qs(parsed.query)
        
        config = {
            "host": host,
            "port": port,
            "type": query.get('type', ['tcp'])[0],
            "security": query.get('security', ['none'])[0],
            "sni": query.get('sni', [''])[0],
            "path": urllib.parse.unquote(query.get('path', ['/'])[0]),
            "encryption": query.get('encryption', ['none'])[0]
        }
        
        # Fallback for SNI if not explicitly set but present in host
        if not config['sni']:
            config['sni'] = config['host']
            
        return config
    except Exception:
        return {}

def test_proxy_handshake(config_link: str, timeout: int = 5) -> Tuple[bool, float, str]:
    """
    Perform a real handshake test based on the config link.
    Returns: (success, latency_ms, status_message)
    """
    config = parse_proxy_url(config_link)
    if not config:
        return False, 0.0, "Invalid Link"

    host = config['host']
    port = config['port']
    sni = config['sni']
    path = config['path']
    security = config['security']
    net_type = config['type']

    start_time = time.time()
    
    try:
        # 1. TCP Connection
        sock = socket.create_connection((host, port), timeout=timeout)
        
        # 2. TLS Handshake (if security is tls/ssl)
        if security == 'tls' or security == 'ssl':
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            try:
                sock = context.wrap_socket(sock, server_hostname=sni if sni else host)
            except Exception as e:
                sock.close()
                return False, 0.0, f"TLS Error: {e}"

        # 3. WebSocket Handshake (if type is ws)
        if net_type == 'ws':
            request = (
                f"GET {path} HTTP/1.1\r\n"
                f"Host: {sni if sni else host}\r\n"
                f"Upgrade: websocket\r\n"
                f"Connection: Upgrade\r\n"
                f"Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
                f"Sec-WebSocket-Version: 13\r\n"
                f"\r\n"
            )
            sock.sendall(request.encode())
            
            response = sock.recv(4096).decode()
            if "101 Switching Protocols" not in response:
                sock.close()
                return False, 0.0, "WS Handshake Failed"

        latency = (time.time() - start_time) * 1000
        sock.close()
        return True, latency, "Handshake OK"

    except socket.timeout:
        return False, 0.0, "Timeout"
    except ConnectionRefusedError:
        return False, 0.0, "Refused"
    except Exception as e:
        return False, 0.0, f"Error: {str(e)}"

def tcp_ping(host: str, port: int = 443, timeout: int = 3) -> Tuple[bool, float]:
    """Legacy TCP ping support"""
    try:
        start_time = time.time()
        with socket.create_connection((host, port), timeout=timeout):
            latency = (time.time() - start_time) * 1000
            return True, latency
    except Exception:
        return False, 0.0

def check_domain_status(domain: str, timeout: int = 5) -> str:
    """
    Check if a domain is reachable via HTTP/HTTPS and returns status 200.
    Returns: "ACTIVE", "DEAD"
    """
    if not domain:
        return "DEAD"

    # Try HTTPS first, then HTTP
    protocols = ["https", "http"]
    
    for proto in protocols:
        try:
            url = f"{proto}://{domain}"
            # User requested strict check: "jika status 200 berarti domain masih hidup"
            response = requests.get(url, timeout=timeout, allow_redirects=True)
            
            if response.status_code == 200:
                return "ACTIVE"
        except requests.exceptions.RequestException:
            # DNS failure, Connection refusal, Timeout all fall here -> Continue to next proto or return DEAD
            continue
            
    return "DEAD"
