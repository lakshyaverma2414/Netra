import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('ai-service/.env')

dsn = f"dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')} host={os.getenv('POSTGRES_HOST')} port={os.getenv('POSTGRES_PORT')}"

conn = psycopg2.connect(dsn)
with conn.cursor() as cur:
    cur.execute("LOAD 'age';")
    cur.execute("SET search_path = ag_catalog, \"$user\", public;")
    
    query = f"""
    SELECT * FROM cypher('crime_network', $$
        MERGE (n:PERSON {{entity_id: 'P009'}})
        SET n.canonical_name = 'Vikram (New)',
            n.resolution_status = 'CONFIRMED',
            n.resolution_score = 0.99,
            n.aliases = '["Vicky"]'
    $$) AS (v agtype);
    """
    cur.execute(query)
    
    query_edge = f"""
    SELECT * FROM cypher('crime_network', $$
        MATCH (a {{entity_id: 'P001'}})
        MATCH (b {{entity_id: 'P009'}})
        MERGE (a)-[r:ASSOCIATED_WITH {{relationship_id: 'REL009'}}]->(b)
        SET r.status = 'CONFIRMED',
            r.source_record_ids = '["NEW_RECORD"]',
            r.evidence_ids = '["NEW_EVIDENCE"]'
    $$) AS (v agtype);
    """
    cur.execute(query_edge)
    conn.commit()
    print("Injected P009 into AGE graph.")
