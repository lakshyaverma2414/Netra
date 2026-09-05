from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import RelationshipAssertion
from app.services.validation_service import validate_relationship
from app.schemas.validation import ValidationRequest

engine = create_engine("postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres")
Session = sessionmaker(bind=engine)
db = Session()

assertion = db.query(RelationshipAssertion).first()
if assertion:
    val_req = ValidationRequest(
        case_id="C-001",
        source_entity_id=assertion.source_entity_id,
        relationship_type=assertion.relationship_type,
        target_entity_id=assertion.target_entity_id,
        extracted_text=assertion.evidence_text,
        source_record_id=assertion.source_record_id,
        evidence_ids=[str(assertion.observation_id)]
    )
    val_resp = validate_relationship(db, val_req)
    print("Status:", val_resp.status)
    print("Reasons:", val_resp.reasons)
