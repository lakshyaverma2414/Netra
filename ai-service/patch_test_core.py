import os

path = "/mnt/d/NETRA/SIH2026/ai-service/tests/ontology/test_ontology_core.py"
with open(path, 'r') as f:
    content = f.read()

content = content.replace('OntologyLoader("ontology")', 'OntologyLoader("ai-service/ontology")')

with open(path, 'w') as f:
    f.write(content)
