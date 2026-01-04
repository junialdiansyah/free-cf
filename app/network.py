import socket
import time

def tcp_ping(host: str, port: int = 443, timeout: int = 3) -> tuple[bool, float]:
    """
    Perform a simple TCP handshake to check reachability.
    Returns (success, latency_ms).
    """
    try:
        # Resolve hostname first (handles SNI domains generally resolving to same IP)
        # Note: API usually returns hostname.
        start_time = time.time()
        with socket.create_connection((host, port), timeout=timeout):
            latency = (time.time() - start_time) * 1000
            return True, latency
    except Exception:
        return False, 0.0
