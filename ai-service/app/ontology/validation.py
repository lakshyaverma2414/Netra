from .registry import OntologyRegistry
from .models import ValidationResult

class OntologyValidator:
    def __init__(self, registry: OntologyRegistry):
        self.registry = registry

    def validate_direct_relationship(self, source_type: str, rel_type: str, target_type: str) -> ValidationResult:
        rel = self.registry.relationships.get(rel_type)
        if not rel:
            return ValidationResult(is_valid=False, reasons=[f"Relationship '{rel_type}' is not defined."])
        if not rel.direct:
            return ValidationResult(is_valid=False, reasons=[f"Relationship '{rel_type}' is not a direct relationship."])

        domain_valid = any(self.registry.is_subclass(source_type, d) for d in rel.domain)
        if not domain_valid:
            return ValidationResult(is_valid=False, reasons=[f"Source type '{source_type}' invalid for '{rel_type}'. Allowed: {rel.domain}"])

        range_valid = any(self.registry.is_subclass(target_type, r) for r in rel.range)
        if not range_valid:
            return ValidationResult(is_valid=False, reasons=[f"Target type '{target_type}' invalid for '{rel_type}'. Allowed: {rel.range}"])

        return ValidationResult(is_valid=True, reasons=[])

    def validate_event_role(self, event_type: str, role_name: str, entity_type: str) -> ValidationResult:
        event = self.registry.events.get(event_type)
        if not event:
            return ValidationResult(is_valid=False, reasons=[f"Event '{event_type}' is not defined."])
        if role_name not in event.roles:
            return ValidationResult(is_valid=False, reasons=[f"Role '{role_name}' is not defined for event '{event_type}'."])

        role_def = event.roles[role_name]
        role_valid = any(self.registry.is_subclass(entity_type, t) for t in role_def.allowed_types)
        if not role_valid:
            return ValidationResult(is_valid=False, reasons=[f"Entity '{entity_type}' cannot play role '{role_name}'. Allowed: {role_def.allowed_types}"])

        return ValidationResult(is_valid=True, reasons=[])

class OntologySelfValidator:
    def __init__(self, registry: OntologyRegistry):
        self.registry = registry

    def run_full_audit(self) -> ValidationResult:
        reasons = []

        for space in (self.registry.entities, self.registry.events, self.registry.relationships, self.registry.contexts, self.registry.provenance, self.registry.assertions):
            for k, node in space.items():
                if node.description is None or node.description.strip() == "":
                    reasons.append(f"Missing description for {k}")
                if getattr(node, "parent", None):
                    if not self.registry.get_node(node.parent):
                        reasons.append(f"Unknown parent '{node.parent}' for '{k}'")

        for k, rel in self.registry.relationships.items():
            for d in rel.domain:
                if not self.registry.get_node(d):
                    reasons.append(f"Unknown domain '{d}' in relationship '{k}'")
            for r in rel.range:
                if not self.registry.get_node(r):
                    reasons.append(f"Unknown range '{r}' in relationship '{k}'")
            if rel.inverse:
                inv_rel = self.registry.relationships.get(rel.inverse)
                if not inv_rel:
                    reasons.append(f"Unknown inverse '{rel.inverse}' in relationship '{k}'")
                elif inv_rel.inverse and inv_rel.inverse != k:
                    reasons.append(f"Inverse mismatch between '{k}' and '{rel.inverse}'")
            if rel.symmetric and rel.inverse:
                reasons.append(f"Relationship '{k}' cannot be both symmetric and have an explicit inverse.")

        for k, event in self.registry.events.items():
            for role_name, role_def in event.roles.items():
                for t in role_def.allowed_types:
                    if not self.registry.get_node(t):
                        reasons.append(f"Unknown allowed_type '{t}' in event '{k}' role '{role_name}'")

        return ValidationResult(is_valid=len(reasons)==0, reasons=reasons)
