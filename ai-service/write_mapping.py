import os

mapping_code = """
ENTITY_TYPE_MAPPING = {
    "PERSON": "netra:Person",
    "PHONE": "netra:Identifier",
    "IMEI": "netra:Identifier",
    "VEHICLE": "netra:Vehicle",
    "LOCATION": "netra:Location",
    "ORGANIZATION": "netra:Organization",
    "EVENT": "netra:Event",
    "BANK_ACCOUNT": "netra:Account",
    "UPI_ID": "netra:Account",
    "SOCIAL_ACCOUNT": "netra:Account",
    "CASE": "netra:Case"
}

RELATIONSHIP_TO_EVENT_MAPPING = {
    "TRANSFERRED_TO": {
        "event": "netra:FinancialTransaction",
        "source_role": "originator",
        "target_role": "beneficiary"
    }
}

DIRECT_REL_MAPPING = {
    "USES": "netra:USES",
    "OWNS": "netra:OWNS",
    "COMMUNICATES_WITH": "netra:COMMUNICATES_WITH",
    "LOCATED_AT": "netra:LOCATED_AT",
    "ASSOCIATED_WITH": "netra:AFFILIATED_WITH",
    "LINKED_TO": "netra:USED_BY",
    "INVOLVED_IN": "netra:PARTICIPATED_IN",
    "SAME_AS": "netra:SAME_AS",
    "ALIAS_OF": "netra:ALIAS_OF"
}
"""
path = "/mnt/d/NETRA/SIH2026/ai-service/app/ontology/mapping.py"
with open(path, "w", encoding="utf-8") as f:
    f.write(mapping_code.strip())
