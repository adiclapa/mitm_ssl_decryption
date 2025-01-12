from mitmproxy import http

def request(flow: http.HTTPFlow):
    """Intercept HTTP/HTTPS requests and log them."""
    print(f"[+] {flow.request.method} {flow.request.pretty_url}")
    print(f"Headers: {flow.request.headers}")
    if flow.request.content:
        print(f"Body: {flow.request.get_text()}")
    print("=" * 80)

def response(flow: http.HTTPFlow):
    """Intercept responses if needed."""
    print(f"[+] Response from {flow.request.pretty_url} ({flow.response.status_code})")
    print("=" * 80)

# Save the script as mitm_logger.py and run it with mitmproxy:
# mitmproxy -s mitm_logger.py --mode transparent --listen-host 0.0.0.0 --listen-port 80 --listen-port 443
