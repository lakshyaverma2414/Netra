import sys
sys.path.insert(0, "/mnt/d/NETRA/SIH2026/ai-service")

from app.llm.qwen_client import extract_relationships_with_qwen

with open("/mnt/d/sahaay/NETRA_10_CASE_EVIDENCE_CORPUS_multimedia_v2/NETRA_10_CASE_EVIDENCE_CORPUS_FINAL/C-001/C-001_1993_Bombay_Bomb_Blast.txt", "r", encoding="utf-8") as f:
    text = f.read()

print(f"Text length: {len(text)} chars")
print(f"First 500 chars:\n{text[:500]}\n")

# Send to Qwen
resp = extract_relationships_with_qwen(text)
if resp:
    print(f"Qwen returned {len(resp.relationships)} relationships")
    for r in resp.relationships[:5]:
        print(f"  {r.source_text} --[{r.relationship_type}]--> {r.target_text}")
else:
    print("Qwen returned None / empty")
