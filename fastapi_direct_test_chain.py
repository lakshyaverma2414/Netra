import os
import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv('ai-service/.env')
dsn = f"dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')} host={os.getenv('POSTGRES_HOST')} port={os.getenv('POSTGRES_PORT')}"
conn = psycopg2.connect(dsn)
def run_cypher(query):
    with conn.cursor() as cur:
        cur.execute("LOAD 'age';")
        cur.execute("SET search_path = ag_catalog, \"$user\", public;")
        cur.execute(query)
        conn.commit()

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
    MERGE (a)-[:ASSOCIATED_WITH {relationship_id: 'RHOP1', status: 'CONFIRMED'}]->(h1)
    MERGE (h1)-[:ASSOCIATED_WITH {relationship_id: 'RHOP2', status: 'CONFIRMED'}]->(h2)
    MERGE (h2)-[:ASSOCIATED_WITH {relationship_id: 'RHOP3', status: 'CONFIRMED'}]->(h3)
$$) AS (v agtype);
""")

r1 = requests.get('http://localhost:8000/api/v1/graph/explore?entity_id=P001&depth=1').json()
r2 = requests.get('http://localhost:8000/api/v1/graph/explore?entity_id=P001&depth=2').json()
r3 = requests.get('http://localhost:8000/api/v1/graph/explore?entity_id=P001&depth=3').json()
print("D1 Nodes:", [n['data']['id'] for n in r1.get('nodes',[])])
print("D2 Nodes:", [n['data']['id'] for n in r2.get('nodes',[])])
print("D3 Nodes:", [n['data']['id'] for n in r3.get('nodes',[])])
