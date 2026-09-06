import yaml

path = "/mnt/d/NETRA/SIH2026/ai-service/ontology/assertions.yaml"
with open(path, 'r') as f:
    data = yaml.safe_load(f)

if "netra:AssertionStatus" in data:
    data["netra:AssertionStatus"]["label"] = "Assertion Status"
    
with open(path, 'w') as f:
    yaml.dump(data, f, sort_keys=False)
