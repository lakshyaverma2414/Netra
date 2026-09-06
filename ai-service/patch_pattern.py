import os
import yaml

pattern_dir = "/mnt/d/NETRA/SIH2026/ai-service/app/analytics/patterns"

with open(os.path.join(pattern_dir, "financial_convergence.yaml"), "r") as f:
    doc = yaml.safe_load(f)

doc["pattern"]["query_template"] = """
    SELECT ee_target.entity_id as focal_entity, COUNT(DISTINCT ee_source.entity_id) as incoming_count
    FROM events e
    JOIN event_entities ee_target ON e.event_id = ee_target.event_id AND ee_target.role = 'beneficiary'
    JOIN event_entities ee_source ON e.event_id = ee_source.event_id AND ee_source.role = 'originator'
    WHERE e.event_type = 'netra:FinancialTransaction'
    GROUP BY ee_target.entity_id
    HAVING COUNT(DISTINCT ee_source.entity_id) >= :minimum_sources
"""

with open(os.path.join(pattern_dir, "financial_convergence.yaml"), "w") as f:
    yaml.dump(doc, f)
