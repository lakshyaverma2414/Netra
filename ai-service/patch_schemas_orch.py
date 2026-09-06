import os
import sys

# 1. Update ValidationRequest in schemas
schema_path = "/mnt/d/NETRA/SIH2026/ai-service/app/schemas/validation.py"
with open(schema_path, "r") as f:
    schema_code = f.read()

if "assertion_id: Optional[str] = None" not in schema_code:
    schema_code = schema_code.replace("source_entity_id: str", "assertion_id: Optional[str] = None\n    source_entity_id: str")
    with open(schema_path, "w") as f:
        f.write(schema_code)

# 2. Update Orchestrator to pass assertion_id
orch_path = "/mnt/d/NETRA/SIH2026/ai-service/app/ingestion/core/orchestrator.py"
with open(orch_path, "r") as f:
    orch_code = f.read()

if "assertion_id=str(assertion.assertion_id)" not in orch_code:
    orch_code = orch_code.replace("val_req = ValidationRequest(", "val_req = ValidationRequest(\n                        assertion_id=str(assertion.assertion_id),")
    with open(orch_path, "w") as f:
        f.write(orch_code)
