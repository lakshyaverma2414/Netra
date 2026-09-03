import re

def normalize_text(text: str, entity_type: str) -> str:
    if not text:
        return ""
        
    t = text.strip().lower()
    
    if entity_type == "PHONE":
        # Keep only digits and '+'
        t = re.sub(r'[^\d+]', '', t)
        if len(t) == 10 and t.isdigit():
            t = "+91-" + t
        elif t.startswith("91") and len(t) == 12:
            t = "+91-" + t[2:]
        elif t.startswith("+91") and len(t) == 13:
            t = "+91-" + t[3:]
        # Convert any remaining simple digits if they didn't match the standard +91- pattern but had +91
        if t.startswith("+91") and "-" not in t:
            t = "+91-" + t[3:]
        return t
        
    if entity_type == "UPI" or entity_type == "EMAIL":
        return t
        
    if entity_type == "VEHICLE":
        # Remove spaces and hyphens, convert to uppercase
        t = re.sub(r'[\s\-]', '', t).upper()
        # To match canonical vehicles like RJ-14-XYZ, wait... 
        # The prompt says: RJ-14-XYZ, RJ14XYZ, RJ 14 XYZ should match without changing underlying.
        # It's better to normalize to the compact form RJ14XYZ for BOTH sides.
        return t
        
    if entity_type == "PERSON" or entity_type == "LOCATION" or entity_type == "ORGANIZATION":
        # Replace multiple spaces with single space
        t = re.sub(r'\s+', ' ', t)
        return t
        
    return t
