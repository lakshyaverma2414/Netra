import json
from pathlib import Path
from app.services.ingestion_service import process_file
from app.services.extractor_service import extract_entities
from app.resolution.resolver import resolve_entities
from app.services.relationship_service import extract_all_relationships

DATA_DIR = Path('d:/NETRA/SIH2026/ai-service/data/synthetic')

all_records = []
all_mentions = []
for f in (DATA_DIR / 'sources').glob('*'):
    ctype = 'FIR' if 'fir' in f.name else 'CDR' if 'cdr' in f.name else 'TRANSACTION' if 'transaction' in f.name else 'SURVEILLANCE'
    recs = process_file(str(f), ctype)
    all_records.extend(recs)
    all_mentions.extend(extract_entities(recs))

canonical_entities = resolve_entities(all_mentions)
predicted_rels = extract_all_relationships(all_records, all_mentions, canonical_entities)

for r in predicted_rels:
    if r.relationship_type.value == "COMMUNICATES_WITH":
        print(f"CDR REL: {r.source_entity_id} -> {r.target_entity_id}")
