import os

test_path = "/mnt/d/NETRA/SIH2026/ai-service/tests/ontology/test_runtime_integration.py"
with open(test_path, "r", encoding="utf-8") as f:
    code = f.read()

# Add dummy evidence_ids to ensure tests return CONFIRMED
code = code.replace(
    'source_record_id="REC1", extracted_text="test", extraction_method="QWEN", case_id="C1"',
    'source_record_id="REC1", extracted_text="test", extraction_method="QWEN", case_id="C1", evidence_ids=["EVID1"]'
)

with open(test_path, "w", encoding="utf-8") as f:
    f.write(code)

