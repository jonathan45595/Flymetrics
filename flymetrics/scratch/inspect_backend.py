import os

base_dir = r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\app"
for root, _, files in os.walk(base_dir):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                if "verificar-cc" in content or "class Cliente" in content or "/clientes" in content:
                    print(f"File: {os.path.relpath(path, base_dir)}")
                    lines = content.splitlines()
                    for idx, line in enumerate(lines):
                        if any(k in line for k in ["def verificar", "/me", "class Cliente", "verificado"]):
                            print(f"  {idx+1}: {line.strip()[:120]}")
            except Exception:
                pass
