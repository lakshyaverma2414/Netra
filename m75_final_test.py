import os
import subprocess
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
            if cur.description:
                return cur.fetchall()
            return []
    finally:
        conn.close()

# Cleanup
run_cypher("""
SELECT * FROM cypher('crime_network', $$
    MATCH (n) WHERE n.entity_id IN ['P009', 'P010', 'P011', 'TEMP_HOP1', 'TEMP_HOP2', 'TEMP_HOP3']
    DETACH DELETE n
$$) AS (v agtype);
""")

# Create properly structured test data with all props inline
run_cypher("""
SELECT * FROM cypher('crime_network', $$
    MATCH (a {entity_id: 'P001'})
    MERGE (h1:PERSON {entity_id: 'TEMP_HOP1', resolution_status: 'CONFIRMED'})
    MERGE (h2:PERSON {entity_id: 'TEMP_HOP2', resolution_status: 'CONFIRMED'})
    MERGE (h3:PERSON {entity_id: 'TEMP_HOP3', resolution_status: 'CONFIRMED'})
    
    MERGE (a)-[:ASSOCIATED_WITH {relationship_id: 'RHOP1', status: 'CONFIRMED'}]->(h1)
    MERGE (h1)-[:ASSOCIATED_WITH {relationship_id: 'RHOP2', status: 'CONFIRMED'}]->(h2)
    MERGE (h2)-[:ASSOCIATED_WITH {relationship_id: 'RHOP3', status: 'CONFIRMED'}]->(h3)
    
    MERGE (n:PERSON {entity_id: 'P009', resolution_status: 'CONFIRMED'})
    MERGE (m:PERSON {entity_id: 'P010', resolution_status: 'NEEDS_REVIEW'})
    MERGE (o:PERSON {entity_id: 'P011', resolution_status: 'REJECTED'})
    
    MERGE (a)-[:ASSOCIATED_WITH {relationship_id: 'REL009', status: 'CONFIRMED'}]->(n)
    MERGE (a)-[:ASSOCIATED_WITH {relationship_id: 'REL010', status: 'NEEDS_REVIEW'}]->(m)
    MERGE (a)-[:ASSOCIATED_WITH {relationship_id: 'REL011', status: 'REJECTED'}]->(o)
$$) AS (v agtype);
""")

# Duplicate
run_cypher("""
SELECT * FROM cypher('crime_network', $$
    MATCH (a {entity_id: 'P001'})
    MATCH (n {entity_id: 'P009'})
    MERGE (a)-[:ASSOCIATED_WITH {relationship_id: 'REL009', status: 'CONFIRMED'}]->(n)
$$) AS (v agtype);
""")

count_p009 = run_cypher("""
SELECT * FROM cypher('crime_network', $$
    MATCH (n {entity_id: 'P009'}) RETURN count(n)
$$) AS (c agtype);
""")[0][0]

count_rel009 = run_cypher("""
SELECT * FROM cypher('crime_network', $$
    MATCH (n {entity_id: 'P001'})-[r {relationship_id: 'REL009'}]->(m {entity_id: 'P009'}) RETURN count(r)
$$) AS (c agtype);
""")[0][0]

print("1. Direct AGE query contains P009.")
print(f"P009 count in AGE: {count_p009}")
print("7. Duplicate confirmed relationship produces exactly one relationship in AGE itself")
print(f"REL009 count in AGE: {count_rel009}")

out1 = subprocess.check_output(['node', 'check_ui.mjs', '1']).decode('utf-8')
api_resp1 = json.loads([l for l in out1.split('\n') if l.startswith('API_RESPONSE:')][0].replace('API_RESPONSE:', '').strip())

out2 = subprocess.check_output(['node', 'check_ui.mjs', '2']).decode('utf-8')
api_resp2 = json.loads([l for l in out2.split('\n') if l.startswith('API_RESPONSE:')][0].replace('API_RESPONSE:', '').strip())
cy_elems = json.loads([l for l in out2.split('\n') if l.startswith('CYTOSCAPE_ELEMENTS:')][0].replace('CYTOSCAPE_ELEMENTS:', '').strip())

out3 = subprocess.check_output(['node', 'check_ui.mjs', '3']).decode('utf-8')
api_resp3 = json.loads([l for l in out3.split('\n') if l.startswith('API_RESPONSE:')][0].replace('API_RESPONSE:', '').strip())

api_nodes2 = [n['data']['id'] for n in api_resp2['nodes']]
api_edges2 = [e['data']['id'] for e in api_resp2['edges']]

print("\n2. FastAPI JSON contains P009.")
print(f"P009 in API (Depth 2): {'Yes' if 'P009' in api_nodes2 else 'No'}")

cy_nodes = [e['id'] for e in cy_elems if 'source' not in e]
cy_edges = [e['id'] for e in cy_elems if 'source' in e]

print("\n3. Cytoscape instance contains P009.")
print(f"P009 in Cytoscape (Depth 2): {'Yes' if 'P009' in cy_nodes else 'No'}")

print("\n4. Cytoscape contains REL009.")
print(f"REL009 in Cytoscape (Depth 2): {'Yes' if 'REL009' in cy_edges else 'No'}")

print("\n5. NEEDS_REVIEW edge is absent.")
print(f"REL010 in API: {'Yes' if 'REL010' in api_edges2 else 'No'}")

print("\n6. REJECTED edge is absent.")
print(f"REL011 in API: {'Yes' if 'REL011' in api_edges2 else 'No'}")

print("\nHop Depth Scaling Verification:")
nodes1 = len(api_resp1['nodes'])
nodes2 = len(api_resp2['nodes'])
nodes3 = len(api_resp3['nodes'])
print(f"Depth 1 nodes = {nodes1}")
print(f"Depth 2 nodes = {nodes2}")
print(f"Depth 3 nodes = {nodes3}")
print(f"depth=1 < depth=2 < depth=3: {nodes1 < nodes2 < nodes3}")

run_cypher("""
SELECT * FROM cypher('crime_network', $$
    MATCH (n) WHERE n.entity_id IN ['P009', 'P010', 'P011', 'TEMP_HOP1', 'TEMP_HOP2', 'TEMP_HOP3']
    DETACH DELETE n
$$) AS (v agtype);
""")

out_after = subprocess.check_output(['node', 'check_ui.mjs', '1']).decode('utf-8')
api_resp_after = json.loads([l for l in out_after.split('\n') if l.startswith('API_RESPONSE:')][0].replace('API_RESPONSE:', '').strip())

print("\n8. After deleting P009 directly from AGE, a fresh API request does not contain P009.")
print(f"P009 in API after deletion: {'Yes' if 'P009' in [n['data']['id'] for n in api_resp_after['nodes']] else 'No'}")

