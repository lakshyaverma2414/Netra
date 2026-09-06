import os
import re
import json
import logging
import httpx
from typing import Optional
from app.schemas.llm_relationship import LLMRelationshipResponse

logger = logging.getLogger(__name__)

QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "http://127.0.0.1:8081")
QWEN_TIMEOUT_SECONDS = int(os.getenv("QWEN_TIMEOUT_SECONDS", "120"))
QWEN_MAX_TOKENS = int(os.getenv("QWEN_MAX_TOKENS", "4096"))

PROMPT_TEMPLATE = """You are a criminal intelligence relationship extraction system.
Extract ALL relationships explicitly supported by the supplied text.

Rules:
- Extract precise, generic semantic relationships (e.g., TRANSFERRED_TO, EMPLOYED_BY, AFFILIATED_WITH, COMMUNICATES_WITH, LOCATED_AT, OWNS, CONSPIRED_WITH, PARTICIPATED_IN, USED_BY).
- Do not invent entities or relationships not present in the text.
- Describe the relationship precisely based on the evidence.
- Identify the entity type (PERSON, PHONE, VEHICLE, LOCATION, ORGANIZATION, BANK_ACCOUNT, EVENT, CASE) for source and target.
- Every relationship must have supporting evidence_text (an exact or paraphrased sentence from the text).
- Detect explicit negation (negated: true).
- Preserve temporal and location context when present.
- Return ONLY valid JSON matching this schema:
{{
  "relationships": [
    {{
      "source_text": "text span",
      "source_type": "PERSON",
      "relationship_type": "AFFILIATED_WITH",
      "target_text": "text span",
      "target_type": "ORGANIZATION",
      "evidence_text": "exact sentence proving this",
      "negated": false,
      "temporal_context": {{}},
      "location_context": ""
    }}
  ]
}}
If no relationships are found, return {{"relationships": []}}.

Text:
{text}
"""


def _repair_truncated_json(content: str) -> Optional[dict]:
    """
    If Qwen's output was token-truncated mid-JSON, attempt to salvage
    all fully-formed relationship objects before the cut point.
    """
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Strategy: find all complete {...} objects inside the relationships array
    # by scanning for complete JSON objects between array boundaries
    try:
        # Extract whatever is between "relationships": [ ... ]
        m = re.search(r'"relationships"\s*:\s*\[', content)
        if not m:
            return None

        array_start = m.end()
        array_content = content[array_start:]

        # Collect complete objects
        complete_rels = []
        depth = 0
        obj_start = None

        for i, ch in enumerate(array_content):
            if ch == '{':
                if depth == 0:
                    obj_start = i
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0 and obj_start is not None:
                    obj_str = array_content[obj_start:i+1]
                    try:
                        obj = json.loads(obj_str)
                        complete_rels.append(obj)
                    except json.JSONDecodeError:
                        pass
                    obj_start = None

        if complete_rels:
            logger.warning(
                f"Qwen JSON was truncated — salvaged {len(complete_rels)} complete relationships from partial response."
            )
            return {"relationships": complete_rels}

    except Exception as e:
        logger.error(f"JSON repair failed: {e}")

    return None


def extract_relationships_with_qwen(text: str) -> Optional[LLMRelationshipResponse]:
    prompt = PROMPT_TEMPLATE.format(text=text)

    payload = {
        "messages": [
            {"role": "system", "content": "You are a precise JSON-only relationship extraction assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0,
        "max_tokens": QWEN_MAX_TOKENS,
        "response_format": {"type": "json_object"}
    }

    try:
        with httpx.Client(timeout=QWEN_TIMEOUT_SECONDS) as client:
            response = client.post(f"{QWEN_BASE_URL}/v1/chat/completions", json=payload)
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            # Strip markdown code fences if present
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # Try to parse — fall back to repair if truncated
            parsed = _repair_truncated_json(content)
            if parsed is None:
                logger.error("Qwen returned unparseable JSON even after repair attempt.")
                return None

            return LLMRelationshipResponse(**parsed)

    except Exception as e:
        logger.error(f"Qwen extraction failed: {e}")
        return None
