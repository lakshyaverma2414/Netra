import pytest
from fastapi.testclient import TestClient
import uuid
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../ai-service')))

from app.main import app
from app.db.database import SessionLocal
from app.db.repositories.case_repository import CaseRepository
from app.db.repositories.entity_repository import EntityRepository
from app.db.repositories.relationship_repository import RelationshipRepository, AssertionRepository
from app.graph.age_graph_repository import AgeGraphRepository
from app.db.models import SourceRecord, IngestionBatch, User

client = TestClient(app)

def test_full_pipeline_persistence():
    db = SessionLocal()
    try:
        case_id = f"TEST-CASE-{uuid.uuid4().hex[:6]}"
        
        case_repo = CaseRepository(db)
        case_repo.create(case_id, case_number=case_id, title="Integration Test Case")
        
        user = User(username=f"testuser_{uuid.uuid4().hex[:6]}", password_hash="hash", role="INVESTIGATOR")
        db.add(user)
        db.flush()
        
        batch = IngestionBatch(case_id=case_id, submitted_by=user.user_id, original_filename="test.json", file_type="JSON", file_hash="hash", status="COMPLETED")
        db.add(batch)
        db.flush()
        
        record_id = f"REC-{uuid.uuid4().hex[:6]}"
        record = SourceRecord(record_id=record_id, batch_id=batch.batch_id, case_id=case_id, source_type="JSON", raw_payload={"data": "test"})
        db.add(record)
        db.flush()
        
        ent_repo = EntityRepository(db)
        mention_1 = ent_repo.add_mention(mention_id=f"M1-{uuid.uuid4().hex[:4]}", entity_type="PERSON", extracted_text="John Doe", normalized_value="JOHN DOE", method="TEST", source_record_id=record_id)
        mention_2 = ent_repo.add_mention(mention_id=f"M2-{uuid.uuid4().hex[:4]}", entity_type="PHONE", extracted_text="1234567890", normalized_value="1234567890", method="TEST", source_record_id=record_id)
        
        e1 = ent_repo.create(entity_id=f"E1-{uuid.uuid4().hex[:4]}", entity_type="PERSON", canonical_name="John Doe", normalized_value="JOHN DOE", resolution_status="CONFIRMED")
        e2 = ent_repo.create(entity_id=f"E2-{uuid.uuid4().hex[:4]}", entity_type="PHONE", canonical_name="1234567890", normalized_value="1234567890", resolution_status="CONFIRMED")
        
        mention_1.resolved_entity_id = e1.entity_id
        mention_2.resolved_entity_id = e2.entity_id
        
        case_repo.add_entity(case_id, e1.entity_id)
        case_repo.add_entity(case_id, e2.entity_id)
        
        rel_repo = RelationshipRepository(db)
        assert_repo = AssertionRepository(db)
        
        assertion = assert_repo.create(source_entity_id=e1.entity_id, target_entity_id=e2.entity_id, relationship_type="USES", status="ACCEPTED", source_record_id=record_id)
        
        rel_id = f"REL-{uuid.uuid4().hex[:6]}"
        rel = rel_repo.create_canonical(relationship_id=rel_id, source_entity_id=e1.entity_id, relationship_type="USES", target_entity_id=e2.entity_id, status="CONFIRMED")
        
        assert_repo.link_assertion(rel.relationship_id, assertion.assertion_id)
        rel_repo.add_case_context(rel.relationship_id, case_id)
        
        db.commit()
        
        age_repo = AgeGraphRepository(db)
        age_repo.sync_confirmed_relationship(
            relationship_id=rel.relationship_id,
            source_id=e1.entity_id,
            target_id=e2.entity_id,
            rel_type=rel.relationship_type,
            source_label=e1.entity_type.value,
            target_label=e2.entity_type.value,
            props={"status": rel.status.value, "relationship_id": rel.relationship_id}
        )
        db.commit()
        
        response = client.get(f"/api/v1/graph/cases/{case_id}")
        data = response.json()
        
        assert len(data["nodes"]) == 2
        assert len(data["edges"]) == 1
        
        print("Integration Test Passed!")
        
    finally:
        db.close()
