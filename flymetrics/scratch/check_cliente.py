import re
import sys

with open("frontend/cliente.html", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# 1. Check duplicate IDs
ids = re.findall(r'id=["\']([^"\']+)["\']', content)
id_counts = {}
for i in ids:
    id_counts[i] = id_counts.get(i, 0) + 1

dupes = {k: v for k, v in id_counts.items() if v > 1}
print("=== DUPLICATE IDs IN CLIENTE.HTML ===")
for k, v in dupes.items():
    print(f"  - ID '{k}' appears {v} times")

# 2. Check getElementById references in JS vs DOM HTML
js_get_ids = set(re.findall(r'document\.getElementById\(["\']([^"\']+)["\']\)', content))
dom_ids = set(ids)

missing_ids = js_get_ids - dom_ids
print("\n=== JS getElementById REFERENCING NON-EXISTENT DOM IDs ===")
if missing_ids:
    for m in sorted(missing_ids):
        print(f"  - Missing DOM element ID: '{m}'")
else:
    print("  - None! All referenced DOM IDs exist.")

# 3. Check onclick handlers vs JS window functions
onclick_fns = set(re.findall(r'onclick=["\']([a-zA-Z0-9_]+)\(', content))
js_win_fns = set(re.findall(r'window\.([a-zA-Z0-9_]+)\s*=', content))
js_decl_fns = set(re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', content))
all_defined_fns = js_win_fns | js_decl_fns

missing_fns = onclick_fns - all_defined_fns
print("\n=== ONCLICK HANDLERS REFERENCING UNDEFINED JS FUNCTIONS ===")
if missing_fns:
    for f in sorted(missing_fns):
        print(f"  - Undefined function: '{f}()'")
else:
    print("  - None! All onclick functions are defined.")
