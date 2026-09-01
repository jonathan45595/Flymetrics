import shutil
import os

src_dir = r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\frontend\css"
dest_dir = r"c:\Users\MIGUEL\OneDrive\Documentos\flymetrics\frontend\css"

files = ["style.css", "old_style.css"]

print("Restoring CSS files from Desktop backup...")
for f in files:
    src_file = os.path.join(src_dir, f)
    dest_file = os.path.join(dest_dir, f)
    if os.path.exists(src_file):
        try:
            shutil.copy2(src_file, dest_file)
            print(f"Successfully copied {f} to workspace ({os.path.getsize(dest_file)} bytes).")
        except Exception as e:
            print(f"Error copying {f}: {e}")
    else:
        print(f"Backup file not found: {src_file}")
