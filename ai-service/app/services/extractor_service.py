from typing import List
from app.schemas.ingestion import NormalizedRecord
from app.schemas.extraction import EntityMention
from app.extraction.entity_extractor import extract_entities_from_record

def extract_entities(records: List[NormalizedRecord]) -> List[EntityMention]:
    all_mentions = []
    for record in records:
        all_mentions.extend(extract_entities_from_record(record))
    return all_mentions
