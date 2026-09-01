import sqlite3

conn = sqlite3.connect('flymetrics.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]
print('Tables in DB:', tables)

for t in tables:
    cursor.execute(f"PRAGMA table_info({t});")
    cols = [r[1] for r in cursor.fetchall()]
    print(f"Table '{t}' columns ({len(cols)}):", cols)
