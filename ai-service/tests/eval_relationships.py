import json
from pathlib import Path
from typing import Dict, List

from app.services.ingestion_service import process_file
from app.services.extractor_service import extract_entities
from app.resolution.resolver import resolve_entities
from app.services.relationship_service import extract_all_relationships

DATA_DIR = Path('d:/NETRA/SIH2026/ai-service/data/synthetic')

def evaluate():
    # 1. Process records and extract mentions
    all_records = []
    all_mentions = []
    for f in (DATA_DIR / 'sources').glob('*'):
        ctype = 'FIR' if 'fir' in f.name else 'CDR' if 'cdr' in f.name else 'TRANSACTION' if 'transaction' in f.name else 'SURVEILLANCE'
        recs = process_file(str(f), ctype)
        all_records.extend(recs)
        all_mentions.extend(extract_entities(recs))

    # 2. Resolve entities
    canonical_entities = resolve_entities(all_mentions)
    
    # 3. Load mention GT to map Canonical -> GT
    with open(DATA_DIR / 'evaluation' / 'mention_ground_truth.json', 'r', encoding='utf-8') as f:
        gt_mentions = json.load(f)
    
    mention_to_gt = {ann["mention_id"]: ann["ground_truth_entity_id"] for ann in gt_mentions}
    
    canonical_to_gt = {}
    for ce in canonical_entities:
        # Get the GT ID for the mentions inside this canonical entity
        gt_ids = set(mention_to_gt.get(sm.mention_id) for sm in ce.source_mentions if mention_to_gt.get(sm.mention_id))
        if len(gt_ids) == 1:
            canonical_to_gt[ce.entity_id] = gt_ids.pop()
        elif len(gt_ids) > 1:
            # It's an over-merge; we can pick one or skip. We'll just pick the first.
            canonical_to_gt[ce.entity_id] = list(gt_ids)[0]
    
    # 4. Extract Relationships
    predicted_rels = extract_all_relationships(all_records, all_mentions, canonical_entities)
    
    # 5. Build predicted GT set: (source_gt, type, target_gt)
    pred_set = set()
    for r in predicted_rels:
        sgt = canonical_to_gt.get(r.source_entity_id)
        tgt = canonical_to_gt.get(r.target_entity_id)
        if sgt and tgt and not r.negated:
            pred_set.add((sgt, r.relationship_type.value, tgt))
            
    # 6. Load Ground Truth relationships
    with open(DATA_DIR / 'ground_truth' / 'relationships.json', 'r', encoding='utf-8-sig') as f:
        gt_rels = json.load(f)
        
    gt_set = set()
    for gr in gt_rels:
        gt_set.add((gr["source_entity"], gr["relation_type"], gr["target_entity"]))
        
    # Evaluate
    tp = pred_set.intersection(gt_set)
    fp = pred_set - gt_set
    fn = gt_set - pred_set
    
    precision = len(tp) / (len(tp) + len(fp)) if (len(tp) + len(fp)) > 0 else 1.0
    recall = len(tp) / (len(tp) + len(fn)) if (len(tp) + len(fn)) > 0 else 1.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    print("========================================")
    print("RELATIONSHIP EXTRACTION EVALUATION")
    print("========================================")
    print(f"\nExtracted Relationships: {len(predicted_rels)}")
    print(f"Mapped Predicted Set:    {len(pred_set)}")
    print(f"Ground Truth Set:        {len(gt_set)}")
    print(f"\nTrue Positives (TP):     {len(tp)}")
    print(f"False Positives (FP):    {len(fp)}")
    print(f"False Negatives (FN):    {len(fn)}")
    print(f"\nPrecision:               {precision:.4f}")
    print(f"Recall:                  {recall:.4f}")
    print(f"F1 Score:                {f1:.4f}")
    
    print("\n----------------------------------------")
    print("FALSE POSITIVES (FP)")
    print("----------------------------------------")
    if not fp: print("None")
    for f in fp:
        print(f"{f[0]} -> {f[1]} -> {f[2]}")
        
    print("\n----------------------------------------")
    print("FALSE NEGATIVES (FN)")
    print("----------------------------------------")
    if not fn: print("None")
    for f in fn:
        print(f"{f[0]} -> {f[1]} -> {f[2]}")

if __name__ == '__main__':
    evaluate()
