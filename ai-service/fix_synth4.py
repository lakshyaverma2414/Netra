import os
import uuid

with open("/mnt/d/NETRA/SIH2026/ai-service/run_synthetic.py", "r") as f:
    code = f.read()

code = code.replace("batch_id=\"B-001\",", "")

with open("/mnt/d/NETRA/SIH2026/ai-service/run_synthetic.py", "w") as f:
    f.write(code)
