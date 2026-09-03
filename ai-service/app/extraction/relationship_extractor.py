import re
from typing import List, Dict, Tuple, Optional
from app.schemas.ingestion import NormalizedRecord
from app.schemas.extraction import EntityMention
from app.schemas.resolution import CanonicalEntity
from app.schemas.relationship import RelationshipCandidate, RelationshipType

def build_mention_to_canonical_map(canonical_entities: List[CanonicalEntity]) -> Dict[str, str]:
    mapping = {}
    for ce in canonical_entities:
        for prov in ce.source_mentions:
            mapping[prov.mention_id] = ce.entity_id
    return mapping

def extract_relationships(
    record: NormalizedRecord, 
    mentions: List[EntityMention], 
    canonical_entities: List[CanonicalEntity]
) -> List[RelationshipCandidate]:
    
    candidates = []
    mention_to_canonical = build_mention_to_canonical_map(canonical_entities)
    
    # Helper to find a mention by type and value within the record
    def find_canonical(etype: str, text_or_norm: str) -> Optional[str]:
        for m in mentions:
            if m.record_id == record.record_id and m.entity_type == etype:
                if text_or_norm in [m.text, m.normalized_value]:
                    return mention_to_canonical.get(m.mention_id)
        return None
        
    def find_any_canonical(etype: str) -> Optional[str]:
        for m in mentions:
            if m.record_id == record.record_id and m.entity_type == etype:
                return mention_to_canonical.get(m.mention_id)
        return None
    
    if record.content_type == "STRUCTURED" and record.data:
        evidence_id = record.data.get("evidence_id")
        
        if record.source_type == "CDR":
            caller_norm = record.data.get("caller")
            recv_norm = record.data.get("receiver")
            
            src_id = find_canonical("PHONE", caller_norm)
            tgt_id = find_canonical("PHONE", recv_norm)
            
            if src_id and tgt_id:
                candidates.append(RelationshipCandidate(
                    source_entity_id=src_id,
                    relationship_type=RelationshipType.COMMUNICATES_WITH,
                    target_entity_id=tgt_id,
                    source_record_id=record.record_id,
                    evidence_id=evidence_id,
                    extraction_method="STRUCTURED_RULE"
                ))
                
        elif record.source_type == "TRANSACTION":
            sender_norm = record.data.get("sender_account")
            recv_norm = record.data.get("receiver_account")
            
            src_id = find_canonical("UPI_ACCOUNT", sender_norm)
            tgt_id = find_canonical("UPI_ACCOUNT", recv_norm)
            
            if src_id and tgt_id:
                candidates.append(RelationshipCandidate(
                    source_entity_id=src_id,
                    relationship_type=RelationshipType.TRANSFERRED_TO,
                    target_entity_id=tgt_id,
                    source_record_id=record.record_id,
                    evidence_id=evidence_id,
                    extraction_method="STRUCTURED_RULE"
                ))
                
    elif record.content_type == "SEMI_STRUCTURED" and record.data:
        # Surveillance Data
        evidence_id = record.data.get("evidence_id")
        person = record.data.get("observed_person")
        location = record.data.get("location")
        vehicle = record.data.get("vehicle_number")
        notes = record.data.get("notes", "")
        
        person_id = find_canonical("PERSON", person) if person else None
        location_id = find_canonical("LOCATION", location) if location else None
        vehicle_id = find_canonical("VEHICLE", vehicle) if vehicle else None
        
        if person_id and location_id:
            candidates.append(RelationshipCandidate(
                source_entity_id=person_id,
                relationship_type=RelationshipType.LOCATED_AT,
                target_entity_id=location_id,
                source_record_id=record.record_id,
                evidence_id=evidence_id,
                extraction_method="STRUCTURED_RULE"
            ))
            
        if vehicle_id and location_id:
            candidates.append(RelationshipCandidate(
                source_entity_id=vehicle_id,
                relationship_type=RelationshipType.LOCATED_AT,
                target_entity_id=location_id,
                source_record_id=record.record_id,
                evidence_id=evidence_id,
                extraction_method="STRUCTURED_RULE"
            ))
            
        # Unstructured text in notes
        if notes:
            candidates.extend(_extract_from_text(notes, record.record_id, evidence_id, mentions, mention_to_canonical))
            
    elif record.content_type == "TEXT" and record.text:
        # FIR or general text
        evidence_id = record.data.get("evidence_id") if record.data else None
        candidates.extend(_extract_from_text(record.text, record.record_id, evidence_id, mentions, mention_to_canonical))
        
    return candidates

def _extract_from_text(
    text: str, 
    record_id: str, 
    evidence_id: Optional[str],
    mentions: List[EntityMention],
    mention_to_canonical: Dict[str, str]
) -> List[RelationshipCandidate]:
    candidates = []
    
    # Helper to get canonical ID of a mention found in this text block
    def get_canonical_by_type(etype: str) -> Optional[str]:
        for m in mentions:
            if m.record_id == record_id and m.entity_type == etype:
                return mention_to_canonical.get(m.mention_id)
        return None
        
    def get_all_canonicals_by_type(etype: str) -> List[str]:
        ids = []
        for m in mentions:
            if m.record_id == record_id and m.entity_type == etype:
                cid = mention_to_canonical.get(m.mention_id)
                if cid and cid not in ids:
                    ids.append(cid)
        return ids

    lower_text = text.lower()
    
    # Handle negation (simple text rule)
    negated = False
    if "not use" in lower_text or "did not" in lower_text or "does not" in lower_text:
        negated = True
        
    # rule: USES (PERSON -> PHONE)
    if "uses mobile" in lower_text or "using device" in lower_text or "using mobile" in lower_text or "uses international number" in lower_text or "use phone" in lower_text:
        pid = get_canonical_by_type("PERSON")
        phid = get_canonical_by_type("PHONE")
        if pid and phid:
            candidates.append(RelationshipCandidate(
                source_entity_id=pid, relationship_type=RelationshipType.USES, target_entity_id=phid,
                source_record_id=record_id, evidence_id=evidence_id, extraction_method="TEXT_RULE", evidence_text=text, negated=negated
            ))
            
    # rule: OWNS (PERSON -> VEHICLE / UPI)
    if "owns vehicle" in lower_text or "holds registration" in lower_text:
        pid = get_canonical_by_type("PERSON")
        vid = get_canonical_by_type("VEHICLE")
        if pid and vid:
            candidates.append(RelationshipCandidate(
                source_entity_id=pid, relationship_type=RelationshipType.OWNS, target_entity_id=vid,
                source_record_id=record_id, evidence_id=evidence_id, extraction_method="TEXT_RULE", evidence_text=text, negated=negated
            ))
            
    if "owner of upi" in lower_text or "operates financial account" in lower_text:
        pid = get_canonical_by_type("PERSON")
        uid = get_canonical_by_type("UPI_ACCOUNT")
        if pid and uid:
            candidates.append(RelationshipCandidate(
                source_entity_id=pid, relationship_type=RelationshipType.OWNS, target_entity_id=uid,
                source_record_id=record_id, evidence_id=evidence_id, extraction_method="TEXT_RULE", evidence_text=text, negated=negated
            ))
            
    # rule: ASSOCIATED_WITH (PERSON -> ORG)
    if "associate of" in lower_text or "entering" in lower_text or "operational front" in lower_text:
        pid = get_canonical_by_type("PERSON")
        oid = get_canonical_by_type("ORGANIZATION")
        if pid and oid:
            candidates.append(RelationshipCandidate(
                source_entity_id=pid, relationship_type=RelationshipType.ASSOCIATED_WITH, target_entity_id=oid,
                source_record_id=record_id, evidence_id=evidence_id, extraction_method="TEXT_RULE", evidence_text=text, negated=negated
            ))
            
    # rule: LOCATED_AT (PERSON -> LOCATION)
    if "seen near" in lower_text:
        pid = get_canonical_by_type("PERSON")
        lid = get_canonical_by_type("LOCATION")
        if pid and lid:
            candidates.append(RelationshipCandidate(
                source_entity_id=pid, relationship_type=RelationshipType.LOCATED_AT, target_entity_id=lid,
                source_record_id=record_id, evidence_id=evidence_id, extraction_method="TEXT_RULE", evidence_text=text, negated=negated
            ))
            
    # rule: LINKED_TO (PERSON/VEHICLE -> CASE)
    if "linked to" in lower_text:
        vid = get_canonical_by_type("VEHICLE")
        cid = get_canonical_by_type("CASE")
        if vid and cid:
            candidates.append(RelationshipCandidate(
                source_entity_id=vid, relationship_type=RelationshipType.LINKED_TO, target_entity_id=cid,
                source_record_id=record_id, evidence_id=evidence_id, extraction_method="TEXT_RULE", evidence_text=text, negated=negated
            ))
            
        pid = get_canonical_by_type("PERSON")
        if pid and cid:
            candidates.append(RelationshipCandidate(
                source_entity_id=pid, relationship_type=RelationshipType.LINKED_TO, target_entity_id=cid,
                source_record_id=record_id, evidence_id=evidence_id, extraction_method="TEXT_RULE", evidence_text=text, negated=negated
            ))
            
    # rule: INVOLVED_IN (PERSON -> CASE)
    if "suspect" in lower_text or "filed." in lower_text:
        # P001 -> INVOLVED_IN -> CASE001
        pids = get_all_canonicals_by_type("PERSON")
        cid = get_canonical_by_type("CASE")
        if cid:
            for pid in pids:
                candidates.append(RelationshipCandidate(
                    source_entity_id=pid, relationship_type=RelationshipType.INVOLVED_IN, target_entity_id=cid,
                    source_record_id=record_id, evidence_id=evidence_id, extraction_method="TEXT_RULE", evidence_text=text, negated=negated
                ))

    return candidates
