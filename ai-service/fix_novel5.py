import os

with open("/mnt/d/NETRA/SIH2026/ai-service/run_novel.py", "r") as f:
    code = f.read()

code = code.replace("metadata={}", "metadata={\"source_file\": \"test.txt\"}")

with open("/mnt/d/NETRA/SIH2026/ai-service/run_novel.py", "w") as f:
    f.write(code)
