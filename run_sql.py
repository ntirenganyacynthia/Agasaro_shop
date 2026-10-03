import os
import sys

import psycopg

url = os.environ["DATABASE_URL"].replace("postgresql+psycopg://", "postgresql://")
sql_file = sys.argv[1]

with psycopg.connect(url) as conn:
    print("Connected to:", conn.info.host)
    conn.execute(open(sql_file).read())
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    print("Done. Total products:", count)