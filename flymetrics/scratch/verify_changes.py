import os
import re

frontend_dir = r"c:\Users\migue\OneDrive\Desktop\este es el verdadero - copia\flymetrics\frontend"

def check_file(filename, required_strings, forbidden_strings=[]):
    path = os.path.join(frontend_dir, filename)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    missing = [s for s in required_strings if s not in content]
    present_forbidden = [s for s in forbidden_strings if s in content]
    
    if missing:
        print(f"[ERROR] {filename} missing: {missing}")
    else:
        print(f"[OK] {filename} has all required elements.")
        
    if present_forbidden:
        print(f"[ERROR] {filename} has forbidden strings: {present_forbidden}")
    else:
        print(f"[OK] {filename} has no forbidden strings.")

print("--- VERIFYING TECNICO.HTML ---")
check_file("tecnico.html", [
    "Outfit",
    "Plus Jakarta Sans",
    "Mi Ficha Operativa",
    "padding: 32px 36px"
], [
    "Estado de Disponibilidad",
    "Licencia RPAS",
    "Horas de vuelo acumuladas"
])

print("\n--- VERIFYING ADMIN.HTML ---")
check_file("admin.html", [
    "overrideBitacoraModal",
    "overrideInformeEjecutivoModal",
    "overrideInformeTipo",
    "overrideInformeDriveUrl"
])

print("\n--- VERIFYING ADMIN.JS ---")
check_file("js/admin.js", [
    "loadServiciosTiposDropdown",
    "viewReporteBitacora",
    "viewInformeEjecutivo",
    "openEditBitacoraModal",
    "openEditInformeEjecutivoModal"
])

print("\n--- VERIFYING CLIENTE.HTML ---")
check_file("cliente.html", [
    "navItemInformes",
    "navItemBitacora",
    "panelDocsMainText",
    "abrirModalInformeCliente",
    "abrirModalBitacoraCliente"
], [
    "btnTabInformes",
    "btnTabBitacora"
])

print("\nALL VERIFICATIONS COMPLETE!")
