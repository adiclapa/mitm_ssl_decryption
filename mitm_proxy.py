import re
import os
import json
import requests
from datetime import datetime
from mitmproxy import http
from dotenv import load_dotenv

load_dotenv()

ELASTICSEARCH_URL = os.environ['ELASTICSEARCH_URL']

def load_patterns(pattern_file):
    """Load regex patterns from a JSON file."""
    try:
        with open(pattern_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data.get("patterns", [])
    except Exception as e:
        print(f"Error loading patterns: {e}")
        return []

def check_patterns(text, patterns):
    """Check if the given text contains any of the provided regex patterns."""
    matches = {}
    for pattern in patterns:
        try:
            name = pattern.get("name", "Unknown Pattern")
            regex = pattern.get("regex")
            compiled_pattern = re.compile(regex)
            found = compiled_pattern.findall(text)
            if found:
                matches[name] = found
        except re.error as e:
            print(f"Invalid regex pattern: {regex} - Error: {e}")
    return matches

class CustomResponse:
    def __init__(self):
        self.pattern_file = '/home/cyberman/mitm_ssl_decryption/patterns.json'
        self.patterns = load_patterns(self.pattern_file)

    def log_to_elasticsearch(self, log_data):
        """Send log data to Elasticsearch."""
        try:
            response = requests.post(ELASTICSEARCH_URL, json=log_data)
            if response.status_code not in [200, 201]:
                print(f"Failed to log to Elasticsearch: {response.text}")
        except Exception as e:
            print(f"Error logging to Elasticsearch: {e}")

    def response(self, flow: http.HTTPFlow) -> None:
        """Intercept HTTP/HTTPS requests and analyze them for DLP violations."""
        try:
            url = flow.request.pretty_url

            if "localhost" not in url:

                headers = str(flow.request.headers)
                body = flow.request.get_text()
                req_content = url + headers + body
                
                matches = check_patterns(req_content, self.patterns)
                if matches:
                    flow.response = http.Response.make(
                        403, b'<h1>DLP triggered. Access denied!</h1>', {"Content-Type": "text/html"}
                    )
                    print("[!] DLP Triggered: Access Denied")
                    print(matches)

                    # Log event to Elasticsearch
                    for match in matches:
                        log_data = {
                            "timestamp": datetime.utcnow().isoformat(),
                            "url": url,
                            "method": flow.request.method,
                            "headers": headers,
                            "body": body,
                            "matched_patterns": match,
                            "found": matches[match]
                        }
                        self.log_to_elasticsearch(log_data)

        except Exception as e:
            print(f"Error processing request: {e}")

        print("=" * 80)


def request(flow: http.HTTPFlow):
    """Intercept HTTP/HTTPS requests and analyze them for DLP violations."""
    pass

def response(flow: http.HTTPFlow):
    """Log intercepted responses."""
    print(f"[+] Response from {flow.request.pretty_url} ({flow.response.status_code})")
    print("=" * 80)

addons = [CustomResponse()]

# Save the script as mitm_logger.py and run it with mitmproxy:
# mitmproxy -s mitm_logger.py --mode transparent --listen-host 0.0.0.0 --listen-port 80 --listen-port 443
