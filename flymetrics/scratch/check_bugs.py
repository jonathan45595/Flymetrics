import os
import sys
import re
import ast
import inspect
from collections import defaultdict

# Force stdout to UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

print("=== INICIANDO ANÁLISIS PROFUNDO ARCHIVO POR ARCHIVO Y CARPETA POR CARPETA ===\n")

issues = defaultdict(list)

# --- CARPETA 1: ROOT (.) ---
print("--- 1. Analizando Carpeta Root (.) ---")
root_py_files = ['main.py', 'run_server.py', 'run_server_inicio_primera_vez.py', 'create_admin_cli.py', 'crear_admin.py', 'create_admin.py']
for rfile in root_py_files:
    if os.path.exists(rfile):
        with open(rfile, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        try:
            ast.parse(content)
        except SyntaxError as e:
            issues[rfile].append(f"Error de sintaxis en línea {e.lineno}: {e.msg}")

if os.path.exists('main.py'):
    with open('main.py', 'r', encoding='utf-8', errors='ignore') as f:
        mcontent = f.read()
    if 'app.mount("/",' in mcontent:
        mount_idx = mcontent.find('app.mount("/",')
        inc_idx = mcontent.find('app.include_router(')
        if mount_idx < inc_idx:
            issues['main.py'].append("El montaje de archivos estáticos 'app.mount(\"/\"...)' está definido ANTES de 'app.include_router(...)', lo que interfiere con la captura de rutas API.")

# --- CARPETA 2: app/infrastructure/database/models/ ---
print("--- 2. Analizando app/infrastructure/database/models/models.py ---")
import app.infrastructure.database.models.models as models

for col in models.UsuarioModel.__table__.columns:
    if 'contrase' in col.name or 'contraseña' in col.name:
        if col.name != 'contraseña':
            issues['app/infrastructure/database/models/models.py'].append(
                f"Nombre de columna con problema de codificación: '{col.name}' en UsuarioModel."
            )

# --- CARPETA 3: app/application/dto/schemas.py ---
print("--- 3. Analizando app/application/dto/schemas.py ---")
import app.application.dto.schemas as schemas
with open('app/application/dto/schemas.py', 'r', encoding='utf-8', errors='ignore') as f:
    s_code = f.read()

# --- CARPETA 4: app/presentation/api/dependencies/auth.py ---
print("--- 4. Analizando app/presentation/api/dependencies/auth.py ---")
with open('app/presentation/api/dependencies/auth.py', 'r', encoding='utf-8', errors='ignore') as f:
    auth_code = f.read()

# --- CARPETA 5: app/presentation/api/routers/ ---
print("--- 5. Analizando Routers en app/presentation/api/routers/ ---")
router_files = [f for f in os.listdir('app/presentation/api/routers') if f.endswith('.py') and not f.startswith('__')]

for rfile in router_files:
    path = os.path.join('app/presentation/api/routers', rfile)
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        issues[path].append(f"Error de sintaxis: {e}")
        continue
    
    if rfile == 'entregables.py':
        if 'frontend/uploads/entregables' in code and 'os.makedirs' not in code:
            issues[path].append("No crea explícitamente la carpeta de destino 'frontend/uploads/entregables' antes de guardar archivos subidos, lo que provoca FileNotFoundError si la carpeta no existe.")

# --- CARPETA 6: frontend/ ---
print("--- 6. Analizando Frontend (HTML y JS) ---")
for root, dirs, files in os.walk('frontend'):
    for f in files:
        fpath = os.path.join(root, f)
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as file_obj:
            content = file_obj.read()
        
        if f.endswith('.html'):
            ids = re.findall(r'\bid=["\']([^"\']+)["\']', content)
            id_counts = defaultdict(int)
            for i in ids:
                id_counts[i] += 1
            dups = [i for i, c in id_counts.items() if c > 1]
            if dups:
                issues[fpath].append(f"IDs HTML duplicados en el mismo documento: {dups}")

print("\n" + "="*80)
print("                       REPORTES DE ERRORES ENCONTRADOS")
print("="*80 + "\n")

if not issues:
    print("No se encontraron errores graves en los chequeos automáticos básicos.")
else:
    for file_name, file_issues in issues.items():
        print(f"[+] ARCHIVO: {file_name}")
        for iss in file_issues:
            print(f"    - {iss}")
        print()
