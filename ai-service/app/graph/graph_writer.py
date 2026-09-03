import logging
from typing import List, Dict, Any
from abc import ABC, abstractmethod

from app.schemas.validation import RelationshipValidationResult, ValidationStatus
from app.schemas.resolution import CanonicalEntity

logger = logging.getLogger(__name__)

class GraphWriter(ABC):
    @abstractmethod
    def connect(self):
        pass
        
    @abstractmethod
    def disconnect(self):
        pass
        
    @abstractmethod
    def write_entities(self, entities: List[CanonicalEntity]) -> int:
        pass

    @abstractmethod
    def write_relationships(self, validation_results: List[RelationshipValidationResult]) -> int:
        pass

class MockGraphWriter(GraphWriter):
    def __init__(self, connection_string: str = None):
        self.is_connected = False
        
    def connect(self):
        self.is_connected = True
        
    def disconnect(self):
        self.is_connected = False
        
    def write_entities(self, entities: List[CanonicalEntity]) -> int:
        if not self.is_connected:
            raise RuntimeError("Not connected")
        written = 0
        for ent in entities:
            if ent.resolution_status in ["CONFIRMED", "PROBABLE"]:
                written += 1
        return written

    def write_relationships(self, validation_results: List[RelationshipValidationResult]) -> int:
        if not self.is_connected:
            raise RuntimeError("Not connected")
        written = 0
        for res in validation_results:
            if res.status == ValidationStatus.CONFIRMED:
                written += 1
        return written
