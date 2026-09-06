# Uncertainty Model

## The Danger of "Confidence"
A heuristic score from an LLM (e.g., 0.91) is NOT a probability (91% chance this is true). It is a similarity or confidence-of-extraction metric.

## Semantic Dimensions of Uncertainty
NETRA must track three distinct axes:
1.  **Extraction Confidence (Heuristic)**: How confident is the tool (Qwen/Spacy) that it correctly parsed the sentence?
2.  **Source Reliability (Belief)**: How trustworthy is the source? (e.g., verified CDR vs anonymous tip).
3.  **Validation Status (Workflow)**: 
    *   `CANDIDATE`: Extracted, pending review.
    *   `CONFIRMED`: Validated mathematically or manually.
    *   `CONTRADICTED`: Conflicting evidence exists.
    *   `REJECTED`: Proven false.
