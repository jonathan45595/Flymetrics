import os
import re
import sys

# Ensure UTF-8 output if possible, or replace unsupported characters
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

files = [
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\index.html",
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\cliente.html",
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\admin.html",
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\tecnico.html",
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\staff.html",
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\css\style.css",
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\css\admin.css",
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\css\old_style.css",
]

legacy_patterns = [
    (r"#1e90ff", "Dodger Blue Hex"),
    (r"30,\s*144,\s*255", "Dodger Blue RGB"),
    (r"#00ff88", "Spring Green Hex"),
    (r"0,\s*255,\s*136", "Spring Green RGB"),
    (r"#070707", "Old dark background"),
    (r"#0c0c0c", "Old dark card background"),
]

for file_path in files:
    if os.path.exists(file_path):
        print(f"\n--- Checking: {os.path.basename(file_path)} ---")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.splitlines()
        for pattern, label in legacy_patterns:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            if matches:
                print(f"  [{label}] Found {len(matches)} match(es):")
                for match in matches:
                    start_char = match.start()
                    line_no = content[:start_char].count('\n') + 1
                    line_text = lines[line_no - 1].strip()
                    # Safe print encoding
                    safe_text = line_text[:100].encode('ascii', errors='replace').decode('ascii')
                    print(f"    Line {line_no}: {safe_text}")
    else:
        print(f"File not found: {file_path}")
