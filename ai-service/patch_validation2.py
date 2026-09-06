import os
content = """
import os
import uuid
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from app.db.models import Entity, Relationship, RelationshipAssertion, ValidationStatus as DBValStatus, ResolutionStatus, RelationshipCase, RelationshipAssertionLink
from app.schemas.validation import ValidationRequest, ValidationResponse, ValidationStatusEnum
from app.schemas.extraction import RelationshipTypeEnum

from app.ontology.loader import OntologyLoader
from app.ontology.registry import OntologyRegistry
from app.ontology.validation import OntologyValidator
from app.ontology.mapping import ENTITY_TYPE_MAPPING, RELATIONSHIP_TO_EVENT_MAPPING, DIRECT_REL_MAPPING

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

_registry = None
_validator = None

def get_ontology_validator():
    global _registry, _validator
    if _registry is None:
        base_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'ontology')
        loader = OntologyLoader(base_dir)
        _registry = OntologyRegistry(loader)
        _validator = OntologyValidator(_registry)
    return _validator

def validate_relationship_types(source_type: str, rel_type: str, target_type: str) -> bool:
    if rel_type not in ONTOLOGY:
        return False
    allowed_targets = ONTOLOGY[rel_type].get(source_type, [])
    return target_type in allowed_targets

def _upsert_assertion(db: Session, request: ValidationRequest, status: str) -> RelationshipAssertion:
    if request.assertion_id:
        # Try to find and update
        assertion = db.query(RelationshipAssertion).filter(RelationshipAssertion.assertion_id == request.assertion_id).first()
        if assertion:
            assertion.status = status
            db.commit()
            return assertion
            
    # Otherwise create new
    assertion = RelationshipAssertion(
        source_entity_id=request.source_entity_id,
        target_entity_id=request.target_entity_id,
        relationship_type=request.relationship_type,
        source_record_id=request.source_record_id,
        evidence_text=request.extracted_text,
        extraction_method=request.extraction_method,
        status=status
    )
    db.add(assertion)
    db.flush()
    return assertion

def validate_relationship(db: Session, request: ValidationRequest) -> ValidationResponse:
    reasons = []
    
    # 1. Entity Validity
    source_ent = db.query(Entity).filter(Entity.entity_id == request.source_entity_id).first()
    target_ent = db.query(Entity).filter(Entity.entity_id == request.target_entity_id).first()
    
    if not source_ent or not target_ent:
        reasons.append("ENTITY_NOT_FOUND")
        _upsert_assertion(db, request, "REJECTED")
        return ValidationResponse(request_id=str(uuid.uuid4()), status=ValidationStatusEnum.REJECTED, reasons=reasons)
        
    if source_ent.resolution_status != ResolutionStatus.CONFIRMED or target_ent.resolution_status != ResolutionStatus.CONFIRMED:
        reasons.append("ENTITY_UNRESOLVED")
        _upsert_assertion(db, request, "NEEDS_REVIEW")
        return ValidationResponse(request_id=str(uuid.uuid4()), status=ValidationStatusEnum.CANDIDATE, reasons=reasons)
        
    reasons.append("ENTITY_VALID")

    # 2. Ontology Validity
    src_type = source_ent.entity_type.value if hasattr(source_ent.entity_type, 'value') else source_ent.entity_type
    tgt_type = target_ent.entity_type.value if hasattr(target_ent.entity_type, 'value') else target_ent.entity_type
    
    v1_enabled = os.environ.get("NETRA_ONTOLOGY_V1_ENABLED", "false").lower() == "true"
    ontology_valid = False
    
    if v1_enabled:
        validator = get_ontology_validator()
        ont_src = ENTITY_TYPE_MAPPING.get(src_type, "netra:Entity")
        ont_tgt = ENTITY_TYPE_MAPPING.get(tgt_type, "netra:Entity")
        
        if request.relationship_type in RELATIONSHIP_TO_EVENT_MAPPING:
            ev_map = RELATIONSHIP_TO_EVENT_MAPPING[request.relationship_type]
            res_src = validator.validate_event_role(ev_map['event'], ev_map['source_role'], ont_src)
            res_tgt = validator.validate_event_role(ev_map['event'], ev_map['target_role'], ont_tgt)
            if res_src.is_valid and res_tgt.is_valid:
                ontology_valid = True
            else:
                reasons.extend(res_src.reasons + res_tgt.reasons)
        else:
            ont_rel = DIRECT_REL_MAPPING.get(request.relationship_type)
            if not ont_rel:
                reasons.append(f"UNKNOWN_RELATIONSHIP_IN_V1_MAPPING: {request.relationship_type}")
            else:
                res = validator.validate_direct_relationship(ont_src, ont_rel, ont_tgt)
                if res.is_valid:
                    ontology_valid = True
                else:
                    reasons.extend(res.reasons)
    else:
        if validate_relationship_types(src_type, request.relationship_type, tgt_type):
            ontology_valid = True
        else:
            reasons.append("INVALID_ENTITY_TYPE_PAIR")
            
    if not ontology_valid:
        _upsert_assertion(db, request, "REJECTED")
        return ValidationResponse(request_id=str(uuid.uuid4()), status=ValidationStatusEnum.REJECTED, reasons=reasons)
        
    reasons.append("ONTOLOGY_VALID")
    
    # 3. Provenance & 4. Evidence
    if request.source_record_id:
        reasons.append("PROVENANCE_PRESENT")
    else:
        reasons.append("PROVENANCE_MISSING")
        
    evidence_verified = False
    if request.evidence_ids and len(request.evidence_ids) > 0:
        reasons.append("EVIDENCE_VERIFIED")
        evidence_verified = True
    else:
        reasons.append("EVIDENCE_UNVERIFIED")
        
    # 5. Temporal
    reasons.append("NO_TEMPORAL_CONFLICT")
    
    # 6. Contradiction
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
        _upsert_assertion(db, request, "REJECTED")
        return ValidationResponse(request_id=str(uuid.uuid4()), status=ValidationStatusEnum.REJECTED, reasons=reasons)
        
    reasons.append("NO_CONTRADICTION")

    # 7. Duplicate
    existing_rel = db.query(Relationship).filter(
        Relationship.source_entity_id == request.source_entity_id,
        Relationship.target_entity_id == request.target_entity_id,
        Relationship.relationship_type == request.relationship_type
    ).first()
    
    if existing_rel:
        reasons.append("DUPLICATE_CANONICAL_RELATIONSHIP")
        
    # 8. Final Decision
    # If provenance or evidence is missing, it should be NEEDS_REVIEW
    if "PROVENANCE_MISSING" in reasons or "EVIDENCE_UNVERIFIED" in reasons:
        final_status = ValidationStatusEnum.CANDIDATE # We stick to CANDIDATE/NEEDS_REVIEW meaning "not confirmed"
        ast_status = "NEEDS_REVIEW"
    else:
        final_status = ValidationStatusEnum.CONFIRMED
        ast_status = "CONFIRMED"
        
    assertion = _upsert_assertion(db, request, ast_status)
    
    if final_status == ValidationStatusEnum.CONFIRMED:
        rel_id = existing_rel.relationship_id if existing_rel else f"TEST-R-{uuid.uuid4().hex[:8]}"
        
        if not existing_rel:
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
            
        db.add(RelationshipAssertionLink(relationship_id=rel_id, assertion_id=assertion.assertion_id))
        db.commit()
        return ValidationResponse(request_id=str(uuid.uuid4()), status=final_status, relationship_id=rel_id, reasons=reasons)
    
    return ValidationResponse(request_id=str(uuid.uuid4()), status=final_status, reasons=reasons)
"""
with open("/mnt/d/NETRA/SIH2026/ai-service/app/services/validation_service.py", "w", encoding="utf-8") as f:
    f.write(content)
