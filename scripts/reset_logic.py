import os
import uuid
import sys
from sqlalchemy import text
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../ai-service')))
from app.db.database import SessionLocal, engine
from app.db.models import (User, Case, Entity, EntityMention, EntityAlias, EntityResolutionLog,
                           CaseEntity, Relationship, RelationshipAssertion, RelationshipCase,
                           Evidence, EvidenceCase, Finding, SourceRecord, IngestionBatch)
from app.graph.age_graph_repository import AgeGraphRepository

def reset_database():
    print("Resetting database...")
    db = SessionLocal()
    db.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
    db.execute(text("GRANT ALL ON SCHEMA public TO public;"))
    db.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    db.commit()
    
    schema_path = os.path.join(os.path.dirname(__file__), '../migrations/001_initial_schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    conn = engine.raw_connection()
    try:
        cur = conn.cursor()
        cur.execute(schema_sql)
        conn.commit()
    finally:
        conn.close()

    age_repo = AgeGraphRepository(db, "crime_network")
    age_repo.db.execute(text("SELECT drop_graph('crime_network', true) WHERE EXISTS (SELECT FROM ag_graph WHERE name = 'crime_network');"))
    age_repo.db.execute(text("SELECT create_graph('crime_network');"))
    age_repo.db.commit()
    db.close()
    print("Database reset complete.")
