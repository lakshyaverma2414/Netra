import uuid
import difflib
from sqlalchemy.orm import Session
from typing import List, Tuple, Optional
from app.db.models import Entity, EntityAlias, EntityMention, EntityResolutionLog, ResolutionStatus as DBResStatus, CaseEntity
from app.schemas.resolution import ResolutionRequest, ResolutionResponse, ResolutionResultItem, ResolutionStatusEnum
from app.resolution.normalizer import normalize_text
import datetime

def generate_candidates(db: Session, text: str, norm_val: str, entity_type: str) -> List[Tuple[Entity, float, List[str]]]:
    candidates = []
    
    # Tier 1: Exact Identifiers
    db_type = "UPI_ID" if entity_type == "UPI" else ("BANK_ACCOUNT" if entity_type == "ACCOUNT" else entity_type)
    if db_type in ["PHONE", "UPI_ID", "VEHICLE", "CASE", "BANK_ACCOUNT", "EMAIL"]:
        exact_ents = db.query(Entity).filter(Entity.entity_type == db_type).all()
        for e in exact_ents:
            if normalize_text(e.canonical_name, entity_type) == norm_val:
                return [(e, 1.0, ["exact_identifier_match"])]
        return []
    
    # Tier 2 & 3: Person / Location / Org
    
    # Find in Aliases
    norm_no_punct = "".join(c for c in norm_val if c.isalnum() or c.isspace()).strip().upper()
    aliases = db.query(EntityAlias).filter( (EntityAlias.normalized_alias == norm_val) | (EntityAlias.normalized_alias == norm_no_punct) ).all()
    for al in aliases:
        ent = db.query(Entity).filter(Entity.entity_id == al.entity_id).first()
        if ent and ent.entity_type == db_type or (hasattr(ent.entity_type, "value") and ent.entity_type.value == db_type):
            if not any(c[0].entity_id == ent.entity_id for c in candidates):
                candidates.append((ent, 0.95, ["alias_match"]))
    
    # Find exact in Entities
    exact_names = db.query(Entity).filter(Entity.entity_type == db_type).all()
    for ent in exact_names:
        ent_norm = normalize_text(ent.canonical_name, entity_type)
        if ent_norm == norm_val:
            if not any(c[0].entity_id == ent.entity_id for c in candidates):
                candidates.append((ent, 0.90, ["normalized_name_match"]))
        else:
            # Fuzzy match (Tier 4)
            sim = difflib.SequenceMatcher(None, ent_norm, norm_val).ratio()
            if sim > 0.8:
                if not any(c[0].entity_id == ent.entity_id for c in candidates):
                    candidates.append((ent, sim * 0.8, ["fuzzy_name_similarity"]))
    
    # Sort by score descending
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates

def determine_status(candidates: List[Tuple[Entity, float, List[str]]]) -> Tuple[ResolutionStatusEnum, Optional[Entity], float, List[str]]:
    if not candidates:
        return ResolutionStatusEnum.REJECTED, None, 0.0, []
    
    top_score = candidates[0][1]
    
    if len(candidates) > 1:
        second_score = candidates[1][1]
        # Ambiguous identity
        if top_score - second_score < 0.1:
            return ResolutionStatusEnum.CANDIDATE, None, top_score, ["ambiguous_candidates"]
    
    if top_score >= 0.9:
        return ResolutionStatusEnum.CONFIRMED, candidates[0][0], top_score, candidates[0][2]
    elif top_score >= 0.7:
        return ResolutionStatusEnum.PROBABLE, candidates[0][0], top_score, candidates[0][2]
    
    return ResolutionStatusEnum.REJECTED, None, 0.0, []

def resolve_mentions(db: Session, request: ResolutionRequest) -> ResolutionResponse:
    results = []
    req_id = str(uuid.uuid4())
    
    for m in request.mentions:
        norm_val = normalize_text(m.text, m.entity_type.value)
        
        candidates = generate_candidates(db, m.text, norm_val, m.entity_type.value)
        status, matched_ent, score, methods = determine_status(candidates)
        
        db_type = "UPI_ID" if m.entity_type.name == "UPI" else ("BANK_ACCOUNT" if m.entity_type.name == "ACCOUNT" else m.entity_type.name)

        # AUTO-CREATE IF REJECTED
        if status == ResolutionStatusEnum.REJECTED or not matched_ent:
            new_ent = Entity(
                entity_id=f"E-{uuid.uuid4().hex[:8]}",
                entity_type=db_type,
                canonical_name=m.text,
                normalized_value=norm_val,
                resolution_status="CONFIRMED",
                resolution_score=1.0
            )
            db.add(new_ent)
            db.flush() # Make it queryable for the next mention in the loop
            
            matched_ent = new_ent
            status = ResolutionStatusEnum.CONFIRMED
            score = 1.0
            methods = ["auto_created_from_mention"]
            candidates = [(new_ent, score, methods)] # Update candidates for the log

        db_status = DBResStatus.REJECTED
        if status == ResolutionStatusEnum.CONFIRMED:
            db_status = DBResStatus.CONFIRMED
        elif status in [ResolutionStatusEnum.PROBABLE, ResolutionStatusEnum.CANDIDATE]:
            db_status = DBResStatus.CANDIDATE
            
        mention_id = f"M-{uuid.uuid4().hex[:8]}"
        
        # Write Mention
        db_mention = EntityMention(
            mention_id=mention_id,
            entity_type=db_type,
            extracted_text=m.text,
            normalized_value=norm_val,
            extraction_method="Orchestrator",
            extraction_confidence=score,
            source_record_id=m.source_record_id,
            observation_id=m.observation_id,
            resolved_entity_id=matched_ent.entity_id if matched_ent and status == ResolutionStatusEnum.CONFIRMED else None
        )
        db.add(db_mention)
        
        # Write Log
        if candidates:
            # Log the top candidate even if ambiguous
            log_ent = matched_ent if matched_ent else candidates[0][0]
            log_entry = EntityResolutionLog(
                mention_id=mention_id,
                candidate_entity_id=log_ent.entity_id,
                decision=db_status,
                probability=score,
                matching_features={"methods": methods, "ambiguous": status == ResolutionStatusEnum.CANDIDATE},
                resolver_version="entity-resolver-v1"
            )
            db.add(log_entry)
            
            # Associate case if confirmed
            if status == ResolutionStatusEnum.CONFIRMED:
                existing_ce = db.query(CaseEntity).filter_by(case_id=request.case_id, entity_id=matched_ent.entity_id).first()
                if not existing_ce:
                    db.add(CaseEntity(case_id=request.case_id, entity_id=matched_ent.entity_id, association_type="RESOLVED_MENTION"))
                    db.flush()
        
        results.append(ResolutionResultItem(
            mention=m.text,
            entity_type=m.entity_type,
            status=status,
            entity_id=matched_ent.entity_id if matched_ent and status == ResolutionStatusEnum.CONFIRMED else None,
            canonical_name=matched_ent.canonical_name if matched_ent and status == ResolutionStatusEnum.CONFIRMED else None,
            score=score,
            matching_methods=methods
        ))
    
    db.commit()
    return ResolutionResponse(request_id=req_id, results=results)
