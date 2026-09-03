from pathlib import Path
from app.services.ingestion_service import process_file
from app.services.extractor_service import extract_entities

DATA_DIR = Path('d:/NETRA/SIH2026/ai-service/data/synthetic')
for f in (DATA_DIR / 'sources').glob('*'):
    if 'cdr' in f.name:
        recs = process_file(str(f), 'CDR')
        ments = extract_entities(recs)
        for m in ments:
            print(f"CDR MENTION: {m.text} | NORM: {m.normalized_value}")
