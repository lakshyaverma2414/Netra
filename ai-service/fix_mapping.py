import os
import json

mapping_path = "/mnt/d/NETRA/SIH2026/ai-service/app/ontology/mapping.py"
with open(mapping_path, "r") as f:
    content = f.read()

# Make mappings strictly semantic
content = content.replace('"ASSOCIATED_WITH": "netra:AFFILIATED_WITH",', '# "ASSOCIATED_WITH": "netra:AFFILIATED_WITH", # Removed: Not semantically equivalent')
content = content.replace('"LINKED_TO": "netra:USED_BY",', '# "LINKED_TO": "netra:USED_BY", # Removed: Too broad')
content = content.replace('"INVOLVED_IN": "netra:PARTICIPATED_IN",', '# "INVOLVED_IN": "netra:PARTICIPATED_IN", # Removed: Requires strict event structure')

with open(mapping_path, "w") as f:
    f.write(content)

