import os

base_dirs = [r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\js", r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen"]
found = False
for b_dir in base_dirs:
    for root, _, files in os.walk(b_dir):
        for file in files:
            if file.endswith((".js", ".html")) and file != "cliente.html":
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    if "service-modal" in content or "showServiceModal" in content:
                        print(f"File: {os.path.relpath(path, b_dir)}")
                        lines = content.splitlines()
                        for idx, line in enumerate(lines):
                            if "service-modal" in line or "showServiceModal" in line or "modal-icon" in line:
                                print(f"  {idx+1}: {line.strip()[:140]}")
                        found = True
                except Exception:
                    pass

