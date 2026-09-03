import os
import psycopg2
from dotenv import load_dotenv
import json

load_dotenv('ai-service/.env')

dsn = f"dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')} host={os.getenv('POSTGRES_HOST')} port={os.getenv('POSTGRES_PORT')}"

conn = psycopg2.connect(dsn)
with conn.cursor() as cur:
    cur.execute("LOAD 'age';")
    cur.execute("SET search_path = ag_catalog, \"$user\", public;")
    
    cur.execute("""
        SELECT * FROM cypher('crime_network', $$
            MATCH (n) RETURN properties(n)
        $$) AS (c agtype);
    """)
    print("NODES:")
    for row in cur.fetchall():
        print(row[0])
        
    cur.execute("""
        SELECT * FROM cypher('crime_network', $$
            MATCH ()-[e]->() RETURN properties(e), type(e)
        $$) AS (c agtype, t agtype);
    """)
    print("\nEDGES:")
    for row in cur.fetchall():
        print(f"[{row[1]}] {row[0]}")
