# MITM SSL decryption

## Usefull links
- [Mitmproxy docs](https://docs.mitmproxy.org/stable/).
- [Github issue](https://github.com/mitmproxy/mitmproxy/issues/458).

## Steps to Use:
1. Install mitm proxy on Ubuntu VM2.
   1. Download and install from [mitmproxy website.](https://mitmproxy.org)
   2. `mitmproxy --mode transparent --showhost --set ssl_insecure=true`
   3. `cat ~/.mitmproxy/mitmproxy-ca.pem`
   4. Install the mitm proxy certificare on the Ubuntu VM1

2. Use redsocks to redirect the traffic to the mitm proxy.
   1. Install redsocks: `sudo apt install redsocks` 
   2. Edit redsocks config `/etc/redsocks.conf`:
   ```conf
   base {
        log_debug = off;
        log_info = on;
        daemon = on;
        redirector = iptables;
    }

    redsocks {
        local_ip = 127.0.0.1;
        local_port = 12345;
        ip = 127.0.0.1;
        port = 8080;
        type = http-relay;
    }
   ```
   3. Start the proxy in `http-relay` mode:
   ```bash
    sudo redsocks
   ```
3. Create iptables rules to redirect the incoming traffic:
   ```bash
    # Mark the incoming web traffic
    iptables -t mangle -A PREROUTING -i ens160 -p tcp --dport 80 -j MARK --set-mark 1
    iptables -t mangle -A PREROUTING -i ens160 -p tcp --dport 443 -j MARK --set-mark 1

    # Use policy routing to forward marked traffic to redsocks
    ip rule add fwmark 1 table 100
    ip route add default via 127.0.0.1 dev lo table 100

    # Routing Decrypted Traffic Back to the Default Gateway
    ip route add default via <gateway IP> dev ens160 table 101
    ip rule add fwmark 2 table 101
   ```

4. Set the VM2 IP address as default gateway to VM1.
5. Test traffic decryption

# Create a python script to inspect the intercepted traffic and block sensitive information
1. `pip install mitmproxy`
2. Mitm Proxy Logger script:
```python
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
# mitmproxy -s mitm_logger.py --mode transparent --listen-host 0.0.0.0
```
3. Run mitmproxy with this script:
```mitmproxy -s mitm_proxy.py --mode transparent --showhost --set ssl_insecure=true```
