import os
import sys
import ast
import re

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

routers_dir = r'app/presentation/api/routers'
files = [f for f in os.listdir(routers_dir) if f.endswith('.py') and not f.startswith('__')]

print("=== CHECKING ROUTERS FOR BUGS AND MISSING IMPORTS/EXCEPTIONS ===")

for fname in sorted(files):
    fpath = os.path.join(routers_dir, fname)
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    
    issues = []
    
    # AST parse
    try:
        tree = ast.parse(code)
    except SyntaxError as se:
        issues.append(f"Syntax error line {se.lineno}: {se.msg}")
        continue

    # Check for raw SQL query concatenation or injection risks
    if 'text(' in code and '%' in code:
        issues.append("Uso de text() con interpolación de strings (% o f-strings) que puede presentar riesgos de SQL injection.")

    # Check for exception swallowing
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                issues.append(f"Bloque except en línea {node.lineno} contiene solo 'pass' (silencia errores sin registro).")
            elif len(node.body) == 1 and isinstance(node.body[0], (ast.Return, ast.Continue)):
                # returns dummy fallback
                pass

    if issues:
        print(f"\n📁 Archivo: {fpath}")
        for iss in issues:
            print(f"  ❌ {iss}")

