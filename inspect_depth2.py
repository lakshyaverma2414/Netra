import os
import requests
import json
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

# Cleanup
run_cypher("""
SELECT * FROM cypher('crime_network', $$
    MATCH (n) WHERE n.entity_id IN ['TEMP_HOP1', 'TEMP_HOP2', 'TEMP_HOP3']
    DETACH DELETE n
$$) AS (v agtype);
""")

run_cypher("""
SELECT * FROM cypher('crime_network', $$
    MATCH (a {entity_id: 'P001'})
    MERGE (h1:PERSON {entity_id: 'TEMP_HOP1'}) SET h1.resolution_status = 'CONFIRMED'
    MERGE (h2:PERSON {entity_id: 'TEMP_HOP2'}) SET h2.resolution_status = 'CONFIRMED'
    MERGE (h3:PERSON {entity_id: 'TEMP_HOP3'}) SET h3.resolution_status = 'CONFIRMED'
    
    MERGE (a)-[rh1:ASSOCIATED_WITH {relationship_id: 'RHOP1'}]->(h1) SET rh1.status = 'CONFIRMED'
    MERGE (h1)-[rh2:ASSOCIATED_WITH {relationship_id: 'RHOP2'}]->(h2) SET rh2.status = 'CONFIRMED'
    MERGE (h2)-[rh3:ASSOCIATED_WITH {relationship_id: 'RHOP3'}]->(h3) SET rh3.status = 'CONFIRMED'
$$) AS (v agtype);
""")

d1 = requests.get('http://localhost:8000/api/v1/graph/explore?entity_id=P001&depth=1').json()
d2 = requests.get('http://localhost:8000/api/v1/graph/explore?entity_id=P001&depth=2').json()
d3 = requests.get('http://localhost:8000/api/v1/graph/explore?entity_id=P001&depth=3').json()

print("Depth 1 Nodes:", [n['data']['id'] for n in d1.get('nodes', [])])
print("Depth 2 Nodes:", [n['data']['id'] for n in d2.get('nodes', [])])
print("Depth 3 Nodes:", [n['data']['id'] for n in d3.get('nodes', [])])

