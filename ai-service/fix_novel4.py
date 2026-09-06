import os

with open("/mnt/d/NETRA/SIH2026/ai-service/run_novel.py", "r") as f:
    code = f.read()

code = code.replace("data={\"evidence_id\": rec_id}", "data={\"evidence_id\": rec_id}, source_type=\"DOCUMENT\", metadata={}")

with open("/mnt/d/NETRA/SIH2026/ai-service/run_novel.py", "w") as f:
    f.write(code)
