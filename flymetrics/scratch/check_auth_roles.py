import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

print("=== CHECKING AUTHORIZATION AND IDOR VULNERABILITIES IN ALL ROUTERS ===")

routers_dir = r'app/presentation/api/routers'
router_files = [f for f in os.listdir(routers_dir) if f.endswith('.py') and not f.startswith('__')]

for rfile in sorted(router_files):
    path = os.path.join(routers_dir, rfile)
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    current_endpoint = None
    for idx, line in enumerate(lines, 1):
        if line.strip().startswith('@router.'):
            current_endpoint = line.strip()
        elif current_endpoint and 'def ' in line:
            func_sig = line.strip()
            # check next lines for params
            full_def = line
            j = idx
            while ')' not in full_def and j < len(lines):
                j += 1
                full_def += lines[j-1]
            
            if 'Depends(get_current_user)' in full_def:
                print(f"📄 {rfile}:{idx} -> {current_endpoint}")
                print(f"   ⚠️ Usa 'get_current_user' (Cualquier rol autenticado). Verificar si falta restricción de rol o filtrado de propietario.")
            current_endpoint = None

