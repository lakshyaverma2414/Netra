import logging
from typing import List, Dict, Optional
from app.schemas.ingestion import NormalizedRecord
from app.schemas.extraction import EntityMention
from app.schemas.resolution import CanonicalEntity
from app.schemas.relationship import RelationshipCandidate
from app.llm.qwen_client import extract_relationships_with_qwen

logger = logging.getLogger(__name__)

def build_text_to_canonical_map(
    record_id: str,
    mentions: List[EntityMention], 
    canonical_entities: List[CanonicalEntity]
) -> Dict[str, str]:
    # Maps lowercase mention text -> canonical entity ID
    mapping = {}
    
    # build mention_id -> canonical_id
    m_to_c = {}
    for ce in canonical_entities:
        for prov in ce.source_mentions:
            m_to_c[prov.mention_id] = ce.entity_id
            
    for m in mentions:
        if m.record_id == record_id:
            cid = m_to_c.get(m.mention_id)
            if cid:
                mapping[m.text.lower()] = cid
                mapping[m.normalized_value.lower()] = cid
                
    return mapping

def extract_qwen_relationships_for_record(
    record: NormalizedRecord,
    mentions: List[EntityMention],
    canonical_entities: List[CanonicalEntity]
) -> List[RelationshipCandidate]:
    candidates = []
    
    if record.content_type != "TEXT" and not (record.content_type == "SEMI_STRUCTURED" and record.data and "notes" in record.data):
        return candidates
        
    text_to_process = record.text if record.content_type == "TEXT" else record.data.get("notes", "")
    if not text_to_process:
        return candidates
        
    llm_resp = extract_relationships_with_qwen(text_to_process)
    if not llm_resp:
        return candidates
        
    text_to_canonical = build_text_to_canonical_map(record.record_id, mentions, canonical_entities)
    evidence_id = record.data.get("evidence_id") if record.data else None
    
    for llm_rel in llm_resp.relationships:
        src_cid = text_to_canonical.get(llm_rel.source_text.lower())
        tgt_cid = text_to_canonical.get(llm_rel.target_text.lower())
        
        if src_cid and tgt_cid:
            candidates.append(RelationshipCandidate(
                source_entity_id=src_cid,
                relationship_type=llm_rel.relationship_type,
                target_entity_id=tgt_cid,
                source_record_id=record.record_id,
                evidence_id=evidence_id,
                extraction_method="QWEN_SEMANTIC",
                evidence_text=llm_rel.evidence_text,
                negated=llm_rel.negated,
                temporal_context=llm_rel.temporal_context,
                location_context=llm_rel.location_context,
                status="CANDIDATE"
            ))
        else:
            logger.warning(f"Qwen mapped unknown entities: {llm_rel.source_text} or {llm_rel.target_text}")
            
    return candidates
