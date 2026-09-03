import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('ai-service/.env')
dsn = f"dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')} host={os.getenv('POSTGRES_HOST')} port={os.getenv('POSTGRES_PORT')}"
conn = psycopg2.connect(dsn)
with conn.cursor() as cur:
    cur.execute("LOAD 'age';")
    cur.execute("SET search_path = ag_catalog, \"$user\", public;")
    query = """
    SELECT * FROM cypher('crime_network', $$
        MATCH p = (n {entity_id: 'P001'})-[*1..1]-(m)
        WHERE ALL(rel IN relationships(p) WHERE rel.status = 'CONFIRMED')
        RETURN p
    $$) AS (p agtype);
    """
    try:
        cur.execute(query)
        print("SUCCESS")
    except Exception as e:
        print("ERROR:", e)
