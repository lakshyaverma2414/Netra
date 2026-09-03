import json
import re
from pathlib import Path
from app.services.ingestion_service import process_file
from app.services.extractor_service import extract_entities

DATA_DIR = Path('d:/NETRA/SIH2026/ai-service/data/synthetic')

with open(DATA_DIR / 'ground_truth' / 'entities.json', 'r', encoding='utf-8-sig') as f:
    gt_data = json.load(f)

def normalize_string(s):
    return re.sub(r'\W+', '', s).lower()
    
# Store lists of strings to check
gt_map = {}
for gt_e in gt_data:
    keys = [gt_e['canonical_name']] + gt_e.get('aliases', [])
    for k in keys:
        n = normalize_string(k)
        gt_map[n] = gt_e['entity_id']
        # If phone, also store the last 10 digits
        if gt_e['entity_type'] == 'PHONE' and len(n) >= 10:
            gt_map[n[-10:]] = gt_e['entity_id']

all_mentions = []
for f in (DATA_DIR / 'sources').glob('*'):
    ctype = 'FIR' if 'fir' in f.name else 'CDR' if 'cdr' in f.name else 'TRANSACTION' if 'transaction' in f.name else 'SURVEILLANCE'
    recs = process_file(str(f), ctype)
    all_mentions.extend(extract_entities(recs))

annotations = []
for m in all_mentions:
    n_key = normalize_string(m.normalized_value)
    
    gt_id = None
    if n_key in gt_map:
        gt_id = gt_map[n_key]
    elif m.entity_type == 'PHONE' and len(n_key) >= 10 and n_key[-10:] in gt_map:
        gt_id = gt_map[n_key[-10:]]
        
    if gt_id:
        annotations.append({
            "mention_id": m.mention_id,
            "text": m.text,
            "ground_truth_entity_id": gt_id
        })

out_dir = DATA_DIR / 'evaluation'
out_dir.mkdir(exist_ok=True)
with open(out_dir / 'mention_ground_truth.json', 'w', encoding='utf-8') as f:
    json.dump(annotations, f, indent=2)

print("Generated mention_ground_truth.json")
