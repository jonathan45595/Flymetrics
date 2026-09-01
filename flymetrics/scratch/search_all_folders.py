import os

search_paths = [
    r"c:\Users\MIGUEL\OneDrive\Desktop",
    r"c:\Users\MIGUEL\OneDrive\Documentos",
    r"c:\Users\MIGUEL\Downloads",
    r"c:\Users\MIGUEL\.gemini\antigravity"
]

print("Searching for any style.css...")
for base in search_paths:
    if not os.path.exists(base):
        continue
    for root, dirs, files in os.walk(base):
        for file in files:
            if file == "style.css" or file == "old_style.css":
                path = os.path.join(root, file)
                size = os.path.getsize(path)
                if size > 1000:
                    print(f"Found: {path} - Size: {size} bytes")
