import os

path = "/mnt/d/NETRA/SIH2026/ai-service/update_gate.py"
with open(path, 'r') as f:
    content = f.read()

content = content.replace('node.parent or ""', 'getattr(node, "parent", None) or ""')

with open(path, 'w') as f:
    f.write(content)
