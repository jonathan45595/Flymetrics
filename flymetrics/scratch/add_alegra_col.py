import sys, os
sys.path.insert(0, os.path.abspath('.'))

from sqlalchemy import text
from app.infrastructure.database.session import SessionLocal

db = SessionLocal()
try:
    res = db.execute(text("SHOW COLUMNS FROM tabla_clientes LIKE 'link_alegra'")).fetchall()
    if not res:
        db.execute(text("ALTER TABLE tabla_clientes ADD COLUMN link_alegra VARCHAR(500) NULL"))
        db.commit()
        print('Added link_alegra column to tabla_clientes!')
    else:
        print('Column link_alegra already exists.')
finally:
    db.close()
