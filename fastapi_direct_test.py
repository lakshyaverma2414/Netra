import os
import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv('ai-service/.env')
dsn = f"dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')} host={os.getenv('POSTGRES_HOST')} port={os.getenv('POSTGRES_PORT')}"

def run_cypher(query):
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute("LOAD 'age';")
            cur.execute("SET search_path = ag_catalog, \"$user\", public;")
            cur.execute(query)
            conn.commit()
    finally:
        conn.close()

run_cypher("""
SELECT * FROM cypher('crime_network', $$
    MATCH (a {entity_id: 'P001'})
    MERGE (h1:PERSON {entity_id: 'TEMP_HOP1'}) SET h1.resolution_status = 'CONFIRMED'
    MERGE (a)-[rh1:ASSOCIATED_WITH {relationship_id: 'RHOP1', status: 'CONFIRMED'}]->(h1)
$$) AS (v agtype);
""")

r1 = requests.get('http://localhost:8000/api/v1/graph/explore?entity_id=P001&depth=1').json()
print("D1 Nodes:", [n['data']['id'] for n in r1['nodes']])

run_cypher("""
SELECT * FROM cypher('crime_network', $$
    MATCH (n) WHERE n.entity_id = 'TEMP_HOP1'
    DETACH DELETE n
$$) AS (v agtype);
""")
