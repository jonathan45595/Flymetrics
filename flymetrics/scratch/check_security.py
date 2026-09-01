import os
import sys
import ast
import re

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

print("=== CHECKING SECURITY AND FUNCTIONALITY ISSUES ===")

# 1. Check IDOR / Auth checks in routers
routers_dir = r'app/presentation/api/routers'
router_files = [f for f in os.listdir(routers_dir) if f.endswith('.py') and not f.startswith('__')]

for rfile in sorted(router_files):
    path = os.path.join(routers_dir, rfile)
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Check for endpoints missing Depends(get_current_user) or Depends(RoleChecker)
    routes = re.findall(r'@router\.(get|post|put|delete|patch)\(([^)]+)\)\s*\n(?:async\s+)?def\s+([a_zA_Z0-9_]+)\(([^)]*)\)', content)
    for method, route_path, func_name, params in routes:
        if 'current_user' not in params and 'get_current_user' not in params:
            # exclude public routes like login, register, docs, webhook signature
            if not ('login' in func_name or 'register' in func_name or 'public' in func_name or 'webhook' in rfile):
                print(f"  [SECURITY RISK] {rfile} -> {func_name} ({method} {route_path}): Sin autenticación current_user")

    # Check path traversal risks in file downloads/uploads
    if 'FileResponse' in content or 'send_file' in content or 'open(' in content:
        if '..' in content or 'lstrip' not in content:
            print(f"  [PATH TRAVERSAL CHECK] {rfile}: Manejo de archivos físicos encontrado.")

# 2. Check Password Hashing logic
with open('app/infrastructure/security/jwt_handler.py', 'r', encoding='utf-8', errors='ignore') as f:
    jwt_code = f.read()
    if 'HS256' in jwt_code and 'SECRET' in jwt_code:
        print("  [JWT] JWT Handler cargado.")

