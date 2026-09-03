import pytest
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.schemas.resolution import ResolutionRequest, MentionInput, ResolutionStatusEnum
from app.schemas.extraction import EntityTypeEnum
from app.services.resolution_service import resolve_mentions
from app.db.models import EntityAlias, Entity

@pytest.fixture
def db():
    session = SessionLocal()
    existing_alias = session.query(EntityAlias).filter_by(entity_id="P-002", alias="V. Singh").first()
    if not existing_alias:
        session.add(EntityAlias(entity_id="P-002", alias="V. Singh", normalized_alias="v. singh"))
        session.commit()
    yield session
    session.rollback()
    session.close()

def test_alias_resolution(db):
    req = ResolutionRequest(
        case_id="C-002",
        mentions=[
            MentionInput(text="V. Singh", entity_type=EntityTypeEnum.PERSON, source_record_id="SR-101")
        ]
    )
    res = resolve_mentions(db, req)
    assert res.results[0].status == ResolutionStatusEnum.CONFIRMED
    assert res.results[0].entity_id == "P-002"

def test_exact_identifier_resolution(db):
    req = ResolutionRequest(
        case_id="C-003",
        mentions=[
            MentionInput(text="+91-9999988888", entity_type=EntityTypeEnum.PHONE, source_record_id="SR-102"),
            MentionInput(text="ghost@bank", entity_type=EntityTypeEnum.UPI, source_record_id="SR-102"),
            MentionInput(text="RJ 14 XYZ", entity_type=EntityTypeEnum.VEHICLE, source_record_id="SR-102")
        ]
    )
    res = resolve_mentions(db, req)
    assert res.results[0].entity_id == "PH-002"
    assert res.results[1].entity_id == "UPI-001"
    assert res.results[2].entity_id == "VEH-001"

def test_canonical_name_resolution(db):
    req = ResolutionRequest(
        case_id="C-001",
        mentions=[MentionInput(text="Vikram Singh", entity_type=EntityTypeEnum.PERSON, source_record_id="SR-103")]
    )
    res = resolve_mentions(db, req)
    assert res.results[0].entity_id == "P-002"

def test_ambiguity_remains_candidate(db):
    # Insert multiple matching entities to force ambiguity
    temp_rajan = Entity(entity_id="P-022", entity_type="PERSON", canonical_name="Rajan", normalized_value="rajan")
    db.add(temp_rajan)
    db.commit()
    
    req = ResolutionRequest(
        case_id="C-001",
        mentions=[MentionInput(text="Rajan", entity_type=EntityTypeEnum.PERSON, source_record_id="SR-104")]
    )
    res = resolve_mentions(db, req)
    
    db.delete(temp_rajan)
    db.commit()
    
    assert res.results[0].status == ResolutionStatusEnum.CANDIDATE

def test_negative_match(db):
    req = ResolutionRequest(
        case_id="C-001",
        mentions=[MentionInput(text="Rahul", entity_type=EntityTypeEnum.PERSON, source_record_id="SR-201")]
    )
    res = resolve_mentions(db, req)
    assert res.results[0].status == ResolutionStatusEnum.REJECTED
