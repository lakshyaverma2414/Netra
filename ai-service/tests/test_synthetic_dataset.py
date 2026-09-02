import json
import csv
import os
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path("d:/NETRA/SIH2026/ai-service/data/synthetic")
GROUND_TRUTH_DIR = DATA_DIR / "ground_truth"
SOURCES_DIR = DATA_DIR / "sources"

def test_synthetic_dataset_validity():
    # 1 & 2: Load entities and relationships
    with open(GROUND_TRUTH_DIR / "entities.json", "r", encoding="utf-8-sig") as f:
        entities = json.load(f)
    
    with open(GROUND_TRUTH_DIR / "relationships.json", "r", encoding="utf-8-sig") as f:
        relationships = json.load(f)

    # 5: Entity IDs unique
    entity_ids = [e["entity_id"] for e in entities]
    assert len(entity_ids) == len(set(entity_ids)), "Entity IDs are not unique"

    # 6: Relationship IDs unique
    rel_ids = [r["relationship_id"] for r in relationships]
    assert len(rel_ids) == len(set(rel_ids)), "Relationship IDs are not unique"

    # 3: Every relationship references an existing entity
    valid_entity_ids = set(entity_ids)
    for r in relationships:
        assert r["source_entity"] in valid_entity_ids, f"Unknown source {r['source_entity']}"
        assert r["target_entity"] in valid_entity_ids, f"Unknown target {r['target_entity']}"

    # 7: Source files not empty & extract evidence IDs
    source_evidence_ids = set()
    source_files = list(SOURCES_DIR.glob("*.*"))
    assert len(source_files) > 0, "No source files found"
    
    for sf in source_files:
        assert sf.stat().st_size > 0, f"Source file {sf.name} is empty"
        if sf.suffix == ".json":
            with open(sf, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
                for item in data:
                    if "evidence_id" in item:
                        source_evidence_ids.add(item["evidence_id"])
        elif sf.suffix == ".csv":
            with open(sf, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if "evidence_id" in row:
                        source_evidence_ids.add(row["evidence_id"])

    # 4: Every evidence ID referenced by relationships exists somewhere in the synthetic source data
    for r in relationships:
        for eid in r.get("evidence_ids", []):
            assert eid in source_evidence_ids, f"Evidence ID {eid} in rel {r['relationship_id']} missing from sources"

    # 8: The dataset contains at least one multi-hop path of length >= 3
    # Build adjacency list (undirected for path finding)
    adj = defaultdict(list)
    for r in relationships:
        adj[r["source_entity"]].append(r["target_entity"])
        adj[r["target_entity"]].append(r["source_entity"])
    
    def bfs_max_depth(start_node):
        visited = set([start_node])
        queue = [(start_node, 0)]
        max_d = 0
        while queue:
            curr, depth = queue.pop(0)
            if depth > max_d:
                max_d = depth
            for neighbor in adj[curr]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))
        return max_d

    max_path_length = 0
    for node in adj.keys():
        d = bfs_max_depth(node)
        if d > max_path_length:
            max_path_length = d
            
    assert max_path_length >= 3, f"Max path length is only {max_path_length}, expected >= 3"
