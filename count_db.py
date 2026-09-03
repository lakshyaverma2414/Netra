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
            MATCH (n) RETURN count(n)
        $$) AS (c agtype);
    """)
    nodes = cur.fetchone()[0]
    
    cur.execute("""
        SELECT * FROM cypher('crime_network', $$
            MATCH ()-[e]->() RETURN count(e)
        $$) AS (c agtype);
    """)
    edges = cur.fetchone()[0]
    
    print(f"Nodes: {nodes}")
    print(f"Edges: {edges}")
