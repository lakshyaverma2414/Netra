import os

BASE_DIR = "/mnt/d/NETRA/SIH2026/ai-service/tests/ontology"
target_dir = "ai-service/ontology"

def patch_test(name):
    path = os.path.join(BASE_DIR, name)
    with open(path, 'r') as f:
        content = f.read()
    
    content = content.replace('OntologyLoader("ontology")', 'OntologyLoader("ai-service/ontology")')
    
    with open(path, 'w') as f:
        f.write(content)

patch_test("test_ontology_entities.py")
patch_test("test_ontology_events.py")
patch_test("test_ontology_identity.py")
patch_test("test_ontology_relationships.py")

