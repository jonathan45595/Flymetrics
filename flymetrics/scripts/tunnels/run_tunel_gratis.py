import subprocess
import sys
import os
from pathlib import Path

base_dir = Path(__file__).resolve().parent
cloudflared_path = base_dir / "cloudflared.exe"

print("=" * 65)
print("     FLYMETRICS - TUNEL CLOUDFLARE PUBLICO (100% GRATUITO)")
print("=" * 65)
print("\n[+] Iniciando túnel seguro HTTPS con Cloudflare...")
print("[+] Conectando a http://localhost:3000 sin contraseñas...\n")

if not cloudflared_path.exists():
    print(f"Error: No se encontró {cloudflared_path}")
    sys.exit(1)

try:
    subprocess.run([str(cloudflared_path), "tunnel", "--url", "http://localhost:3000"])
except KeyboardInterrupt:
    print("\n[!] Túnel detenido por el usuario.")
