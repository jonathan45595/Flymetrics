import sys
sys.path.insert(0, '.')
from sqlalchemy import text
from app.infrastructure.database.session import engine

def migrate():
    print("[MIGRATION] Creating PQR tables in MySQL...")
    with engine.connect() as conn:
        # Create tabla_pqrs if not exists
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS tabla_pqrs (
                id_pqr INT AUTO_INCREMENT PRIMARY KEY,
                id_usuario INT NOT NULL,
                tipo VARCHAR(50) NOT NULL,
                asunto VARCHAR(150) NOT NULL,
                mensaje TEXT NOT NULL,
                estado VARCHAR(30) DEFAULT 'Abierto',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP NULL DEFAULT NULL,
                created_by INT NULL,
                updated_by INT NULL,
                FOREIGN KEY (id_usuario) REFERENCES tabla_usuarios (id_usuarios) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """))
        # Create tabla_mensajes_pqrs if not exists
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS tabla_mensajes_pqrs (
                id_mensaje_pqr INT AUTO_INCREMENT PRIMARY KEY,
                id_pqr INT NOT NULL,
                id_usuario INT NOT NULL,
                mensaje TEXT NOT NULL,
                fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP NULL DEFAULT NULL,
                created_by INT NULL,
                updated_by INT NULL,
                FOREIGN KEY (id_pqr) REFERENCES tabla_pqrs (id_pqr) ON DELETE CASCADE,
                FOREIGN KEY (id_usuario) REFERENCES tabla_usuarios (id_usuarios) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """))
        conn.commit()
        print("[MIGRATION] PQR tables created successfully!")

if __name__ == "__main__":
    migrate()
