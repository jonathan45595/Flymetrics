import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

from fastapi.testclient import TestClient  # type: ignore
from main import app

client = TestClient(app)

print("=== EJECUTANDO PRUEBAS DE INTEGRACIÓN Y FUNCIONALIDAD E2E ===")

# 1. Health Check
res = client.get("/api/v1/health")
print(f"[+] Endpoint /api/v1/health: HTTP {res.status_code} -> {res.json()}")
assert res.status_code == 200

# 2. Docs Availability
res = client.get("/docs")
print(f"[+] Swagger Docs /docs: HTTP {res.status_code}")
assert res.status_code == 200

# 3. Static Index HTML
res = client.get("/")
print(f"[+] Frontend Index /: HTTP {res.status_code}")
assert res.status_code == 200 and "<!DOCTYPE html>" in res.text

# 4. Admin HTML
res = client.get("/admin.html")
print(f"[+] Frontend Admin /admin.html: HTTP {res.status_code}")
assert res.status_code == 200 and "admin" in res.text

# 5. Cliente HTML
res = client.get("/cliente.html")
print(f"[+] Frontend Cliente /cliente.html: HTTP {res.status_code}")
assert res.status_code == 200 and "cliente" in res.text

print("\n🎉 TODAS LAS PRUEBAS DE INTEGRACIÓN PASARON EXITOSAMENTE CON 0 ERRORES.")
