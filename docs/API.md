# Local API guide

Start `python server.py`, then send JSON to `http://127.0.0.1:8000/api`. The API is a development interface on loopback, not an internet-facing service.

Example (Python, Windows/Linux/macOS):

```python
import json
from urllib.request import Request, urlopen
payload = {'action': 'adjust', 'command': 'receipt-001', 'sku': 'SENSOR-01', 'delta': 20, 'expected_version': 0, 'reason': 'Supplier receipt'}
request = Request("http://127.0.0.1:8000/api", data=json.dumps(payload).encode(), headers={"Content-Type":"application/json"})
with urlopen(request) as response:
    print(json.load(response))
```

Success: HTTP 200 with a JSON result. Invalid domain commands: HTTP 400 with `{"error":"..."}`. Unknown routes: 404. Foreign browser origins: 403. Request bodies are limited to 100,000 bytes. SQL uses bound parameters. No arbitrary Python, shell command, or user-supplied handler execution is supported.

## Actions
- `adjust`: `command`, `sku`, nonzero integer `delta`, integer `expected_version`, and `reason`.
- `state`: `sku`; returns quantity and version.
- `events`: optional `sku`; returns ordered event history.

Read the current version, submit an adjustment with a new command ID, and refresh on a version conflict. Retry the exact same command ID and body after an uncertain response; do not generate a new ID for the same business operation.
