from typing import Optional
from .models import OntologyNode

class OntologyRegistry:
    def __init__(self, loader):
        self.version = loader.manifest.get("version", "1.0.0")
        self.entities = {e.id: e for e in loader.load_entities()}
        self.events = {e.id: e for e in loader.load_events()}
        self.relationships = {r.id: r for r in loader.load_relationships()}
        self.contexts = {c.id: c for c in loader.load_contexts()}
        self.provenance = {p.id: p for p in loader.load_provenance()}
        self.assertions = {a.id: a for a in loader.load_assertions()}

    def get_node(self, node_id: str) -> Optional[OntologyNode]:
        for space in (self.entities, self.events, self.relationships, self.contexts, self.provenance, self.assertions):
            if node_id in space:
                return space[node_id]
        return None

    def is_subclass(self, child_id: str, parent_id: str) -> bool:
        if child_id == parent_id:
            return True
        node = self.get_node(child_id)
        visited = set()
        while node and node.parent:
            if node.id in visited:
                break # Circular prevention in traversal
            visited.add(node.id)
            if node.parent == parent_id:
                return True
            node = self.get_node(node.parent)
        return False
