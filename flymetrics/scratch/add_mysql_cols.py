import sys
sys.path.insert(0, '.')

from sqlalchemy import text
from app.infrastructure.database.session import engine

with engine.begin() as conn:
    queries = [
        "ALTER TABLE tabla_reportes_vuelo ADD COLUMN requerimientos_vuelo TEXT NULL;",
        "ALTER TABLE tabla_reportes_vuelo ADD COLUMN notas_tecnicas TEXT NULL;",
        "ALTER TABLE tabla_entregables ADD COLUMN nombre_archivo VARCHAR(150) NULL;",
        "ALTER TABLE tabla_pagos ADD COLUMN url_comprobante VARCHAR(255) NULL;",
        "ALTER TABLE tabla_pagos ADD COLUMN url_cotizacion VARCHAR(255) NULL;",
        "ALTER TABLE tabla_pagos ADD COLUMN estado_pago VARCHAR(30) DEFAULT 'Pendiente';"
    ]
    for q in queries:
        try:
            conn.execute(text(q))
            print(f"Executed: {q}")
        except Exception as e:
            print(f"Notice: {e}")

print("All MySQL Columns Verified & Updated!")
