import json
import time
import httpx
from sqlalchemy import create_engine, text
import pandas as pd
from collections import defaultdict

# ==========================================
# NETRA STEP 10.3 EVALUATION SCRIPT
# ==========================================
# Run this script while the FastAPI AI Service 
# and the llama.cpp server are BOTH running.

DB_URL = "postgresql+psycopg2://postgres:netra_secure_dev_password@127.0.0.1:5433/postgres" 
API_URL = "http://127.0.0.1:8001/api/v1/extraction"

def fetch_ground_truth():
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        # Fetch actual synthetic documents from Step 9.1
        records = conn.execute(text("SELECT record_id, case_id, raw_payload->>'text' as text FROM source_records")).fetchall()
        source_texts = {r[0]: (r[1], r[2]) for r in records}
        
        # Fetch ground truth relationships 
        rels = conn.execute(text("""
            SELECT ra.source_record_id, e1.canonical_name as src_name, ra.relationship_type, e2.canonical_name as tgt_name 
            FROM relationship_assertions ra
            JOIN entities e1 ON ra.source_entity_id = e1.entity_id
            JOIN entities e2 ON ra.target_entity_id = e2.entity_id
            WHERE ra.status = 'ACCEPTED' OR ra.status = 'NEEDS_REVIEW'
        """)).fetchall()
        
        gt_relationships = defaultdict(list)
        for r in rels:
            gt_relationships[r[0]].append({
                "source": r[1].lower(),
                "type": r[2],
                "target": r[3].lower()
            })
            
    return source_texts, gt_relationships

def evaluate():
    print("Fetching Step 9.1 documents and ground truth from PostgreSQL...")
    try:
        source_texts, gt_relationships = fetch_ground_truth()
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return

    report_lines = [
        "# NETRA_STEP10_3_EVALUATION_REPORT_V1",
        "",
        "## A. Model",
        "* Qwen model: Qwen3-4B-Instruct-2507 (Q4_K_M)",
        "* Llama.cpp backend: httpx client via FastAPI",
        "",
        "## B. Dataset",
        f"* Number of documents evaluated: {len(source_texts)}",
        "",
        "## C. Performance Metrics",
    ]
    
    tp = fp = fn = 0
    raw_examples = []
    
    print(f"Evaluating Qwen across {len(source_texts)} documents...")
    
    with httpx.Client(timeout=60.0) as client:
        for rec_id, (case_id, text_data) in source_texts.items():
            if not text_data: continue
            
            start_time = time.time()
            try:
                # Calls the real local Qwen via FastAPI
                res = client.post(f"{API_URL}/relationships", json={
                    "case_id": case_id,
                    "text": text_data
                })
                extracted = res.json().get("relationships", [])
            except Exception as e:
                print(f"Error calling extraction API for {rec_id}. Ensure llama.cpp is running! ({e})")
                extracted = []
            
            latency = time.time() - start_time
            
            # Entity Resolution is skipped here (per instructions). 
            # We strictly evaluate if Qwen extracted the semantic mention.
            pred_set = set((r.get("source_mention", "").lower(), r.get("relationship_type"), r.get("target_mention", "").lower()) for r in extracted)
            
            gt_list = gt_relationships.get(rec_id, [])
            gt_set = set((g["source"], g["type"], g["target"]) for g in gt_list)
            
            tp_set = pred_set.intersection(gt_set)
            fp_set = pred_set - gt_set
            fn_set = gt_set - pred_set
            
            tp += len(tp_set)
            fp += len(fp_set)
            fn += len(fn_set)
            
            raw_examples.append({
                "record_id": rec_id,
                "text": text_data,
                "predicted": list(pred_set),
                "ground_truth": list(gt_set),
                "latency": f"{latency:.2f}s",
                "false_positives": list(fp_set),
                "false_negatives": list(fn_set)
            })
                
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    report_lines.extend([
        f"- **True Positives**: {tp}",
        f"- **False Positives**: {fp}",
        f"- **False Negatives**: {fn}",
        f"- **Precision**: {precision:.2f}",
        f"- **Recall**: {recall:.2f}",
        f"- **F1 Score**: {f1:.2f}",
        "",
        "## D. Raw Examples and Failure Analysis"
    ])
    
    for ex in raw_examples:
        report_lines.extend([
            f"### Source Record: {ex['record_id']}",
            f"> {ex['text']}",
            f"**Latency**: {ex['latency']}",
            "",
            "**Predicted (Qwen Candidates)**:",
            f"```json\n{json.dumps(ex['predicted'], indent=2)}\n```",
            "**Ground Truth (PostgreSQL)**:",
            f"```json\n{json.dumps(ex['ground_truth'], indent=2)}\n```",
            "**False Positives (Hallucinations/Over-extractions)**:",
            f"```json\n{json.dumps(ex['false_positives'], indent=2)}\n```",
            "**False Negatives (Missed by Model)**:",
            f"```json\n{json.dumps(ex['false_negatives'], indent=2)}\n```",
            "---"
        ])
        
    with open("NETRA_STEP10_3_EVALUATION_REPORT_V1.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print("SUCCESS: Report generated at NETRA_STEP10_3_EVALUATION_REPORT_V1.md")

if __name__ == "__main__":
    evaluate()
