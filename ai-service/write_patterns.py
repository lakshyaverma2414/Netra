import os
import yaml

pattern_dir = "/mnt/d/NETRA/SIH2026/ai-service/app/analytics/patterns"
os.makedirs(pattern_dir, exist_ok=True)

conv = {
    "pattern": {
        "id": "financial_convergence",
        "description": "Identify entities receiving funds from multiple distinct originators.",
        "parameters": {
            "minimum_sources": 2
        },
        "query_template": """
            SELECT r2.target_entity_id as focal_entity, COUNT(DISTINCT r1.source_entity_id) as incoming_count
            FROM relationships r1
            JOIN relationships r2 ON r1.relationship_id = r2.relationship_id -- Mock proxy for event join
            WHERE r1.relationship_type = 'TRANSFERRED_TO'
            GROUP BY r2.target_entity_id
            HAVING COUNT(DISTINCT r1.source_entity_id) >= :minimum_sources
        """
    }
}
with open(os.path.join(pattern_dir, "financial_convergence.yaml"), "w") as f:
    yaml.dump(conv, f)

bridge = {
    "pattern": {
        "id": "cross_case_bridge",
        "description": "Identify entities that connect otherwise separate cases.",
        "parameters": {
            "minimum_cases": 2
        },
        "query_template": """
            SELECT entity_id, COUNT(DISTINCT case_id) as case_count
            FROM case_entities
            GROUP BY entity_id
            HAVING COUNT(DISTINCT case_id) >= :minimum_cases
        """
    }
}
with open(os.path.join(pattern_dir, "cross_case_bridge.yaml"), "w") as f:
    yaml.dump(bridge, f)
