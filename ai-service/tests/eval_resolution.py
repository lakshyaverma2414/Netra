import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path

from app.services.ingestion_service import process_file
from app.services.extractor_service import extract_entities
from app.resolution.resolver import resolve_entities
from app.schemas.extraction import EntityMention

DATA_DIR = Path('d:/NETRA/SIH2026/ai-service/data/synthetic')

def classify_missed_match(m1: EntityMention, m2: EntityMention):
    # Determine the reason for failure
    if m1.entity_type != m2.entity_type:
        return "NORMALIZATION / EXTRACTION"
    
    t1 = m1.normalized_value.lower()
    t2 = m2.normalized_value.lower()
    
    # If they are completely different strings like Rocky and Rahul Sharma
    import difflib
    sim = difflib.SequenceMatcher(None, t1, t2).ratio()
    
    if sim < 0.6:
        return "MISSING_EVIDENCE (Requires relationship/co-reference)"
    elif sim < 0.85:
        return "SIMILARITY / THRESHOLD (Score too low without calibration)"
    else:
        return "BLOCKING (Failed candidate generation rules)"

def evaluate():
    all_mentions = []
    sources_dir = DATA_DIR / 'sources'
    for f in sources_dir.glob('*'):
        ctype = 'FIR' if 'fir' in f.name else 'CDR' if 'cdr' in f.name else 'TRANSACTION' if 'transaction' in f.name else 'SURVEILLANCE'
        recs = process_file(str(f), ctype)
        all_mentions.extend(extract_entities(recs))

    predicted_entities = resolve_entities(all_mentions)
    
    pred_pairs = set()
    for e in predicted_entities:
        mention_ids = sorted([m.mention_id for m in e.source_mentions])
        for p in combinations(mention_ids, 2):
            pred_pairs.add(p)

    with open(DATA_DIR / 'evaluation' / 'mention_ground_truth.json', 'r', encoding='utf-8') as f:
        gt_annotations = json.load(f)
        
    mention_to_gt = {ann["mention_id"]: ann["ground_truth_entity_id"] for ann in gt_annotations}
            
    gt_clusters = defaultdict(list)
    mention_dict = {}
    for m in all_mentions:
        mention_dict[m.mention_id] = m
        gt_id = mention_to_gt.get(m.mention_id)
        if gt_id:
            gt_clusters[gt_id].append(m.mention_id)
        else:
            gt_clusters[m.mention_id].append(m.mention_id)

    gt_pairs = set()
    for c_id, m_list in gt_clusters.items():
        sorted_m = sorted(m_list)
        for p in combinations(sorted_m, 2):
            gt_pairs.add(p)
            
    tp = pred_pairs.intersection(gt_pairs)
    fp = pred_pairs - gt_pairs
    fn = gt_pairs - pred_pairs
    
    precision = len(tp) / (len(tp) + len(fp)) if (len(tp) + len(fp)) > 0 else 1.0
    recall = len(tp) / (len(tp) + len(fn)) if (len(tp) + len(fn)) > 0 else 1.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    print("========================================")
    print("ENTITY RESOLUTION EVALUATION")
    print("========================================")
    print(f"\nTotal mentions:        {len(all_mentions)}")
    print(f"Predicted clusters:    {len(predicted_entities)}")
    print(f"Ground-truth clusters: {len(gt_clusters)}")
    print(f"\nTrue Positive pairs:   {len(tp)}")
    print(f"False Positive pairs:  {len(fp)}")
    print(f"False Negative pairs:  {len(fn)}")
    print(f"\nPrecision:             {precision:.4f}")
    print(f"Recall:                {recall:.4f}")
    print(f"F1:                    {f1:.4f}")
    print(f"\nFalse merges:          {len(fp)}")
    print(f"Missed matches:        {len(fn)}")
    
    print("\n----------------------------------------")
    print("FALSE MERGES")
    print("----------------------------------------")
    if not fp:
        print("None")
    for u, v in fp:
        mu = mention_dict[u]
        mv = mention_dict[v]
        print(f"Mention A: {mu.text} | Mention B: {mv.text} | Cause: CLUSTERING / PROBABILISTIC_OVERMERGE")

    print("\n----------------------------------------")
    print("MISSED MATCHES")
    print("----------------------------------------")
    if not fn:
        print("None")
    for u, v in fn:
        mu = mention_dict[u]
        mv = mention_dict[v]
        cause = classify_missed_match(mu, mv)
        print(f"Mention A: {mu.text:<15} | Mention B: {mv.text:<18} | Cause: {cause}")

    print("\n----------------------------------------")
    print("ADVERSARIAL CASES")
    print("----------------------------------------")
    
    def test_adversarial(m1_text, m2_text):
        m1 = EntityMention(record_id="T1", entity_type="PERSON", text=m1_text, normalized_value=m1_text, extraction_method="T", confidence=1.0)
        m2 = EntityMention(record_id="T2", entity_type="PERSON", text=m2_text, normalized_value=m2_text, extraction_method="T", confidence=1.0)
        res = resolve_entities([m1, m2])
        return "PASS" if len(res) == 2 else "FAIL"

    print(f"Rahul Sharma vs Rahul Verma     {test_adversarial('Rahul Sharma', 'Rahul Verma')}")
    print(f"Amit Kumar vs Amit Sharma       {test_adversarial('Amit Kumar', 'Amit Sharma')}")
    
    # Bridge attack
    m1 = EntityMention(record_id="T1", entity_type="PERSON", text="Rahul Sharma", normalized_value="Rahul Sharma", extraction_method="T", confidence=1.0)
    m2 = EntityMention(record_id="T2", entity_type="PERSON", text="R Sharma", normalized_value="R Sharma", extraction_method="T", confidence=1.0)
    m3 = EntityMention(record_id="T3", entity_type="PERSON", text="R Sharmaa", normalized_value="R Sharmaa", extraction_method="T", confidence=1.0)
    m4 = EntityMention(record_id="T4", entity_type="PERSON", text="R Sharmaaa", normalized_value="R Sharmaaa", extraction_method="T", confidence=1.0)
    res = resolve_entities([m1, m2, m3, m4])
    m1_entity = next((e for e in res if any(sm.mention_id == m1.mention_id for sm in e.source_mentions)), None)
    m4_entity = next((e for e in res if any(sm.mention_id == m4.mention_id for sm in e.source_mentions)), None)
    
    bridge_pass = "FAIL"
    if m1_entity and m4_entity and m1_entity.entity_id != m4_entity.entity_id:
        bridge_pass = "PASS"
        
    print(f"Bridge over-merge               {bridge_pass}")

if __name__ == '__main__':
    evaluate()
