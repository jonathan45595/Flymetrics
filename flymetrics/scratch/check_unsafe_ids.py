import re

with open("frontend/cliente.html", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Find document.getElementById(...) property accesses like .textContent =, .value =, .style, .innerHTML =
accesses = re.findall(r'document\.getElementById\(["\']([^"\']+)["\']\)\.([a-zA-Z0-9_]+)', content)

# Check which ones might fail if the ID is missing
ids_in_html = set(re.findall(r'id=["\']([^"\']+)["\']', content))

unsafe = []
for id_name, prop in accesses:
    if id_name not in ids_in_html:
        unsafe.append((id_name, prop))

print("=== UNSAFE getElementById PROPERTY ACCESSES IN CLIENTE.HTML ===")
if unsafe:
    for id_name, prop in unsafe:
        print(f"  - document.getElementById('{id_name}').{prop} (DOM element missing!)")
else:
    print("  - None! All property accesses target existing DOM IDs or are guarded.")
