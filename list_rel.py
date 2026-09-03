import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('ai-service/.env')

dsn = f"dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')} host={os.getenv('POSTGRES_HOST')} port={os.getenv('POSTGRES_PORT')}"

conn = psycopg2.connect(dsn)
with conn.cursor() as cur:
    cur.execute("LOAD 'age';")
    cur.execute("SET search_path = ag_catalog, \"$user\", public;")
    
    cur.execute("""
        SELECT * FROM cypher('crime_network', $$
            MATCH p = (n {entity_id: 'P001'})-[*1..3]-(m)
            UNWIND relationships(p) AS e
            RETURN id(e), properties(e), type(e), start_id(e), end_id(e)
        $$) AS (id agtype, props agtype, type agtype, start_id agtype, end_id agtype);
    """)
    for row in cur.fetchall():
        print(row)
