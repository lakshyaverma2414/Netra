import os

with open("/mnt/d/NETRA/SIH2026/ai-service/run_synthetic.py", "r") as f:
    code = f.read()

code = code.replace("canonical_name=\"Alice\",", "canonical_name=\"Alice\", normalized_value=\"alice\",")
code = code.replace("canonical_name=\"Bob\",", "canonical_name=\"Bob\", normalized_value=\"bob\",")
code = code.replace("canonical_name=\"W1_WALLET\",", "canonical_name=\"W1_WALLET\", normalized_value=\"w1_wallet\",")

with open("/mnt/d/NETRA/SIH2026/ai-service/run_synthetic.py", "w") as f:
    f.write(code)
