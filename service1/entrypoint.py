import sys
import datetime

lines = sys.stdin.read().splitlines()
format_type = lines[0].strip() if lines else "iso"

now = datetime.datetime.now(datetime.UTC)

if format_type == "timestamp":
    print(str(int(now.timestamp())))
else:
    print(now.isoformat())