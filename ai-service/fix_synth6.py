import os

with open("/mnt/d/NETRA/SIH2026/ai-service/run_synthetic.py", "r") as f:
    code = f.read()

code = code.replace("case_id = \"C-SYNTH-001\"", "case_id = f\"C-SYNTH-{uuid.uuid4().hex[:4]}\"")

with open("/mnt/d/NETRA/SIH2026/ai-service/run_synthetic.py", "w") as f:
    f.write(code)
