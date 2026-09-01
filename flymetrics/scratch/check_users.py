import os
import pymysql
from dotenv import load_dotenv

load_dotenv()
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "miguepro")
DB_NAME = os.getenv("DB_NAME", "flymetrics_db")

try:
    conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tabla_usuarios")
    # let's describe table first to see columns
    cursor.execute("DESCRIBE tabla_usuarios")
    cols = cursor.fetchall()
    print("Columns in tabla_usuarios:")
    for c in cols:
        print(f" - {c[0]}: {c[1]}")
        
    cursor.execute("SELECT * FROM tabla_usuarios")
    rows = cursor.fetchall()
    print("\nUsers in database:")
    for r in rows:
        print(r)
    cursor.close()
    conn.close()
except Exception as e:
    print("DB connection error:", e)
