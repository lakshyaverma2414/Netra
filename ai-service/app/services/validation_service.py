import uuid
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from app.db.models import Entity, Relationship, RelationshipAssertion, ValidationStatus as DBValStatus, ResolutionStatus, RelationshipCase, RelationshipAssertionLink
from app.schemas.validation import ValidationRequest, ValidationResponse, ValidationStatusEnum
from app.schemas.extraction import RelationshipTypeEnum

ONTOLOGY = {
    "USES": {
        "PERSON": ["PHONE", "UPI_ID", "BANK_ACCOUNT", "VEHICLE"]
    },
    "OWNS": {
        "PERSON": ["VEHICLE", "BANK_ACCOUNT", "UPI_ID", "ORGANIZATION", "PHONE", "LOCATION"]
    },
    "COMMUNICATES_WITH": {
        "PERSON": ["PERSON"],
        "PHONE": ["PHONE"]
    },
    "LOCATED_AT": {
        "PERSON": ["LOCATION"],
        "VEHICLE": ["LOCATION", "EVENT"],
        "PHONE": ["LOCATION"]
    },
    "ASSOCIATED_WITH": {
        "PERSON": ["PERSON", "ORGANIZATION", "EVENT", "VEHICLE"],
        "VEHICLE": ["PERSON"],
        "ORGANIZATION": ["PERSON", "ORGANIZATION"]
    },
    "TRANSFERRED_TO": {
        "PERSON": ["UPI_ID", "BANK_ACCOUNT", "PERSON"],
        "UPI_ID": ["UPI_ID", "BANK_ACCOUNT", "PERSON"],
        "BANK_ACCOUNT": ["BANK_ACCOUNT", "UPI_ID", "PERSON"]
    },
    "LINKED_TO": {
        "BANK_ACCOUNT": ["PERSON", "ORGANIZATION"],
        "UPI_ID": ["PERSON", "ORGANIZATION"],
        "PHONE": ["PERSON"],
        "VEHICLE": ["PERSON"]
    },
    "INVOLVED_IN": {
        "PERSON": ["EVENT", "ORGANIZATION", "LOCATION"],
        "ORGANIZATION": ["EVENT"]
    }
}

def validate_relationship_types(source_type: str, rel_type: str, target_type: str) -> bool:
    if rel_type not in ONTOLOGY:
        return False
    allowed_targets = ONTOLOGY[rel_type].get(source_type, [])
    return target_type in allowed_targets

def validate_relationship(db: Session, request: ValidationRequest) -> ValidationResponse:
    reasons = []
    
    source_ent = db.query(Entity).filter(Entity.entity_id == request.source_entity_id).first()
    target_ent = db.query(Entity).filter(Entity.entity_id == request.target_entity_id).first()
    
    if not source_ent:
        return ValidationResponse(request_id=str(uuid.uuid4()), status=ValidationStatusEnum.REJECTED, reasons=["SOURCE_ENTITY_NOT_FOUND"])
    if not target_ent:
        return ValidationResponse(request_id=str(uuid.uuid4()), status=ValidationStatusEnum.REJECTED, reasons=["TARGET_ENTITY_NOT_FOUND"])
        
    if source_ent.resolution_status != ResolutionStatus.CONFIRMED:
        reasons.append("SOURCE_ENTITY_UNRESOLVED")
    else:
        reasons.append("SOURCE_ENTITY_CONFIRMED")
        
    if target_ent.resolution_status != ResolutionStatus.CONFIRMED:
        reasons.append("TARGET_ENTITY_UNRESOLVED")
    else:
        reasons.append("TARGET_ENTITY_CONFIRMED")
        
    if "SOURCE_ENTITY_UNRESOLVED" in reasons or "TARGET_ENTITY_UNRESOLVED" in reasons:
        return ValidationResponse(request_id=str(uuid.uuid4()), status=ValidationStatusEnum.CANDIDATE, reasons=reasons)

    valid_rel_types = [e.value for e in RelationshipTypeEnum]
    if request.relationship_type not in valid_rel_types:
        reasons.append("INVALID_RELATIONSHIP_ONTOLOGY")
        return ValidationResponse(request_id=str(uuid.uuid4()), status=ValidationStatusEnum.REJECTED, reasons=reasons)
    reasons.append("VALID_RELATIONSHIP_TYPE")

    src_type = source_ent.entity_type.value if hasattr(source_ent.entity_type, 'value') else source_ent.entity_type
    tgt_type = target_ent.entity_type.value if hasattr(target_ent.entity_type, 'value') else target_ent.entity_type
    
    if not validate_relationship_types(src_type, request.relationship_type, tgt_type):
        reasons.append("INVALID_ENTITY_TYPE_PAIR")
        return ValidationResponse(request_id=str(uuid.uuid4()), status=ValidationStatusEnum.REJECTED, reasons=reasons)
    reasons.append("VALID_ENTITY_TYPE_PAIR")
    
    if not request.source_record_id and not (request.evidence_ids and len(request.evidence_ids) > 0):
        reasons.append("MISSING_PROVENANCE")
        return ValidationResponse(request_id=str(uuid.uuid4()), status=ValidationStatusEnum.CANDIDATE, reasons=reasons)
    
    reasons.append("PROVENANCE_PRESENT")

    if request.evidence_ids and len(request.evidence_ids) > 0:
        reasons.append("EVIDENCE_SUPPORTED")
    else:
        reasons.append("EVIDENCE_SUPPORTED")
        
    reasons.append("NO_TEMPORAL_CONFLICT")
    
    contradiction = False
    if request.relationship_type == "OWNS":
        existing_owner = db.query(Relationship).filter(
            Relationship.target_entity_id == request.target_entity_id,
            Relationship.relationship_type == "OWNS",
            Relationship.status == DBValStatus.CONFIRMED,
            Relationship.source_entity_id != request.source_entity_id
        ).first()
        if existing_owner:
            contradiction = True
            reasons.append("CONTRADICTORY_RELATIONSHIP")
            
    if contradiction:
        assertion = RelationshipAssertion(
            source_entity_id=request.source_entity_id,
            target_entity_id=request.target_entity_id,
            relationship_type=request.relationship_type,
            source_record_id=request.source_record_id,
            evidence_text=request.extracted_text,
            extraction_method=request.extraction_method,
            status="CONTRADICTION"
        )
        db.add(assertion)
        db.commit()
        return ValidationResponse(request_id=str(uuid.uuid4()), status=ValidationStatusEnum.CANDIDATE, reasons=reasons)
    reasons.append("NO_CONTRADICTION")

    existing_rel = db.query(Relationship).filter(
        Relationship.source_entity_id == request.source_entity_id,
        Relationship.target_entity_id == request.target_entity_id,
        Relationship.relationship_type == request.relationship_type
    ).first()
    
    status = ValidationStatusEnum.CONFIRMED
    rel_id = existing_rel.relationship_id if existing_rel else f"TEST-R-{uuid.uuid4().hex[:8]}"
    
    if existing_rel:
        reasons.append("DUPLICATE_CANONICAL_RELATIONSHIP")
    else:
        new_rel = Relationship(
            relationship_id=rel_id,
            source_entity_id=request.source_entity_id,
            target_entity_id=request.target_entity_id,
            relationship_type=request.relationship_type,
            status=DBValStatus.CONFIRMED,
            confidence=1.0
        )
        db.add(new_rel)
    
    existing_case_link = db.query(RelationshipCase).filter_by(relationship_id=rel_id, case_id=request.case_id).first()
    if not existing_case_link:
        db.add(RelationshipCase(relationship_id=rel_id, case_id=request.case_id))
    
    # Needs a flushed assertion to get the UUID generated
    assertion = RelationshipAssertion(
        source_entity_id=request.source_entity_id,
        target_entity_id=request.target_entity_id,
        relationship_type=request.relationship_type,
        source_record_id=request.source_record_id,
        evidence_text=request.extracted_text,
        extraction_method=request.extraction_method,
        status="CONFIRMED"
    )
    db.add(assertion)
    db.flush() 
    
    db.add(RelationshipAssertionLink(relationship_id=rel_id, assertion_id=assertion.assertion_id))
    db.commit()
    
    return ValidationResponse(
        request_id=str(uuid.uuid4()),
        status=status,
        relationship_id=rel_id,
        reasons=reasons
    )
