import os

filepath = "/mnt/d/NETRA/SIH2026/ai-service/app/llm/qwen_client.py"
with open(filepath, "r") as f:
    code = f.read()

# Replace hardcoded prompt
old_prompt = """Allowed relationship types:
USES
OWNS
COMMUNICATES_WITH
TRANSFERRED_TO
ASSOCIATED_WITH
LOCATED_AT
LINKED_TO
INVOLVED_IN

Rules:
- Do not invent entities.
- Do not invent relationships.
- Do not infer ownership from usage.
- Use only the allowed relationship types."""

new_prompt = """Rules:
- Extract precise, generic semantic relationships (e.g., TRANSFERRED_TO, EMPLOYED_BY, AFFILIATED_WITH, COMMUNICATES_WITH, LOCATED_AT, OWNS).
- Do not invent entities.
- Describe the relationship precisely based on the evidence.
- Do not infer ownership from usage.
- You are not restricted to a fixed list, but aim for clean semantic ontology concepts."""

code = code.replace(old_prompt, new_prompt)

with open(filepath, "w") as f:
    f.write(code)
