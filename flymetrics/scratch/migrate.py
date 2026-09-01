import sys
sys.path.insert(0, '.')
from sqlalchemy import text
from app.infrastructure.database.session import engine

def migrate():
    print("[MIGRATION] Checking/adding columns...")
    with engine.connect() as conn:
        # Check if departamento column exists in tabla_fincas
        result = conn.execute(text("SHOW COLUMNS FROM tabla_fincas LIKE 'departamento'"))
        row = result.fetchone()
        if not row:
            print("  [+] Adding column 'departamento' to 'tabla_fincas'...")
            conn.execute(text("ALTER TABLE tabla_fincas ADD COLUMN departamento VARCHAR(50) NULL"))
            conn.commit()
            print("  [+] Column 'departamento' added successfully!")
        else:
            print("  [i] Column 'departamento' already exists in 'tabla_fincas'")

if __name__ == "__main__":
    migrate()
