import os

with open("/mnt/d/NETRA/SIH2026/ai-service/run_synthetic.py", "r") as f:
    code = f.read()

code = code.replace("case_number=\"SYNTH-26\"", "case_number=f\"SYNTH-{uuid.uuid4().hex[:6]}\"")

with open("/mnt/d/NETRA/SIH2026/ai-service/run_synthetic.py", "w") as f:
    f.write(code)
