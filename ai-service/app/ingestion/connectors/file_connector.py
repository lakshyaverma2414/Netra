import csv
import json
import logging
import uuid
from typing import Generator, Dict, Any
from app.ingestion.connectors.base_connector import BaseConnector

logger = logging.getLogger(__name__)

class FileConnector(BaseConnector):
    def __init__(self, file_path: str, file_type: str):
        self.file_path = file_path
        self.file_type = file_type.upper()
        
    def connect(self) -> bool:
        import os
        return os.path.exists(self.file_path)
        
    def fetch(self) -> Generator[Dict[str, Any], None, None]:
        if self.file_type == 'CSV':
            with open(self.file_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    yield dict(row)
        elif self.file_type == 'JSON':
            with open(self.file_path, mode='r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        yield item
                else:
                    yield data
        elif self.file_type == 'JSONL':
            with open(self.file_path, mode='r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        yield json.loads(line)
        else:
            logger.warning(f"FileConnector fetching unstructured file logic (e.g. {self.file_type}) typically returns a single artifact record.")
            # For PDF/Images, we yield a single 'record' representing the file metadata to initiate the unstructured pipeline
            yield {
                "file_path": self.file_path,
                "file_type": self.file_type,
                "is_unstructured": True
            }
