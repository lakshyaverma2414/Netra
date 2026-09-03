import json

graph = []

# C-001 (Operation Black Web)
nodes_c1 = [
    {"id": "P-001", "label": "Aryan", "type": "person", "riskScore": 80, "riskLevel": "High", "caseId": "C-001"},
    {"id": "PH-001", "label": "+91-9876543210", "type": "phone", "riskScore": 60, "riskLevel": "Medium", "caseId": "C-001"},
    {"id": "LOC-001", "label": "Sector 12 Warehouse", "type": "location", "riskScore": 40, "riskLevel": "Low", "caseId": "C-001"},
    {"id": "PH-002", "label": "+91-9999988888", "type": "phone", "riskScore": 90, "riskLevel": "Critical", "caseId": "C-001"},
]
edges_c1 = [
    {"source": "P-001", "target": "PH-001", "label": "USES", "caseId": "C-001"},
    {"source": "P-001", "target": "LOC-001", "label": "LOCATED_AT", "caseId": "C-001"},
    {"source": "PH-001", "target": "PH-002", "label": "COMMUNICATES_WITH", "caseId": "C-001"},
]

# C-002 (Syndicate Ghost)
nodes_c2 = [
    {"id": "P-002", "label": "Vikram Singh", "type": "person", "riskScore": 95, "riskLevel": "Critical", "caseId": "C-002"},
    {"id": "PH-002-C2", "label": "+91-9999988888", "type": "phone", "riskScore": 90, "riskLevel": "Critical", "caseId": "C-002"}, # same entity, duplicated for case isolation if needed, or wait, if we filter by caseId, we need them to be in the array with multiple caseIds? Wait, filtering by `el.data('caseId') === caseId` means one node per case. Let's just create nodes with matching IDs. Cytoscape merges nodes with the same ID! So if we just output them, we should ensure we tag caseIds properly. Or we can just use the unified graph and the frontend filters edges and nodes.
]
