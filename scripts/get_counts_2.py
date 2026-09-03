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
    "Evidence": "evidence",
    "Findings": "findings"
}

print("=== DB COUNTS ===")
for label, table in tables.items():
    cnt = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
    print(f"{label}: {cnt}")
