import socket
import time
import ssl
import urllib.parse
import requests
from typing import Tuple, Dict, Any

def parse_proxy_url(url: str) -> Dict[str, str]:
    """
    Parse vless:// or trojan:// url to extract connection details.

    Returns dict with keys: host, port, net, type, security, sni, path
    """
    try:
        # Standardize standard scheme for parsing
        parsed = urllib.parse.urlparse(url)
        
        # Extract basic info
        # Use built-in hostname/port attributes which handle IPv6 brackets [::1] automatically
        host = parsed.hostname
        port = parsed.port if parsed.port else 443
        
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

def test_proxy_reliability(config_link: str, count: int = 3) -> Dict[str, Any]:
    """
    Perform multiple handshakes to test reliability and stability.
    Returns dict: {
        "success": bool,     # True if at least one passed
        "success_rate": int, # Percentage 0-100
        "avg_latency": float,
        "min_latency": float,
        "max_latency": float,
        "jitter": float,
        "msg": str
    }
    """
    latencies = []
    success_count = 0
    last_msg = ""
    
    for i in range(count):
        # Fail Fast: If first attempt fails (likely dead/timeout), stop immediately
        # Use a slightly longer timeout for first attempt, shorter for subsequent
        timeout = 2.0 if i == 0 else 1.5
        
        ok, lat, msg = test_proxy_handshake(config_link, timeout=timeout)
        last_msg = msg
        
        if ok:
            success_count += 1
            latencies.append(lat)
        else:
            # If the first one failed, it's virtually guaranteed to be bad/unstable.
            # Abort to save time.
            if i == 0:
                break
                
        time.sleep(0.1) # Reduced delay
            
    if not latencies:
        return {
            "success": False,
            "success_rate": 0,
            "avg_latency": 0.0,
            "min_latency": 0.0,
            "max_latency": 0.0,
            "jitter": 0.0,
            "msg": last_msg
        }
        
    avg = sum(latencies) / len(latencies)
    
    jitter = 0.0
    if len(latencies) > 1:
        jitter = max(latencies) - min(latencies)
        
    return {
        "success": True,
        "success_rate": int((success_count / (i + 1)) * 100), # Rate relative to attempts made
        "avg_latency": avg,
        "min_latency": min(latencies),
        "max_latency": max(latencies),
        "jitter": jitter,
        "msg": "OK"
    }
