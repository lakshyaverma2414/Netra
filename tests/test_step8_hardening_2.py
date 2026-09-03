import pytest
import uuid
import json
from sqlalchemy import text
from app.db.database import SessionLocal
from app.db.models import (Case, Entity, CaseEntity, Relationship, RelationshipCase, 
                           Evidence, EvidenceCase, EvidenceEntity, EvidenceRelationship,
                           EvidenceFinding, EvidenceCustodyLog, AuditLog, Finding)
from app.graph.age_graph_repository import AgeGraphRepository

@pytest.fixture(scope="session")
def db():
    _db = SessionLocal()
    yield _db
    _db.close()

def test_case_isolation_case001_and_case002(db):
    c1 = f"C1-{uuid.uuid4().hex[:6]}"
    c2 = f"C2-{uuid.uuid4().hex[:6]}"
    p1 = f"P1-{uuid.uuid4().hex[:6]}"
    ph1 = f"PH1-{uuid.uuid4().hex[:6]}"
    ph2 = f"PH2-{uuid.uuid4().hex[:6]}"
    
    db.add_all([
        Case(case_id=c1, case_number=c1, title="C1"),
        Case(case_id=c2, case_number=c2, title="C2"),
        Entity(entity_id=p1, entity_type="PERSON", canonical_name="P1", normalized_value="P1"),
        Entity(entity_id=ph1, entity_type="PHONE", canonical_name="PH1", normalized_value="PH1"),
        Entity(entity_id=ph2, entity_type="PHONE", canonical_name="PH2", normalized_value="PH2")
    ])
    db.flush()
    
    # Shared entity P1
    db.add_all([
        CaseEntity(case_id=c1, entity_id=p1),
        CaseEntity(case_id=c2, entity_id=p1),
        CaseEntity(case_id=c1, entity_id=ph1),
        CaseEntity(case_id=c2, entity_id=ph2)
    ])
    db.flush()
    
    # Rel 1: P1 uses PH1 (C1)
    r1 = Relationship(relationship_id=f"R1-{uuid.uuid4().hex[:6]}", source_entity_id=p1, target_entity_id=ph1, relationship_type="USES")
    # Rel 2: P1 uses PH2 (C2)
    r2 = Relationship(relationship_id=f"R2-{uuid.uuid4().hex[:6]}", source_entity_id=p1, target_entity_id=ph2, relationship_type="USES")
    db.add_all([r1, r2])
    db.flush()
    
    db.add_all([
        RelationshipCase(relationship_id=r1.relationship_id, case_id=c1),
        RelationshipCase(relationship_id=r2.relationship_id, case_id=c2)
    ])
    db.commit()
    
    # Write to AGE
    age_repo = AgeGraphRepository(db, "test_network_iso")
    age_repo.db.execute(text("SELECT drop_graph('test_network_iso', true) WHERE EXISTS (SELECT FROM ag_graph WHERE name = 'test_network_iso');"))
    age_repo.db.execute(text("SELECT create_graph('test_network_iso');"))
    age_repo.db.commit()
    
    age_repo.sync_confirmed_relationship(r1.relationship_id, p1, ph1, "USES", "PERSON", "PHONE", {"status": "CONFIRMED"})
    age_repo.sync_confirmed_relationship(r2.relationship_id, p1, ph2, "USES", "PERSON", "PHONE", {"status": "CONFIRMED"})
    db.commit()
    
    # Query C1 Graph
    res1 = age_repo.get_case_subgraph(c1)
    nodes1 = [n['data']['id'] for n in res1['nodes']]
    assert p1 in nodes1
    assert ph1 in nodes1
    assert ph2 not in nodes1 # CASE 2 node explicitly not exposed
    
    # Query C2 Graph
    res2 = age_repo.get_case_subgraph(c2)
    nodes2 = [n['data']['id'] for n in res2['nodes']]
    assert p1 in nodes2
    assert ph2 in nodes2
    assert ph1 not in nodes2
    
    # Cross-Case Traversal (Global)
    res_global = age_repo.get_global_subgraph()
    nodes_global = [n['data']['id'] for n in res_global['nodes']]
    assert p1 in nodes_global
    assert ph1 in nodes_global
    assert ph2 in nodes_global
    assert len([n for n in res_global['nodes'] if n['data']['id'] == p1]) == 1 # NO duplicate global nodes!
    
    age_repo.db.execute(text("SELECT drop_graph('test_network_iso', true);"))
    age_repo.db.commit()

def test_graph_injection_query_safety(db):
    # Verify that adversarial ID strings don't break Cypher execution (sanitize works)
    age_repo = AgeGraphRepository(db, "test_network_inj")
    age_repo.db.execute(text("SELECT drop_graph('test_network_inj', true) WHERE EXISTS (SELECT FROM ag_graph WHERE name = 'test_network_inj');"))
    age_repo.db.execute(text("SELECT create_graph('test_network_inj');"))
    age_repo.db.commit()
    
    # Adversarial input
    adv_id = "P001' OR '1'='1"
    # Sync should sanitize away the quotes and spaces
    age_repo.sync_confirmed_relationship(
        relationship_id=f"R-{uuid.uuid4().hex[:6]}",
        source_id=adv_id,
        target_id="T001",
        rel_type="KNOWS",
        source_label="PERSON",
        target_label="PERSON",
        props={"status": "CONFIRMED"}
    )
    db.commit()
    
    res = age_repo.get_global_subgraph()
    nodes = [n['data']['id'] for n in res['nodes']]
    # Sanitized result for `P001' OR '1'='1` is `P001OR11`
    assert "P001OR11" in nodes
    
    age_repo.db.execute(text("SELECT drop_graph('test_network_inj', true);"))
    age_repo.db.commit()

def test_evidence_mapping(db):
    cid = f"C-{uuid.uuid4().hex[:6]}"
    c = Case(case_id=cid, case_number=cid, title="C")
    db.add(c)
    
    ev_id = f"EV-{uuid.uuid4().hex[:6]}"
    ev = Evidence(evidence_id=ev_id, case_id=cid, evidence_type="DOC", storage_uri="/dev/null", file_hash=ev_id)
    db.add(ev)
    db.flush()
    
    # Map to case
    ec = EvidenceCase(evidence_id=ev_id, case_id=cid)
    db.add(ec)
    
    # Map to Custody
    cl = EvidenceCustodyLog(evidence_id=ev_id, action="INGEST", timestamp=text("NOW()"))
    db.add(cl)
    db.commit()
    
    assert db.query(EvidenceCase).filter_by(evidence_id=ev_id).first() is not None
    assert db.query(EvidenceCustodyLog).filter_by(evidence_id=ev_id).count() == 1

def test_audit_logging(db):
    log = AuditLog(user_id=None, action="CREATE_TEST", resource_type="CASE", resource_id="XYZ")
    db.add(log)
    db.commit()
    assert db.query(AuditLog).filter_by(action="CREATE_TEST").first() is not None

def test_graph_depth(db):
    age_repo = AgeGraphRepository(db, "test_network_depth")
    age_repo.db.execute(text("SELECT drop_graph('test_network_depth', true) WHERE EXISTS (SELECT FROM ag_graph WHERE name = 'test_network_depth');"))
    age_repo.db.execute(text("SELECT create_graph('test_network_depth');"))
    age_repo.db.commit()
    
    # Create chain A -> B -> C -> D
    age_repo.sync_confirmed_relationship("R1", "A", "B", "K", "P", "P", {})
    age_repo.sync_confirmed_relationship("R2", "B", "C", "K", "P", "P", {})
    age_repo.sync_confirmed_relationship("R3", "C", "D", "K", "P", "P", {})
    db.commit()
    
    res1 = age_repo.get_global_subgraph(entity_id="A", depth=1)
    # A and B (hops=1) => length 2
    assert len(res1['nodes']) == 2
    
    res2 = age_repo.get_global_subgraph(entity_id="A", depth=2)
    # A, B, C (hops=2) => length 3
    assert len(res2['nodes']) == 3
    
    res3 = age_repo.get_global_subgraph(entity_id="A", depth=3)
    # A, B, C, D => length 4
    assert len(res3['nodes']) == 4
    
    age_repo.db.execute(text("SELECT drop_graph('test_network_depth', true);"))
    age_repo.db.commit()
