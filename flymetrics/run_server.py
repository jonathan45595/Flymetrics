import os
import sys
import subprocess
from pathlib import Path

def main():
    base_dir = Path(__file__).resolve().parent
    venv_dir = base_dir / ".venv"
    
    if os.name == 'nt':
        python_exe = venv_dir / "Scripts" / "python.exe"
    else:
        python_exe = venv_dir / "bin" / "python"
        
    if not python_exe.exists():
        print("Error: El entorno virtual no existe. Por favor ejecuta 'python run_server_inicio_primera_vez.py' primero.")
        sys.exit(1)
        
    print("Iniciando Flymetrics OS (API)...")
    try:
        subprocess.run([str(python_exe), "main.py"])
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")

if __name__ == "__main__":
    main()
