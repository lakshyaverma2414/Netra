import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

dsn = "dbname=postgres user=netra_app password=netra_app_password host=127.0.0.1 port=5433"
with psycopg2.connect(dsn) as conn:
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    with conn.cursor() as cur:
        with open("migrations/001_initial_schema.sql", "r", encoding="utf-8") as f:
            sql = f.read()
        cur.execute(sql)
        print("Migration 001 executed successfully.")
