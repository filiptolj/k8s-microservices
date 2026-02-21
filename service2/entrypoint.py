import requests
import sys
import os
from datetime import datetime, timezone

SERVICE1_URL = os.getenv("SERVICE1_URL", "http://service1:8080")

lines = sys.stdin.read().splitlines()
format_type = lines[0].strip() if lines else "iso"

try:
    response = requests.post(SERVICE1_URL, data=format_type, timeout=10)
    response.raise_for_status()
except requests.exceptions.ConnectionError:
    print(f"Error: could not connect to service1 at {SERVICE1_URL}", file=sys.stderr)
    sys.exit(1)
except requests.exceptions.Timeout:
    print(f"Error: request to service1 timed out", file=sys.stderr)
    sys.exit(1)
except requests.exceptions.RequestException as e:
    print(f"Error: service1 request failed: {e}", file=sys.stderr)
    sys.exit(1)

timestamp = response.text.strip()

parsed = datetime.fromisoformat(timestamp) if format_type == "iso" else datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
print(parsed.strftime("%Y-%m-%d"))