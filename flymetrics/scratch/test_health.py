import requests
BASE = 'http://localhost:3000/api/v1'

try:
    r = requests.get(f'{BASE}/servicios')
    print("STATUS CODE:", r.status_code)
    print("RESPONSE (first 100 chars):", str(r.json())[:100])
except Exception as e:
    print("CONNECTION ERROR:", e)
