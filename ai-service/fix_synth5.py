import os

with open("/mnt/d/NETRA/SIH2026/ai-service/run_synthetic.py", "r") as f:
    code = f.read()

if "from sqlalchemy import create_engine, text" not in code:
    code = code.replace("from sqlalchemy import create_engine", "from sqlalchemy import create_engine, text")

with open("/mnt/d/NETRA/SIH2026/ai-service/run_synthetic.py", "w") as f:
    f.write(code)
