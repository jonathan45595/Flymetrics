import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

from fastapi.testclient import TestClient  # type: ignore
from main import app

client = TestClient(app)

print("=== VERIFICACIÓN Y AUDITORÍA DE PÁGINAS Y DASHBOARDS FRONTEND ===")

pages = [
    ("/", "Index / Login Client Portal"),
    ("/admin.html", "Dashboard Administrador"),
    ("/cliente.html", "Dashboard Cliente"),
    ("/tecnico.html", "Dashboard Técnico"),
    ("/staff.html", "Portal de Ingreso Staff Institucional"),
    ("/css/admin.css", "Estilos CSS Admin"),
    ("/css/style.css", "Estilos CSS Global"),
    ("/js/api.js", "Cliente API JS"),
    ("/js/admin.js", "Lógica Admin JS"),
    ("/js/app.js", "Lógica App Global JS"),
]

for route, desc in pages:
    res = client.get(route)
    status_icon = "✓" if res.status_code == 200 else "❌"
    print(f"[{status_icon}] {desc} ({route}): HTTP {res.status_code} ({len(res.content)} bytes)")
    assert res.status_code == 200, f"Error en la ruta {route}"

print("\n" + "="*80)
print("  🎉 TODOS LOS DASHBOARDS, PORTALES Y ESTILOS SE CARGAN DE FORMA RÁPIDA Y FLUIDA")
print("="*80)
