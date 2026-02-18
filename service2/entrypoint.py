import requests
import sys
import os
from datetime import datetime

SERVICE1_URL = os.getenv("SERVICE1_URL", "http://service1:8080")

lines = sys.stdin.read().splitlines()
format_type = lines[0].strip() if lines else "iso"

# call service1 with selected format
response = requests.post(SERVICE1_URL, data=format_type)
timestamp = response.text.strip()

parsed = datetime.fromisoformat(timestamp) if format_type == "iso" else datetime.utcfromtimestamp(int(timestamp))
print(parsed.strftime("%Y-%m-%d"))