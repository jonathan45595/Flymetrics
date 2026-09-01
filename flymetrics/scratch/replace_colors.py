import os
import re

files_to_update = [
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\index.html",
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\cliente.html",
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\admin.html",
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\tecnico.html",
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\staff.html",
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\css\style.css",
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\css\admin.css",
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\css\old_style.css",
]

# Colors definition
# Navy Pilot: #003049
# Aero Link: #1C82AD
# Geo Sand: #E4C7A1
# Asphalt: #343A40
# Concrete: #6C757D

def replace_in_file(path):
    if not os.path.exists(path):
        print(f"Skipping (not found): {path}")
        return
    
    print(f"Processing: {os.path.basename(path)}")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    orig_content = content
    
    # 1. Update old_style.css :root variables directly
    if "old_style.css" in path:
        # replace the whole :root block for old_style.css
        root_pattern = r":root\s*\{[^}]*\}"
        new_root = """:root{
  --bg:#f4f6f9;--bg1:#ffffff;--bg2:#edf2f7;--bg3:#e2e8f0;
  --p:#003049;--pg:rgba(0,48,73,.14);--pd:rgba(0,48,73,.07);
  --a:#1C82AD;--ad:rgba(28,130,173,.1);
  --w:#E4C7A1;--e:#FF3B5C;
  --t:#343A40;--t2:#6C757D;--t3:#8E9AA6;
  --b:rgba(108,117,125,.15);--bh:rgba(28,130,173,.38);
  --sb:56px;--sbx:220px;
  --fh:'Syne',sans-serif;--fb:'Space Grotesk',sans-serif;--fm:'JetBrains Mono',monospace;
  --e1:cubic-bezier(.16,1,.3,1);--e2:cubic-bezier(.65,0,.35,1);
}"""
        content = re.sub(root_pattern, new_root, content)

    # 2. General color replacements
    # Dodger Blue Hex (#1E90FF) -> #003049 (Primary Navy) or #1C82AD (Secondary Aero Link)
    # We will use Navy Pilot (#003049) for primary/brand and Aero Link (#1C82AD) for links/icons.
    # To keep visual contrast, let's map hex colors:
    content = content.replace("#1E90FF", "#1C82AD")
    content = content.replace("#1e90ff", "#1c82ad")
    
    # Dodger Blue RGB (30, 144, 255) -> (28, 130, 173) or (0, 48, 73)
    content = re.sub(r"rgba?\(\s*30\s*,\s*144\s*,\s*255\s*,", "rgba(28, 130, 173,", content)
    content = re.sub(r"rgba?\(\s*30\s*,\s*144\s*,\s*255\s*\)", "rgb(28, 130, 173)", content)
    
    # Spring Green Hex (#00FF88) -> #E4C7A1 (Geo Sand) or #1C82AD (Aero Link)
    content = content.replace("#00FF88", "#1C82AD")
    content = content.replace("#00ff88", "#1c82ad")
    
    # Spring Green RGB (0, 255, 136) -> (28, 130, 173)
    content = re.sub(r"rgba?\(\s*0\s*,\s*255\s*,\s*136\s*,", "rgba(28, 130, 173,", content)
    content = re.sub(r"rgba?\(\s*0\s*,\s*255\s*,\s*136\s*\)", "rgb(28, 130, 173)", content)

    # 3. Replace old dark base styles to support Asphalt and light glassmorphism
    if "admin.css" in path:
        # Check background and blobfloat gradients
        content = content.replace("background: #04060e;", "background: var(--bg);")
        content = content.replace("rgba(30,144,255,0.06)", "rgba(0, 48, 73, 0.06)")
        content = content.replace("rgba(0,255,136,0.05)", "rgba(28, 130, 173, 0.05)")
        content = content.replace("rgba(30,144,255,0.03)", "rgba(0, 48, 73, 0.03)")
        content = content.replace("rgba(30,144,255,0.08)", "rgba(28, 130, 173, 0.08)")
        content = content.replace("rgba(0,255,136,0.15)", "rgba(28, 130, 173, 0.15)")
        content = content.replace("rgba(0,255,136,0.3)", "rgba(28, 130, 173, 0.3)")
        
    if "style.css" in path:
        content = content.replace("rgba(30,144,255,0.12)", "rgba(0, 48, 73, 0.12)")
        content = content.replace("rgba(30,144,255,0.75)", "rgba(28, 130, 173, 0.75)")
        content = content.replace("rgba(30, 144, 255, 0.75)", "rgba(28, 130, 173, 0.75)")
        content = content.replace("rgba(30,144,255,0.65)", "rgba(0, 48, 73, 0.65)")
        content = content.replace("rgba(30,144,255,0.45)", "rgba(28, 130, 173, 0.45)")
        content = content.replace("rgba(30, 144, 255, 0.45)", "rgba(28, 130, 173, 0.45)")
        content = content.replace("rgba(30,144,255,0.15)", "rgba(28, 130, 173, 0.15)")
        content = content.replace("rgba(30,144,255,0.35)", "rgba(0, 48, 73, 0.35)")
        content = content.replace("rgba(30, 144, 255, 0.35)", "rgba(0, 48, 73, 0.35)")
        content = content.replace("rgba(30, 144, 255, 0.15)", "rgba(28, 130, 173, 0.15)")
        content = content.replace("rgba(30, 144, 255, 0.05)", "rgba(28, 130, 173, 0.05)")
        content = content.replace("rgba(30,144,255,0.14)", "rgba(0, 48, 73, 0.14)")
        content = content.replace("rgba(30,144,255,0.22)", "rgba(28, 130, 173, 0.22)")
        content = content.replace("rgba(30,144,255,0.08)", "rgba(0, 48, 73, 0.08)")
        content = content.replace("rgba(30, 144, 255, 0.08)", "rgba(0, 48, 73, 0.08)")
        content = content.replace("rgba(30, 144, 255, 0.2)", "rgba(28, 130, 173, 0.2)")
        content = content.replace("rgba(30,144,255,0.2)", "rgba(28, 130, 173, 0.2)")
        content = content.replace("rgba(30, 144, 255, 0.12)", "rgba(0, 48, 73, 0.12)")
        content = content.replace("rgba(30, 144, 255, 0.14)", "rgba(0, 48, 73, 0.14)")

    # 4. Make sure cliente.html has off-white background and light panels so text-main is visible
    if "cliente.html" in path:
        # replace body and cpanel-body background values to avoid dark mode contrast issues
        content = content.replace("background: #040508;", "background: var(--bg1);")
        content = content.replace("background: radial-gradient(circle at 50% 50%, #080a12 0%, #030407 100%);", "background: radial-gradient(circle at 50% 50%, var(--bg1) 0%, var(--bg3) 100%);")
        content = content.replace("background: rgba(10, 15, 30, 0.4);", "background: rgba(255, 255, 255, 0.7);")
        content = content.replace("rgba(30, 144, 255, 0.15)", "rgba(28, 130, 173, 0.15)")
        content = content.replace("rgba(30, 144, 255, 0.4)", "rgba(0, 48, 73, 0.4)")
        content = content.replace("rgba(0, 255, 136, 0.5)", "rgba(28, 130, 173, 0.5)")
        content = content.replace("rgba(0, 255, 136, 0.35)", "rgba(28, 130, 173, 0.35)")
        content = content.replace("rgba(30, 144, 255, 0.05)", "rgba(0, 48, 73, 0.05)")
        content = content.replace("rgba(30, 144, 255, 0.2)", "rgba(0, 48, 73, 0.2)")
        content = content.replace("rgba(0, 255, 136, 0.1)", "rgba(28, 130, 173, 0.1)")
        content = content.replace("rgba(0, 255, 136, 0.05)", "rgba(28, 130, 173, 0.05)")
        content = content.replace("rgba(0, 255, 136, 0.3)", "rgba(28, 130, 173, 0.3)")

    if content != orig_content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("  Updated successfully!")
    else:
        print("  No changes made.")

for p in files_to_update:
    replace_in_file(p)
