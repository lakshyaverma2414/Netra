import json
import httpx
from pathlib import Path
from typing import Dict, List

from app.services.ingestion_service import process_file
from app.services.extractor_service import extract_entities
from app.resolution.resolver import resolve_entities
from app.services.qwen_relationship_service import extract_qwen_relationships_for_record
from app.llm.qwen_client import QWEN_BASE_URL

DATA_DIR = Path('d:/NETRA/SIH2026/ai-service/data/synthetic')

def check_qwen_health():
    try:
        r = httpx.get(f"{QWEN_BASE_URL}/v1/models", timeout=2)
        return r.status_code == 200
    except:
        return False

def evaluate_qwen():
    if not check_qwen_health():
        print("llama.cpp (Qwen) server is not running on localhost:8080. Skipping Qwen evaluation.")
        return
        
    print("Running Qwen semantic extraction evaluation...")

    all_records = process_file(str(DATA_DIR / 'sources' / 'fir_qwen_eval.json'), 'FIR')
    all_mentions = extract_entities(all_records)
    canonical_entities = resolve_entities(all_mentions)
    
    with open(DATA_DIR / 'evaluation' / 'mention_ground_truth.json', 'r', encoding='utf-8') as f:
        gt_mentions = json.load(f)
    
    mention_to_gt = {ann["mention_id"]: ann["ground_truth_entity_id"] for ann in gt_mentions}
    
    canonical_to_gt = {}
    for ce in canonical_entities:
        gt_ids = set(mention_to_gt.get(sm.mention_id) for sm in ce.source_mentions if mention_to_gt.get(sm.mention_id))
        if len(gt_ids) >= 1:
            canonical_to_gt[ce.entity_id] = list(gt_ids)[0]
    
    predicted_rels = []
    for rec in all_records:
        rels = extract_qwen_relationships_for_record(rec, all_mentions, canonical_entities)
        predicted_rels.extend(rels)
    
    pred_set = set()
    for r in predicted_rels:
        sgt = canonical_to_gt.get(r.source_entity_id)
        tgt = canonical_to_gt.get(r.target_entity_id)
        if sgt and tgt and not r.negated:
            pred_set.add((sgt, r.relationship_type.value, tgt))
            
    with open(DATA_DIR / 'ground_truth' / 'relationships_qwen_eval.json', 'r', encoding='utf-8-sig') as f:
        gt_rels = json.load(f)
        
    gt_set = set()
    for gr in gt_rels:
        gt_set.add((gr["source_entity"], gr["relation_type"], gr["target_entity"]))
        
    tp = pred_set.intersection(gt_set)
    fp = pred_set - gt_set
    fn = gt_set - pred_set
    
    precision = len(tp) / (len(tp) + len(fp)) if (len(tp) + len(fp)) > 0 else 1.0
    recall = len(tp) / (len(tp) + len(fn)) if (len(tp) + len(fn)) > 0 else 1.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    print("========================================")
    print("QWEN M6.2 EVALUATION")
    print("========================================")
    print(f"Extracted Relationships: {len(predicted_rels)}")
    print(f"True Positives (TP):     {len(tp)}")
    print(f"False Positives (FP):    {len(fp)}")
    print(f"False Negatives (FN):    {len(fn)}")
    print(f"\nPrecision:               {precision:.4f}")
    print(f"Recall:                  {recall:.4f}")
    print(f"F1 Score:                {f1:.4f}")

if __name__ == '__main__':
    evaluate_qwen()
