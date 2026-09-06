import yaml
import os
from .models import (
    OntologyEntity, OntologyEvent, OntologyRelationship, 
    OntologyContext, OntologyProvenance, OntologyAssertionDef
)

class OntologyLoader:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.manifest = self._load_yaml('ontology_manifest.yaml')

    def _load_yaml(self, filename: str) -> dict:
        path = os.path.join(self.base_dir, filename)
        if not os.path.exists(path):
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    def load_entities(self):
        data = self._load_yaml('entities.yaml')
        return [OntologyEntity(id=k, **v) for k, v in data.items()]

    def load_events(self):
        data = self._load_yaml('events.yaml')
        return [OntologyEvent(id=k, **v) for k, v in data.items()]

    def load_relationships(self):
        data = self._load_yaml('relationships.yaml')
        return [OntologyRelationship(id=k, **v) for k, v in data.items()]

    def load_contexts(self):
        data = self._load_yaml('contexts.yaml')
        return [OntologyContext(id=k, **v) for k, v in data.items()]

    def load_provenance(self):
        data = self._load_yaml('provenance.yaml')
        return [OntologyProvenance(id=k, **v) for k, v in data.items()]

    def load_assertions(self):
        data = self._load_yaml('assertions.yaml')
        return [OntologyAssertionDef(id=k, **v) for k, v in data.items()]
