import os

with open("/mnt/d/NETRA/SIH2026/ai-service/run_novel.py", "r") as f:
    code = f.read()

code = code.replace("start_char=0, end_char=", "extraction_method=\"QWEN_NER\", start_char=0, end_char=")

with open("/mnt/d/NETRA/SIH2026/ai-service/run_novel.py", "w") as f:
    f.write(code)
