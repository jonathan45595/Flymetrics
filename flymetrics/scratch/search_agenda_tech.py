import os

routers_dir = "app/presentation/api/routers"
search_term = "tecnico"

for filename in os.listdir(routers_dir):
    if filename.endswith(".py"):
        filepath = os.path.join(routers_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            if search_term in content or "turno" in content:
                print(f"Found matches in {filename}:")
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    if search_term in line or "turno" in line or "RoleChecker" in line:
                        print(f"  Line {i+1}: {line.strip()}")
