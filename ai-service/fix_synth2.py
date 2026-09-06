import os

with open("/mnt/d/NETRA/SIH2026/ai-service/run_synthetic.py", "r") as f:
    code = f.read()

code = code.replace("e_alice = Entity(", "e_alice = Entity(canonical_name=\"Alice\", ")
code = code.replace("e_bob = Entity(", "e_bob = Entity(canonical_name=\"Bob\", ")
code = code.replace("e_w1 = Entity(", "e_w1 = Entity(canonical_name=\"W1_WALLET\", ")

with open("/mnt/d/NETRA/SIH2026/ai-service/run_synthetic.py", "w") as f:
    f.write(code)
