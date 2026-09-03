from typing import List
from app.schemas.ingestion import NormalizedRecord
from app.schemas.extraction import EntityMention
from app.schemas.resolution import CanonicalEntity
from app.schemas.relationship import RelationshipCandidate
from app.extraction.relationship_extractor import extract_relationships

def extract_all_relationships(
    records: List[NormalizedRecord],
    mentions: List[EntityMention],
    canonical_entities: List[CanonicalEntity]
) -> List[RelationshipCandidate]:
    all_candidates = []
    
    # We pass the full lists down to the extractor
    for record in records:
        record_mentions = [m for m in mentions if m.record_id == record.record_id]
        candidates = extract_relationships(record, record_mentions, canonical_entities)
        all_candidates.extend(candidates)
        
    return all_candidates
