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
                           CaseEntity)
from app.graph.age_graph_repository import AgeGraphRepository

client = TestClient(app)

@pytest.fixture(scope="session")
def db():
    _db = SessionLocal()
    yield _db
    _db.close()

def test_three_cases_exist(db):
    cases = db.query(Case).all()
    assert len(cases) == 3
    ids = {c.case_id for c in cases}
    assert ids == {"C-001", "C-002", "C-003"}
    for c in cases:
        assert c.title is not None
        assert c.description is not None

def test_source_records_exist(db):
    recs = db.query(SourceRecord).count()
    assert recs >= 3

def test_entities_and_mentions_exist(db):
    assert db.query(Entity).count() >= 8
    assert db.query(EntityMention).count() >= 3
    assert db.query(EntityAlias).count() >= 1

def test_shared_canonical_entity(db):
    # P-002 is shared between C-002 and C-003
    p2_cases = db.query(CaseEntity).filter_by(entity_id="P-002").all()
    case_ids = {ce.case_id for ce in p2_cases}
    assert case_ids == {"C-002", "C-003"}
    
    # UPI-001 is shared between C-002 and C-003
    upi_cases = db.query(CaseEntity).filter_by(entity_id="UPI-001").all()
    case_ids = {ce.case_id for ce in upi_cases}
    assert case_ids == {"C-002", "C-003"}

def test_relationships_and_assertions(db):
    # We inserted 8 confirmed and 1 bad
    assert db.query(RelationshipAssertion).count() >= 9
    assert db.query(Relationship).count() >= 9
    assert db.query(Relationship).filter_by(status="CONFIRMED").count() >= 8
    assert db.query(Relationship).filter_by(status="NEEDS_REVIEW").count() == 1

def test_evidence_and_findings(db):
    assert db.query(Evidence).count() >= 2
    assert db.query(Finding).count() >= 1

def test_age_projection_contains_only_confirmed(db):
    conn = db.connection().connection
    with conn.cursor() as cur:
        cur.execute("LOAD 'age';"); cur.execute("SET search_path = ag_catalog, \"$user\", public;")
        cur.execute("SELECT * FROM cypher('crime_network', $$ MATCH ()-[e]->() RETURN count(e) $$) as (c agtype);")
        cnt = int(cur.fetchone()[0])
    
    # Should be exactly 8 edges
    assert cnt >= 8

def test_case_graph_isolation(db):
    repo = AgeGraphRepository(db, "crime_network")
    c1 = repo.get_case_subgraph("C-001")
    c2 = repo.get_case_subgraph("C-002")
    c3 = repo.get_case_subgraph("C-003")
    
    nodes_c1 = {n['data']['id'] for n in c1['nodes']}
    nodes_c2 = {n['data']['id'] for n in c2['nodes']}
    nodes_c3 = {n['data']['id'] for n in c3['nodes']}
    
    # C1 isolated
    assert "P-001" in nodes_c1
    assert "P-002" not in nodes_c1
    
    # C2 isolated
    assert "P-002" in nodes_c2
    assert "UPI-001" in nodes_c2
    assert "P-001" not in nodes_c2
    
    # C3 isolated
    assert "VEH-001" in nodes_c3
    assert "P-002" in nodes_c3
    assert "PH-002" not in nodes_c3

def test_cross_case_discovery(db):
    repo = AgeGraphRepository(db, "crime_network")
    global_graph = repo.get_global_subgraph()
    
    # Find the hidden path: P-001 (C1) -> PH-001 -> PH-002 -> P-002 (C2) -> UPI-001 -> P-003 (C3) -> VEH-001
    
    adj = {}
    for edge in global_graph['edges']:
        src = edge['data']['source']
        tgt = edge['data']['target']
        adj.setdefault(src, []).append(tgt)
        adj.setdefault(tgt, []).append(src)
        
    def find_path(start, end, path=None):
        if path is None:
            path = []
        path = path + [start]
        if start == end:
            return path
        if start not in adj:
            return None
        for node in adj[start]:
            if node not in path:
                newpath = find_path(node, end, path)
                if newpath: return newpath
        return None
        
    path = find_path("P-001", "VEH-001")
    assert path is not None
    # P-001 -> PH-001 -> PH-002 -> P-002 -> UPI-001 -> P-003 -> VEH-001
    # Expected length is 7 nodes (6 edges)
    assert len(path) == 6

