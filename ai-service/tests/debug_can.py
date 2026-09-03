import json
from pathlib import Path
from app.services.ingestion_service import process_file
from app.services.extractor_service import extract_entities
from app.resolution.resolver import resolve_entities

DATA_DIR = Path('d:/NETRA/SIH2026/ai-service/data/synthetic')

all_mentions = []
for f in (DATA_DIR / 'sources').glob('*'):
    ctype = 'FIR' if 'fir' in f.name else 'CDR' if 'cdr' in f.name else 'TRANSACTION' if 'transaction' in f.name else 'SURVEILLANCE'
    all_mentions.extend(extract_entities(process_file(str(f), ctype)))

canonical_entities = resolve_entities(all_mentions)

with open(DATA_DIR / 'evaluation' / 'mention_ground_truth.json', 'r', encoding='utf-8') as f:
    gt_mentions = json.load(f)

mention_to_gt = {ann["mention_id"]: ann["ground_truth_entity_id"] for ann in gt_mentions}

canonical_to_gt = {}
for ce in canonical_entities:
    gt_ids = set(mention_to_gt.get(sm.mention_id) for sm in ce.source_mentions if mention_to_gt.get(sm.mention_id))
    print(f"{ce.entity_type} Canonical {ce.canonical_name}: GT_IDs {gt_ids}")
