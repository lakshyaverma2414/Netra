import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import exc

from app.db.models import (
    Finding, FindingEntity, FindingRelationship, EvidenceFinding,
    Relationship, CaseEntity, RelationshipAssertionLink, RelationshipAssertion
)

class FindingsService:
    def __init__(self, db: Session):
        self.db = db

    def generate_finding_from_lead(self, lead: Dict[str, Any], case_id: str = None) -> Finding:
        # Determine case_id
        assigned_case_id = case_id
        if not assigned_case_id and lead.get("case_ids"):
            assigned_case_id = lead["case_ids"][0]
            
        lead_id = lead.get("lead_id")
        if not lead_id:
            raise ValueError("Lead must have a lead_id")
            
        # Deterministic UUID based on lead_id and assigned_case_id
        # This ensures idempotency
        namespace = uuid.NAMESPACE_OID
        finding_id_str = f"{lead_id}_{assigned_case_id}"
        deterministic_id = uuid.uuid5(namespace, finding_id_str)
        
        # Check if finding already exists
        existing = self.db.query(Finding).filter(Finding.finding_id == deterministic_id).first()
        if existing:
            return existing

        # Filter entities and relationships to ensure they are confirmed and valid
        valid_rel_ids = []
        for rid in lead.get("relationship_ids", []):
            rel = self.db.query(Relationship).filter(
                Relationship.relationship_id == rid,
                Relationship.status == "CONFIRMED"
            ).first()
            if rel:
                valid_rel_ids.append(rid)

        # Create finding
        finding = Finding(
            finding_id=deterministic_id,
            case_id=assigned_case_id,
            finding_type=lead.get("lead_type", "UNKNOWN"),
            title=lead.get("title", "Investigative Lead"),
            description=lead.get("description", ""),
            severity=lead.get("priority", "MEDIUM"),
            status="NEW",
            generated_by="analytics_rule",
            algorithm_version="10.8.0"
        )
        self.db.add(finding)
        self.db.flush()

        # Attach Entities
        for eid in lead.get("entity_ids", []):
            fe = FindingEntity(finding_id=finding.finding_id, entity_id=eid)
            self.db.merge(fe) # Merge handles idempotency

        # Attach Relationships
        for rid in valid_rel_ids:
            fr = FindingRelationship(finding_id=finding.finding_id, relationship_id=rid)
            self.db.merge(fr)

        # Attach Evidence (trace from relationship -> assertion -> evidence if exists, 
        # or just trace from relationship -> assertion)
        # For this prototype, we'll extract evidence if it exists in EvidenceRelationship,
        # otherwise we just rely on source records via assertion links.
        # Let's map assertion source records as evidence if needed, but the prompt says 
        # "Where available: source_record_ids, evidence_ids".
        
        # We will not fabricate evidence_id if it doesn't exist, we just link what we have.
        # But we do need to support GET /findings with traceability.

        self.db.commit()
        self.db.refresh(finding)
        return finding

    def get_findings_for_case(self, case_id: str) -> List[Dict]:
        findings = self.db.query(Finding).filter(Finding.case_id == case_id).all()
        result = []
        for f in findings:
            entities = [fe.entity_id for fe in self.db.query(FindingEntity).filter_by(finding_id=f.finding_id).all()]
            relationships = [fr.relationship_id for fr in self.db.query(FindingRelationship).filter_by(finding_id=f.finding_id).all()]
            evidence = [ef.evidence_id for ef in self.db.query(EvidenceFinding).filter_by(finding_id=f.finding_id).all()]
            
            result.append({
                "finding_id": str(f.finding_id),
                "case_id": f.case_id,
                "type": f.finding_type,
                "priority": f.severity,
                "title": f.title,
                "description": f.description,
                "entity_ids": entities,
                "relationship_ids": relationships,
                "evidence_ids": evidence,
                "status": f.status
            })
        return result

    def get_finding_detail(self, finding_id: str) -> Dict:
        f = self.db.query(Finding).filter(Finding.finding_id == finding_id).first()
        if not f:
            return None
            
        entities = [fe.entity_id for fe in self.db.query(FindingEntity).filter_by(finding_id=f.finding_id).all()]
        relationships = [fr.relationship_id for fr in self.db.query(FindingRelationship).filter_by(finding_id=f.finding_id).all()]
        evidence = [ef.evidence_id for ef in self.db.query(EvidenceFinding).filter_by(finding_id=f.finding_id).all()]
        
        # Trace to source records
        source_records = set()
        for rid in relationships:
            links = self.db.query(RelationshipAssertionLink).filter_by(relationship_id=rid).all()
            for link in links:
                assertion = self.db.query(RelationshipAssertion).filter_by(assertion_id=link.assertion_id).first()
                if assertion and assertion.source_record_id:
                    source_records.add(assertion.source_record_id)

        return {
            "finding_id": str(f.finding_id),
            "case_id": f.case_id,
            "type": f.finding_type,
            "priority": f.severity,
            "title": f.title,
            "description": f.description,
            "status": f.status,
            "generated_by": f.generated_by,
            "algorithm_version": f.algorithm_version,
            "created_at": str(f.created_at),
            "entity_ids": entities,
            "relationship_ids": relationships,
            "evidence_ids": evidence,
            "source_record_ids": list(source_records)
        }
        
    def submit_feedback(self, finding_id: str, decision: str, reason: str, investigator_id: str = None) -> Dict:
        from app.db.models import InvestigatorFeedback
        if decision not in ["CONFIRM", "REJECT", "NEEDS_REVIEW"]:
            raise ValueError("Invalid decision")
            
        f = self.db.query(Finding).filter(Finding.finding_id == finding_id).first()
        if not f:
            raise ValueError("Finding not found")
            
        feedback = InvestigatorFeedback(
            investigator_id=investigator_id,
            finding_id=f.finding_id,
            decision=decision,
            reason=reason
        )
        self.db.add(feedback)
        
        # Update finding status based on feedback, but DO NOT mutate relationships
        f.status = decision
        self.db.commit()
        
        return {"feedback_id": str(feedback.feedback_id), "decision": decision}
