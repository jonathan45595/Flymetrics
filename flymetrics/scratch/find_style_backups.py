import os

print("Searching for style.css or backups...")
for root, dirs, files in os.walk(r"c:\Users\MIGUEL\OneDrive\Documentos\flymetrics"):
    for file in files:
        if "style.css" in file or "old_style.css" in file:
            path = os.path.join(root, file)
            print(f"Found: {path} - Size: {os.path.getsize(path)} bytes")
