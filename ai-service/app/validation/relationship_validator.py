import hashlib
from typing import List, Dict, Set, Tuple
from datetime import datetime

from app.schemas.ingestion import NormalizedRecord
from app.schemas.resolution import CanonicalEntity
from app.schemas.relationship import RelationshipCandidate, RelationshipType
from app.schemas.validation import RelationshipValidationResult, ValidationStatus

RELATIONSHIP_SCHEMA = {
    "USES": {("PERSON", "PHONE"), ("PERSON", "VEHICLE"), ("PERSON", "UPI_ACCOUNT")},
    "OWNS": {("PERSON", "PHONE"), ("PERSON", "VEHICLE"), ("PERSON", "UPI_ACCOUNT")},
    "COMMUNICATES_WITH": {("PERSON", "PERSON"), ("PHONE", "PHONE")},
    "TRANSFERRED_TO": {("UPI_ACCOUNT", "UPI_ACCOUNT")},
    "LOCATED_AT": {("PERSON", "LOCATION"), ("VEHICLE", "LOCATION")},
    "ASSOCIATED_WITH": {("PERSON", "PERSON")},
    "LINKED_TO": {("*", "*")},
    "INVOLVED_IN": {("PERSON", "CASE"), ("VEHICLE", "CASE"), ("PHONE", "CASE")}
}

def generate_rel_id(src: str, rel: str, tgt: str) -> str:
    return hashlib.md5(f"{src}_{rel}_{tgt}".encode()).hexdigest()

class RelationshipValidator:
    def __init__(self, records: List[NormalizedRecord], canonical_entities: List[CanonicalEntity]):
        self.records_map = {r.record_id: r for r in records}
        self.entity_map = {ce.entity_id: ce for ce in canonical_entities}

    def validate(self, candidates: List[RelationshipCandidate]) -> List[RelationshipValidationResult]:
        grouped: Dict[Tuple[str, str, str], List[RelationshipCandidate]] = {}
        for cand in candidates:
            key = (cand.source_entity_id, cand.relationship_type.value, cand.target_entity_id)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(cand)
            
        results = []
        for key, cands in grouped.items():
            results.append(self._validate_group(key, cands))
            
        return results

    def _validate_group(self, key: Tuple[str, str, str], cands: List[RelationshipCandidate]) -> RelationshipValidationResult:
        src_id, rel_type, tgt_id = key
        
        rel_id = generate_rel_id(src_id, rel_type, tgt_id)
        status = ValidationStatus.CONFIRMED
        checks = {}
        reasons = []
        
        has_affirmative = any(not c.negated for c in cands)
        has_negated = any(c.negated for c in cands)
        
        all_sources = list(set([c.source_record_id for c in cands]))
        all_evidences = list(set([c.evidence_id for c in cands if c.evidence_id]))
        
        if has_affirmative and has_negated:
            status = ValidationStatus.NEEDS_REVIEW
            reasons.append("CONTRADICTORY_EVIDENCE")
            checks["contradiction_check"] = "FAILED"
        else:
            checks["contradiction_check"] = "PASSED"
            
        if not has_affirmative:
            return RelationshipValidationResult(
                relationship_id=rel_id,
                status=ValidationStatus.REJECTED,
                source_entity_id=src_id,
                relationship_type=rel_type,
                target_entity_id=tgt_id,
                checks={"negation_check": "FAILED", "contradiction_check": "PASSED"},
                reasons=["NEGATED_RELATIONSHIP"],
                source_record_ids=all_sources,
                evidence_ids=all_evidences
            )
            
        checks["negation_check"] = "PASSED"
        
        src_ent = self.entity_map.get(src_id)
        tgt_ent = self.entity_map.get(tgt_id)
        
        if not src_ent or not tgt_ent:
            status = ValidationStatus.REJECTED
            reasons.append("MISSING_ENTITY")
            checks["entity_check"] = "FAILED"
        else:
            if src_id == tgt_id and rel_type not in ["LINKED_TO"]:
                status = ValidationStatus.REJECTED
                reasons.append("SELF_REFERENTIAL_RELATIONSHIP")
                checks["entity_check"] = "FAILED"
            else:
                checks["entity_check"] = "PASSED"
            
        if checks.get("entity_check") == "PASSED":
            allowed_types = RELATIONSHIP_SCHEMA.get(rel_type)
            if not allowed_types:
                status = ValidationStatus.REJECTED
                reasons.append("UNSUPPORTED_ONTOLOGY")
                checks["ontology_check"] = "FAILED"
            else:
                is_valid_types = False
                for st, tt in allowed_types:
                    if st == "*" or (st == src_ent.entity_type and tt == tgt_ent.entity_type):
                        is_valid_types = True
                        break
                if not is_valid_types:
                    status = ValidationStatus.REJECTED
                    reasons.append("INVALID_ONTOLOGY_TYPES")
                    checks["ontology_check"] = "FAILED"
                else:
                    checks["ontology_check"] = "PASSED"
        
        source_check_passed = True
        evidence_check_passed = True
        
        for cand in cands:
            rec = self.records_map.get(cand.source_record_id)
            if not rec:
                source_check_passed = False
                reasons.append(f"SOURCE_RECORD_NOT_FOUND: {cand.source_record_id}")
                continue
                
            if cand.extraction_method in ["QWEN_SEMANTIC", "TEXT_RULE"] and not cand.negated:
                if not cand.evidence_text:
                    evidence_check_passed = False
                    reasons.append("MISSING_EVIDENCE")
                else:
                    rec_text = rec.text if rec.text else rec.data.get("notes", "")
                    if not rec_text or cand.evidence_text.lower() not in rec_text.lower():
                        evidence_check_passed = False
                        reasons.append("UNSUPPORTED_EVIDENCE_TEXT")

        checks["source_check"] = "PASSED" if source_check_passed else "FAILED"
        checks["evidence_check"] = "EVIDENCE_TEXT_TRACEABLE" if evidence_check_passed else "FAILED"
        
        if not source_check_passed or not evidence_check_passed:
            status = ValidationStatus.REJECTED
            
        checks["temporal_check"] = "UNKNOWN"
        checks["spatial_check"] = "UNKNOWN"
        for cand in cands:
            if cand.temporal_context:
                checks["temporal_check"] = "SUPPORTED"
            if cand.location_context:
                checks["spatial_check"] = "SUPPORTED"
        
        checks["duplicate_check"] = "MERGED" if len(cands) > 1 else "PASSED"

        return RelationshipValidationResult(
            relationship_id=rel_id,
            status=status,
            source_entity_id=src_id,
            relationship_type=rel_type,
            target_entity_id=tgt_id,
            checks=checks,
            reasons=list(set(reasons)),
            source_record_ids=all_sources,
            evidence_ids=all_evidences
        )
