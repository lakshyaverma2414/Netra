import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

def validate_record(dataset_id: str, normalized_payload: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validates data quality constraints. 
    Returns (is_valid, error_message).
    """
    if "DEMO-CDR" in dataset_id:
        if not normalized_payload.get("source_entity") or not normalized_payload.get("target_entity"):
            return False, "Missing source or target phone number"
    elif "DEMO-TXN" in dataset_id:
        amt = normalized_payload.get("amount")
        if amt is None:
            return False, "Missing transaction amount"
        if isinstance(amt, (int, float)) and amt < 0:
            return False, "Negative transaction amount"
            
    # Generic validation passes
    return True, ""
