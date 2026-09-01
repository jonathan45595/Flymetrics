import os
paths = [
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\css\style.css",
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\css\old_style.css",
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\index.html"
]
for p in paths:
    print(f"{p}: exists={os.path.exists(p)}")
    if os.path.exists(p):
        print(f"  Size: {os.path.getsize(p)} bytes")
