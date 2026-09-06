import os

with open("/mnt/d/NETRA/SIH2026/ai-service/run_novel.py", "r") as f:
    code = f.read()

code = code.replace('"DEVICE"', '"PHONE"').replace('"Server"', '"Phone"').replace('"server"', '"phone"').replace('A server located', 'A phone located')

with open("/mnt/d/NETRA/SIH2026/ai-service/run_novel.py", "w") as f:
    f.write(code)
