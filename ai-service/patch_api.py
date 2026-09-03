import re

with open('app/api/graph.py', 'r') as f:
    code = f.read()

# Fix nodes query
code = code.replace(
    "MATCH p = (n {entity_id: '{safe_entity_id}'})-[*1..{depth}]-(m)",
    "MATCH p = (n {entity_id: '{safe_entity_id}'})-[*1..{depth}]-(m) WHERE ALL(rel IN relationships(p) WHERE rel.status = 'CONFIRMED')"
)

with open('app/api/graph.py', 'w') as f:
    f.write(code)
