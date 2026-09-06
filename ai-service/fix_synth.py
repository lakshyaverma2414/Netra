import os

with open("/mnt/d/NETRA/SIH2026/ai-service/run_synthetic.py", "r") as f:
    code = f.read()

code = code.replace("source_record_id=f\"REC-{uuid.uuid4().hex[:8]}\",", "record_id=f\"REC-{uuid.uuid4().hex[:8]}\",")
code = code.replace("record_type=\"DOCUMENT\",", "")
code = code.replace("title=\"Blockchain Ledger Analysis\",", "")
code = code.replace("content=\"Alice and Bob transferred funds to wallet W1.\"", "raw_payload={\"content\": \"Alice and Bob transferred funds to wallet W1.\"}, batch_id=\"B-001\", source_type=\"DOCUMENT\"")
code = code.replace("source_record_id=rec1.source_record_id", "source_record_id=rec1.record_id")
code = code.replace("evidence_ids=[rec1.source_record_id]", "evidence_ids=[rec1.record_id]")
code = code.replace("extracted_text=rec1.content", "extracted_text=\"Alice and Bob transferred funds to wallet W1.\"")

with open("/mnt/d/NETRA/SIH2026/ai-service/run_synthetic.py", "w") as f:
    f.write(code)
