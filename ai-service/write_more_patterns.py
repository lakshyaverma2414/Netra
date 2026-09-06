import os
import yaml

pattern_dir = "/mnt/d/NETRA/SIH2026/ai-service/app/analytics/patterns"

patterns = {
    "shared_identifier": {
        "pattern": {
            "id": "shared_identifier",
            "description": "Entities sharing a common identifier (phone, email, etc).",
            "parameters": {"minimum_entities": 2},
            "query_template": """
                SELECT r1.target_entity_id as identifier, COUNT(DISTINCT r1.source_entity_id) as entity_count
                FROM relationships r1
                WHERE r1.relationship_type = 'USES'
                GROUP BY r1.target_entity_id
                HAVING COUNT(DISTINCT r1.source_entity_id) >= :minimum_entities
            """
        }
    },
    "communication_concentration": {
        "pattern": {
            "id": "communication_concentration",
            "description": "Identify entities that have communication from multiple distinct sources.",
            "parameters": {"minimum_sources": 3},
            "query_template": """
                SELECT target_entity_id as focal_entity, COUNT(DISTINCT source_entity_id) as incoming_count
                FROM relationships
                WHERE relationship_type = 'COMMUNICATES_WITH'
                GROUP BY target_entity_id
                HAVING COUNT(DISTINCT source_entity_id) >= :minimum_sources
            """
        }
    },
    "multi_hop_linkage": {
        "pattern": {
            "id": "multi_hop_linkage",
            "description": "Find entities linked indirectly across multiple relationships.",
            "parameters": {},
            "query_template": """
                SELECT r1.source_entity_id as start_node, r2.target_entity_id as end_node
                FROM relationships r1
                JOIN relationships r2 ON r1.target_entity_id = r2.source_entity_id
                WHERE r1.source_entity_id != r2.target_entity_id
            """
        }
    },
    "temporal_correlation": {
        "pattern": {
            "id": "temporal_correlation",
            "description": "Find relationships occurring within a tight time window.",
            "parameters": {},
            "query_template": """
                SELECT r1.relationship_id as rel1, r2.relationship_id as rel2
                FROM relationships r1
                JOIN relationships r2 ON r1.target_entity_id = r2.target_entity_id
                WHERE r1.relationship_id != r2.relationship_id 
                /* Mocking temporal overlap for now */
            """
        }
    }
}

for pid, pdata in patterns.items():
    with open(os.path.join(pattern_dir, f"{pid}.yaml"), "w") as f:
        yaml.dump(pdata, f)
