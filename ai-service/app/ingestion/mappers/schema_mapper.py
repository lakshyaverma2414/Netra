from typing import Dict, Any

class UnsupportedDatasetError(Exception):
    pass

class SchemaMapper:
    """
    Translates source-specific fields into NETRA Canonical structure.
    """
    MAPPINGS = {
        "NETRA-DEMO-CDR": {
            "caller_number": ("source_entity", "PHONE"),
            "receiver_number": ("target_entity", "PHONE"),
            "call_time": ("occurred_at", "DATETIME"),
            "duration": ("duration", "INT")
        },
        "NETRA-DEMO-TXN": {
            "sender_account": ("source_entity", "BANK_ACCOUNT"),
            "receiver_account": ("target_entity", "BANK_ACCOUNT"),
            "amount": ("amount", "FLOAT"),
            "timestamp": ("occurred_at", "DATETIME")
        },
        "NETRA-DEMO-VEHICLE": {
            "vehicle_number": ("source_entity", "VEHICLE"),
            "owner": ("target_entity", "PERSON")
        }
    }
    
    @classmethod
    def map_record(cls, dataset_id: str, raw_payload: Dict[str, Any]) -> Dict[str, Any]:
        mapping = cls.MAPPINGS.get(dataset_id)
        if not mapping:
            raise UnsupportedDatasetError(f"UNSUPPORTED_DATASET_TYPE: Dataset '{dataset_id}' has no defined canonical mapping.")
            
        normalized = {}
        for source_field, (canonical_key, data_type) in mapping.items():
            if source_field in raw_payload:
                val = raw_payload[source_field]
                # Light casting
                if data_type == "INT":
                    try: val = int(val)
                    except: pass
                elif data_type == "FLOAT":
                    try: val = float(val)
                    except: pass
                normalized[canonical_key] = val
        return normalized
