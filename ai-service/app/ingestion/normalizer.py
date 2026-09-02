import re

def normalize_phone(phone: str) -> str:
    if not phone:
        return phone
    # Keep digits and + only
    cleaned = re.sub(r'[^\d+]', '', phone)
    return cleaned

def normalize_vehicle(vehicle: str) -> str:
    if not vehicle:
        return vehicle
    # Remove whitespace and hyphens, convert to uppercase
    cleaned = re.sub(r'[\s\-]', '', vehicle).upper()
    return cleaned

def normalize_text(text: str) -> str:
    if not text:
        return text
    # Trim and normalize whitespace
    cleaned = re.sub(r'\s+', ' ', text).strip()
    return cleaned
