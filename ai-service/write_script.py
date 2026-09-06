import os
content = """
import os
import csv
import sys
from collections import defaultdict

sys.path.insert(0, "/mnt/d/NETRA/SIH2026/ai-service")
from sqlalchemy import create_engine, text
from app.ontology.loader import OntologyLoader
from app.ontology.registry import OntologyRegistry
from app.ontology.validation import OntologyValidator
from app.ontology.mapping import ENTITY_TYPE_MAPPING, RELATIONSHIP_TO_EVENT_MAPPING, DIRECT_REL_MAPPING

LEGACY_ONTOLOGY = {
    "USES": {"PERSON": ["PHONE", "UPI_ID", "BANK_ACCOUNT", "VEHICLE"]},
    "OWNS": {"PERSON": ["VEHICLE", "BANK_ACCOUNT", "UPI_ID", "ORGANIZATION", "PHONE", "LOCATION"]},
    "COMMUNICATES_WITH": {"PERSON": ["PERSON"], "PHONE": ["PHONE"]},
    "LOCATED_AT": {"PERSON": ["LOCATION"], "VEHICLE": ["LOCATION", "EVENT"], "PHONE": ["LOCATION"]},
    "ASSOCIATED_WITH": {"PERSON": ["PERSON", "ORGANIZATION", "EVENT", "VEHICLE"], "VEHICLE": ["PERSON"], "ORGANIZATION": ["PERSON", "ORGANIZATION"]},
    "TRANSFERRED_TO": {"PERSON": ["UPI_ID", "BANK_ACCOUNT", "PERSON"], "UPI_ID": ["UPI_ID", "BANK_ACCOUNT", "PERSON"], "BANK_ACCOUNT": ["BANK_ACCOUNT", "UPI_ID", "PERSON"]},
    "LINKED_TO": {"BANK_ACCOUNT": ["PERSON", "ORGANIZATION"], "UPI_ID": ["PERSON", "ORGANIZATION"], "PHONE": ["PERSON"], "VEHICLE": ["PERSON"]},
    "INVOLVED_IN": {"PERSON": ["EVENT", "ORGANIZATION", "LOCATION"], "ORGANIZATION": ["EVENT"]}
}

def validate_legacy(src, rel, tgt):
    if rel not in LEGACY_ONTOLOGY: return "REJECTED", "INVALID_RELATIONSHIP"
    if tgt not in LEGACY_ONTOLOGY[rel].get(src, []): return "REJECTED", "INVALID_PAIR"
    return "CONFIRMED", "SUPPORTED"

def run_experiment():
    engine = create_engine('postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres')
    
    loader = OntologyLoader("/mnt/d/NETRA/SIH2026/ai-service/ontology")
    registry = OntologyRegistry(loader)
    validator = OntologyValidator(registry)
    
    reports_dir = "/mnt/d/NETRA/SIH2026/ai-service/reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    delta_csv = os.path.join(reports_dir, "ontology_v1_relationship_delta.csv")
    agg_csv = os.path.join(reports_dir, "ontology_v1_before_after.csv")
    
    deltas = []
    metrics = defaultdict(lambda: {
        "baseline_entities": 0, "v1_entities": 0,
        "baseline_assertions": 0, "v1_assertions": 0,
        "baseline_confirmed": 0, "v1_confirmed": 0,
        "baseline_needs_review": 0, "v1_needs_review": 0,
        "baseline_rejected": 0, "v1_rejected": 0,
        "baseline_age_edges": 0, "v1_age_edges": 0,
        "provenance_complete_before": "Yes", "provenance_complete_after": "Yes",
        "cross_case_links_before": 0, "cross_case_links_after": 0
    })
    
    with engine.connect() as conn:
        cases = conn.execute(text("SELECT case_id FROM cases")).fetchall()
        for c in cases:
            case_id = c[0]
            ent_count = conn.execute(text("SELECT count(DISTINCT entity_id) FROM case_entities WHERE case_id = :c"), {"c": case_id}).scalar()
            metrics[case_id]["baseline_entities"] = ent_count
            metrics[case_id]["v1_entities"] = ent_count
            
        q = text(\"\"\"
            SELECT a.assertion_id, a.source_entity_id, a.target_entity_id, a.relationship_type, a.status,
                   e1.entity_type as src_type, e2.entity_type as tgt_type, 
                   ec1.case_id as src_case, ec2.case_id as tgt_case
            FROM relationship_assertions a
            JOIN entities e1 ON a.source_entity_id = e1.entity_id
            JOIN entities e2 ON a.target_entity_id = e2.entity_id
            LEFT JOIN case_entities ec1 ON e1.entity_id = ec1.entity_id
            LEFT JOIN case_entities ec2 ON e2.entity_id = ec2.entity_id
        \"\"\")
        assertions = conn.execute(q).fetchall()
        
        for row in assertions:
            ast_id = row.assertion_id
            rel_type = row.relationship_type
            src_type = row.src_type
            tgt_type = row.tgt_type
            case_id = row.src_case or row.tgt_case or "UNKNOWN"
            
            baseline_status, baseline_reason = validate_legacy(src_type, rel_type, tgt_type)
            
            ont_src = ENTITY_TYPE_MAPPING.get(src_type, "netra:Entity")
            ont_tgt = ENTITY_TYPE_MAPPING.get(tgt_type, "netra:Entity")
            v1_status = "REJECTED"
            v1_reason = "UNKNOWN"
            
            if rel_type in RELATIONSHIP_TO_EVENT_MAPPING:
                ev = RELATIONSHIP_TO_EVENT_MAPPING[rel_type]
                res_src = validator.validate_event_role(ev['event'], ev['source_role'], ont_src)
                res_tgt = validator.validate_event_role(ev['event'], ev['target_role'], ont_tgt)
                if res_src.is_valid and res_tgt.is_valid:
                    v1_status = "CONFIRMED"
                    v1_reason = "VALID_EVENT_ROLES"
                else:
                    v1_reason = "; ".join(res_src.reasons + res_tgt.reasons)
            else:
                ont_rel = DIRECT_REL_MAPPING.get(rel_type)
                if not ont_rel:
                    v1_reason = "UNKNOWN_RELATIONSHIP"
                else:
                    res = validator.validate_direct_relationship(ont_src, ont_rel, ont_tgt)
                    if res.is_valid:
                        v1_status = "CONFIRMED"
                        v1_reason = "VALID_DIRECT_REL"
                    else:
                        v1_reason = "; ".join(res.reasons)
            
            deltas.append({
                "relationship": f"{src_type} -> {rel_type} -> {tgt_type}",
                "case_id": case_id,
                "baseline_status": baseline_status,
                "v1_status": v1_status,
                "reason_for_change": v1_reason if baseline_status != v1_status else "No change"
            })
            
            metrics[case_id]["baseline_assertions"] += 1
            metrics[case_id]["v1_assertions"] += 1
            
            if baseline_status == "CONFIRMED":
                metrics[case_id]["baseline_confirmed"] += 1
                metrics[case_id]["baseline_age_edges"] += 1
            else:
                metrics[case_id]["baseline_rejected"] += 1
                
            if v1_status == "CONFIRMED":
                metrics[case_id]["v1_confirmed"] += 1
                metrics[case_id]["v1_age_edges"] += 1
            else:
                metrics[case_id]["v1_rejected"] += 1
                
    with open(delta_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["relationship", "case_id", "baseline_status", "v1_status", "reason_for_change"])
        writer.writeheader()
        writer.writerows(deltas)
        
    with open(agg_csv, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["case_id", "baseline_entities", "v1_entities", "baseline_assertions", "v1_assertions", "baseline_confirmed", "v1_confirmed", "baseline_needs_review", "v1_needs_review", "baseline_rejected", "v1_rejected", "baseline_age_edges", "v1_age_edges", "provenance_complete_before", "provenance_complete_after", "cross_case_links_before", "cross_case_links_after"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for cid, m in metrics.items():
            row = {"case_id": cid}
            row.update(m)
            writer.writerow(row)
            
    print(f"Generated {delta_csv} and {agg_csv}")

if __name__ == "__main__":
    run_experiment()
"""
with open("/mnt/d/NETRA/SIH2026/ai-service/run_experiment.py", "w", encoding="utf-8") as f:
    f.write(content)
