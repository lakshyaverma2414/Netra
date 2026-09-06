# Evidence and Provenance Model

## Concept
Following NIST's CASE-Corpora and W3C PROV-O, NETRA must distinguish between a physical/digital artifact (Evidence) and the extraction of intelligence from it (Observation -> Assertion).

## The Provenance Chain
1.  **SourceRecord (Trace/Artifact)**: The physical phone, the hard drive, or the FIR document.
2.  **DerivedArtifact**: A forensic image, a PDF translation, or an OCR output.
3.  **Observation**: The LLM parsing a specific sentence.
4.  **Assertion**: The claim that "Person A OWNS Vehicle B".
5.  **Canonical Relationship**: The accepted fact in the KG.

## Attributes Required
Every Assertion must carry:
*   `extraction_method` (e.g., Qwen-72B, Manual Entry)
*   `confidence` (Extraction heuristic score)
*   `observation_id` (Link to the raw text snippet)
*   `source_record_id` (Link to the root Evidence)
