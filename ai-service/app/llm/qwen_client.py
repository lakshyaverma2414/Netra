import os
import json
import logging
import httpx
from typing import Optional
from app.schemas.llm_relationship import LLMRelationshipResponse

logger = logging.getLogger(__name__)

QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "http://127.0.0.1:8081")
QWEN_TIMEOUT_SECONDS = int(os.getenv("QWEN_TIMEOUT_SECONDS", "120"))
QWEN_MAX_TOKENS = int(os.getenv("QWEN_MAX_TOKENS", "1024"))

PROMPT_TEMPLATE = """You are a relationship extraction system.
Extract relationships explicitly supported by the supplied text.

Allowed relationship types:
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
- Use only the allowed relationship types.
- Every relationship must have supporting evidence_text.
- Detect explicit negation (negated: true).
- Preserve temporal and location context when present.
- Identify the entity type (e.g. PERSON, PHONE, VEHICLE, LOCATION, ORGANIZATION) for source and target.
- Return ONLY valid JSON matching this schema:
{{
  "relationships": [
    {{
      "source_text": "text span",
      "source_type": "PERSON",
      "relationship_type": "USES",
      "target_text": "text span",
      "target_type": "PHONE",
      "evidence_text": "exact sentence proving this",
      "negated": false,
      "temporal_context": {{"date": "YYYY-MM-DD"}},
      "location_context": "location text"
    }}
  ]
}}
If no relationships are found, return {{"relationships": []}}.

Text:
{text}
"""

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
            
            content = content.strip()
            if content.startswith("`json"):
                content = content[7:]
            if content.startswith("`"):
                content = content[3:]
            if content.endswith("`"):
                content = content[:-3]
                
            parsed = json.loads(content)
            return LLMRelationshipResponse(**parsed)
            
    except json.JSONDecodeError as e:
        logger.error(f"Qwen returned invalid JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"Qwen extraction failed: {e}")
        return None
