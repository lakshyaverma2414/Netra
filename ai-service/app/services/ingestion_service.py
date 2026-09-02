import os
from typing import List
from app.schemas.ingestion import NormalizedRecord
from app.ingestion.csv_loader import load_cdr, load_transaction
from app.ingestion.json_loader import load_fir, load_surveillance

def process_file(filepath: str, source_type: str, case_id: str = None) -> List[NormalizedRecord]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File {filepath} not found")

    st = source_type.upper()
    if st == "FIR":
        return load_fir(filepath, case_id)
    elif st == "CDR":
        return load_cdr(filepath, case_id)
    elif st == "TRANSACTION":
        return load_transaction(filepath, case_id)
    elif st == "SURVEILLANCE":
        return load_surveillance(filepath, case_id)
    else:
        raise ValueError(f"Unsupported source type: {source_type}")
