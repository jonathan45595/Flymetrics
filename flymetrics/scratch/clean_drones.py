import os
import re

files_to_update = {
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\index.html": "html",
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\cliente.html": "html",
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\admin.html": "html",
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\tecnico.html": "html",
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\js\app.js": "js",
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\js\main.js": "js",
    r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\js\admin.js": "js",
}

for path, file_type in files_to_update.items():
    if not os.path.exists(path):
        print(f"File not found: {path}")
        continue
    
    print(f"Cleaning: {os.path.basename(path)}")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    orig_content = content
    
    # 1. Replace logo.jpeg with logo.png
    content = content.replace("img/logo.jpeg", "img/logo.png")
    content = content.replace("logo.jpeg", "logo.png")

    if file_type == "html":
        # Delete #flota section in index.html
        if "index.html" in path:
            # Delete navigation links to Fleet
            content = content.replace('<li><a href="#flota" class="nav-link">Flota</a></li>\n', '')
            content = content.replace('<li><a href="#flota" class="nav-link">Flota</a></li>', '')
            content = content.replace('<li><a href="#flota" class="drawer-link">Flota</a></li>\n', '')
            content = content.replace('<li><a href="#flota" class="drawer-link">Flota</a></li>', '')
            content = content.replace('<li><a href="#flota" style="color: var(--text-muted); text-decoration: none; transition: color 0.3s;" onmouseover="this.style.color=\'#fff\'" onmouseout="this.style.color=\'var(--text-muted)\'">Flota Tecnológica</a></li>\n', '')
            content = content.replace('<li><a href="#flota" style="color: var(--text-muted); text-decoration: none; transition: color 0.3s;" onmouseover="this.style.color=\'#fff\'" onmouseout="this.style.color=\'var(--text-muted)\'">Flota Tecnológica</a></li>', '')
            
            # Use regex to strip out the whole <section id="flota">...</section>
            section_pattern = r'<!-- Section 3.5: Flota de Drones Tecnológicos \(Nueva\) -->\s*<section id="flota".*?</section><!-- Section 4: Ubicaciones'
            content = re.sub(section_pattern, '<!-- Section 4: Ubicaciones', content, flags=re.DOTALL)
            
            # Clean up inline drone mentions in service details
            content = content.replace("drones DJI Agras. Dosificación", "sistemas de aspersión inteligente. Dosificación")
            content = content.replace("drones DJI Agras T40. Dosificación", "sistemas de aspersión de precisión. Dosificación")
            content = content.replace("Dron Empleado", "Tecnología Empleada")
            content = content.replace("dron DJI Agras T40", "aspersor inteligente de precisión")
            content = content.replace("DJI Agras T40", "Sistema de Aspersión de Precisión")
            content = content.replace("Mavic 3 Multispectral RTK", "Sensores Ópticos / Multiespectrales")
            content = content.replace("DJI M350 RTK", "Sensores Lidar y Fotogramétricos")
            content = content.replace("Mavic 3 M", "Sistemas Aéreos de Mapeo")
            content = content.replace("Dron FlyMetrics", "Tecnología FlyMetrics")
            content = content.replace("dron", "sistema")
            content = content.replace("Dron", "Sistema")
            content = content.replace("drones", "sistemas aéreos")
            content = content.replace("Drones", "Sistemas aéreos")
            content = content.replace("Los drones", "Los sistemas aéreos")
            content = content.replace("los drones", "los sistemas aéreos")

    elif file_type == "js":
        # Replace DJI drone model mentions with generic system terminology in JavaScript
        content = content.replace("DJI Agras T40", "Sistema de Aspersión de Precisión")
        content = content.replace("DJI Mavic 3 Enterprise RTK", "Sistema Multiespectral Aéreo")
        content = content.replace("DJI Mavic 3 Multispectral", "Sistema Multiespectral Aéreo")
        content = content.replace("Mavic 3 Multispectral RTK", "Sistemas Aéreos de Monitoreo")
        content = content.replace("DJI Phantom 4 RTK / Mavic 3E", "Sistemas de Fotogrametría Aérea")
        content = content.replace("DJI Matrice 30T / Zenmuse H20T", "Cámaras Termográficas de Alta Sensibilidad")
        content = content.replace("DJI Matrice 350 RTK", "Sistemas Lidar y Fotogramétricos")
        content = content.replace("DJI Agras T10", "Sistema de Fertilización de Precisión")
        content = content.replace("DJI Phantom 4 RTK / DJI Mavic 3 Enterprise", "Sistemas de Fotogrametría Aérea")
        content = content.replace("drones DJI Agras T40", "sistemas de aspersión aérea inteligente")
        content = content.replace("drone: ", "sistema: ")
        content = content.replace("Dron Empleado", "Tecnología Empleada")
        content = content.replace("Equipo Operativo", "Tecnología Empleada")
        content = content.replace("modelo: 'DJI Agras T40'", "modelo: 'Sistema de Aspersión Alfa'")
        content = content.replace("modelo: 'DJI Mavic 3 Enterprise'", "modelo: 'Sistema Multiespectral Beta'")
        content = content.replace("modelo: 'DJI Agras T10'", "modelo: 'Sistema de Fertilización Gama'")

    if content != orig_content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("  Cleaned successfully!")
    else:
        print("  No changes made.")

print("Drone model cleanup complete.")
