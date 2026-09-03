import json
from sqlalchemy import text
from app.db.database import SessionLocal

db = SessionLocal()
tables = [
    "users", "cases", "entities", "entity_mentions", "relationship_assertions",
    "relationships", "relationship_cases", "evidence", "findings", "audit_log"
]

for t in tables:
    cnt = db.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
    print(f"{t}: {cnt}")

conn = db.connection().connection
with conn.cursor() as cur:
    cur.execute("SET search_path = ag_catalog, \"$user\", public;")
    cur.execute("SELECT * FROM cypher('crime_network', $$ MATCH (n) RETURN count(n) $$) as (c agtype);")
    v_cnt = cur.fetchone()[0]
    cur.execute("SELECT * FROM cypher('crime_network', $$ MATCH ()-[e]->() RETURN count(e) $$) as (c agtype);")
    e_cnt = cur.fetchone()[0]
    print(f"AGE vertices: {v_cnt}")
    print(f"AGE edges: {e_cnt}")
