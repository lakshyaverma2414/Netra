import os
import sys
from sqlalchemy import text
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../ai-service')))
from app.db.database import SessionLocal

db = SessionLocal()

tables = {
    "Cases": "cases",
    "Entities": "entities",
    "Entity mentions": "entity_mentions",
    "Aliases": "entity_aliases",
    "Source records": "source_records",
    "Documents": "documents",
    "Relationship assertions": "relationship_assertions",
    "Canonical relationships": "relationships",
    "Relationship-case mappings": "relationship_cases",
    "Evidence": "evidence",
    "Findings": "findings"
}

print("=== DB COUNTS ===")
for label, table in tables.items():
    cnt = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
    print(f"{label}: {cnt}")

conn = db.connection().connection
with conn.cursor() as cur:
    cur.execute("LOAD 'age'; SET search_path = ag_catalog, \"$user\", public;")
    cur.execute("SELECT * FROM cypher('crime_network', $$ MATCH (n) RETURN count(n) $$) as (c agtype);")
    v = cur.fetchone()[0]
    cur.execute("SELECT * FROM cypher('crime_network', $$ MATCH ()-[e]->() RETURN count(e) $$) as (c agtype);")
    e = cur.fetchone()[0]
    print(f"AGE vertices: {v}")
    print(f"AGE edges: {e}")
    
    for case_id in ["C-001", "C-002", "C-003"]:
        sql = f"SELECT count(entity_id) FROM case_entities WHERE case_id = '{case_id}'"
        ncnt = db.execute(text(sql)).scalar()
        sql2 = f"SELECT count(relationship_id) FROM relationship_cases WHERE case_id = '{case_id}'"
        ecnt = db.execute(text(sql2)).scalar()
        print(f"{case_id} graph nodes: {ncnt}")
        print(f"{case_id} graph edges: {ecnt}")
