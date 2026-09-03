import pytest
import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../ai-service')))
from app.main import app
from app.db.database import SessionLocal
from app.db.models import (Case, Entity, EntityMention, EntityAlias, 
                           Relationship, RelationshipAssertion, Evidence, Finding, SourceRecord,
                           CaseEntity, Document)
from app.graph.age_graph_repository import AgeGraphRepository

client = TestClient(app)

@pytest.fixture(scope="session")
def db():
    _db = SessionLocal()
    yield _db
    _db.close()

def test_ontology_corrected(db):
    owned_by_count = db.query(Relationship).filter_by(relationship_type="OWNED_BY").count()
    owns_upi = db.query(Relationship).filter_by(relationship_type="OWNS", target_entity_id="UPI-001").first()
    
    assert owned_by_count == 0
    assert owns_upi is not None
    assert owns_upi.source_entity_id == "P-003"

def test_documents_exist(db):
    doc_count = db.query(Document).count()
    assert doc_count > 0

def test_enriched_counts(db):
    assert db.query(Evidence).count() >= 10
    assert db.query(Finding).count() >= 5
    assert db.query(SourceRecord).count() >= 10

def test_cross_case_paths(db):
    repo = AgeGraphRepository(db, "crime_network")
    global_graph = repo.get_global_subgraph()
    
    # Financial path: P-002 -> UPI-001 <- P-003 (inverse)
    # Wait, the edges are directed: P-002 -> UPI-001 (TRANSFERRED_TO) and P-003 -> UPI-001 (OWNS)
    # So P-002 -> UPI-001 <- P-003. We'll trace undirected connectivity.
    
    adj = {}
    for edge in global_graph['edges']:
        src = edge['data']['source']
        tgt = edge['data']['target']
        # Undirected
        adj.setdefault(src, []).append(tgt)
        adj.setdefault(tgt, []).append(src)
        
    def find_path(start, end, path=None):
        if path is None: path = []
        path = path + [start]
        if start == end: return path
        if start not in adj: return None
        for node in adj[start]:
            if node not in path:
                newpath = find_path(node, end, path)
                if newpath: return newpath
        return None
    
    # Operational path directly linking entities
    path = find_path("P-001", "VEH-001")
    assert path is not None
    
    # Check length: 6 nodes (which is 5 hops/edges)
    assert len(path) == 6
    
    # Check financial bridge explicitly
    # Is UPI-001 reachable from P-002 and P-003?
    assert "UPI-001" in adj["P-002"]
    assert "UPI-001" in adj["P-003"]

def test_negative_relationship_absent_from_age(db):
    repo = AgeGraphRepository(db, "crime_network")
    global_graph = repo.get_global_subgraph()
    
    edges = global_graph['edges']
    # Ensure no P-001 -> P-003 edge
    for e in edges:
        s = e['data']['source']
        t = e['data']['target']
        assert not (s == "P-001" and t == "P-003")
        assert not (s == "P-003" and t == "P-001")
        
    # Check it exists in Postgres
    bad_rel = db.query(Relationship).filter_by(source_entity_id="P-001", target_entity_id="P-003").first()
    assert bad_rel is not None
    assert bad_rel.status == "NEEDS_REVIEW"

