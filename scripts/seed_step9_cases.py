import os
import uuid
import sys
from sqlalchemy import text
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../ai-service')))
from app.db.database import SessionLocal, engine
from app.db.models import (User, Case, Entity, EntityMention, EntityAlias, EntityResolutionLog,
                           CaseEntity, Relationship, RelationshipAssertion, RelationshipCase,
                           Evidence, EvidenceCase, Finding, SourceRecord, IngestionBatch,
                           EvidenceCustodyLog, Document)
from app.graph.age_graph_repository import AgeGraphRepository

def reset_database():
    print("Resetting database...")
    db = SessionLocal()
    db.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
    db.execute(text("GRANT ALL ON SCHEMA public TO public;"))
    db.execute(text("CREATE EXTENSION IF NOT EXISTS vector SCHEMA public;"))
    db.commit()
    
    schema_path = os.path.join(os.path.dirname(__file__), '../migrations/001_initial_schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    conn = engine.raw_connection()
    try:
        cur = conn.cursor()
        cur.execute(schema_sql)
        conn.commit()
    finally:
        conn.close()

    age_repo = AgeGraphRepository(db, "crime_network")
    age_repo.db.execute(text("SELECT drop_graph('crime_network', true) WHERE EXISTS (SELECT FROM ag_graph WHERE name = 'crime_network');"))
    age_repo.db.execute(text("SELECT create_graph('crime_network');"))
    age_repo.db.commit()
    db.close()
    print("Database reset complete.")

def seed_data():
    print("Seeding Step 9.1 Data...")
    db = SessionLocal()
    age_repo = AgeGraphRepository(db, "crime_network")
    
    try:
        # Users
        admin = User(user_id=uuid.uuid4(), username="admin", display_name="Admin", password_hash="hash", role="ADMIN")
        inv1 = User(user_id=uuid.uuid4(), username="inv_01", display_name="Investigator 1", password_hash="hash", role="INVESTIGATOR")
        db.add_all([admin, inv1])
        db.flush()
        
        # Cases
        c1 = Case(case_id="C-001", case_number="C-001", title="Operation Black Web", description="Dark web narcotics trafficking", created_by=inv1.user_id)
        c2 = Case(case_id="C-002", case_number="C-002", title="Syndicate Ghost", description="Hawala and money laundering network", created_by=inv1.user_id)
        c3 = Case(case_id="C-003", case_number="C-003", title="Border Route", description="Cross-border smuggling logistics", created_by=inv1.user_id)
        db.add_all([c1, c2, c3])
        db.flush()
        
        # Ingestion Batches
        b1 = IngestionBatch(case_id="C-001", submitted_by=inv1.user_id, original_filename="batch1.zip", file_type="ZIP", file_hash="h1", status="COMPLETED")
        b2 = IngestionBatch(case_id="C-002", submitted_by=inv1.user_id, original_filename="batch2.zip", file_type="ZIP", file_hash="h2", status="COMPLETED")
        b3 = IngestionBatch(case_id="C-003", submitted_by=inv1.user_id, original_filename="batch3.zip", file_type="ZIP", file_hash="h3", status="COMPLETED")
        db.add_all([b1, b2, b3])
        db.flush()
        
        # Source Records
        records = [
            # C-001
            ("SR-101", b1.batch_id, "C-001", "FIR", {"text": "FIR-001: Arrest of Aryan (Shadow) with handset +91-9876543210."}),
            ("SR-102", b1.batch_id, "C-001", "CDR", {"text": "CDR Analysis for +91-9876543210."}),
            ("SR-103", b1.batch_id, "C-001", "SURVEILLANCE", {"text": "Cyber surveillance narrative: Subject observed in Sector 12 Warehouse."}),
            ("SR-104", b1.batch_id, "C-001", "INTEL", {"text": "Unverified tip: Aryan associated with Rajan."}),
            # C-002
            ("SR-201", b2.batch_id, "C-002", "FIR", {"text": "EOW FIR regarding Ghost Shell Co."}),
            ("SR-202", b2.batch_id, "C-002", "FINANCIAL", {"text": "Financial Transaction Report: V. Singh transferred 50L to ghost@bank."}),
            ("SR-203", b2.batch_id, "C-002", "CDR", {"text": "CDR extract for +91-9999988888."}),
            ("SR-204", b2.batch_id, "C-002", "DOC", {"text": "EOW Investigation narrative: Vikram Singh suspected of hawala operations."}),
            ("SR-205", b2.batch_id, "C-002", "INTEL", {"text": "Informant log: Vikram operates Ghost Shell Co."}),
            # C-003
            ("SR-301", b3.batch_id, "C-003", "BORDER_LOG", {"text": "Border checkpoint log: RJ-14-XYZ crossed at 03:00 AM."}),
            ("SR-302", b3.batch_id, "C-003", "RTO", {"text": "RTO Record: RJ-14-XYZ registered to Rajan."}),
            ("SR-303", b3.batch_id, "C-003", "FINANCIAL", {"text": "Financial Intelligence: Beneficiary account ghost@bank linked to Rajan."}),
            ("SR-304", b3.batch_id, "C-003", "DOC", {"text": "Investigation memo: Logistics managed by Vikram Singh."}),
            ("SR-305", b3.batch_id, "C-003", "SURVEILLANCE", {"text": "Subject Rajan observed near border crossing."})
        ]
        
        for r_id, b_id, c_id, s_type, payload in records:
            db.add(SourceRecord(record_id=r_id, batch_id=b_id, case_id=c_id, source_type=s_type, raw_payload=payload))
        db.flush()

        # Unstructured Documents (Synthetic Documents)
        docs = [
            ("DOC-001", "C-001", b1.batch_id, "SR-103", "cyber_surveillance_14aug.pdf", "application/pdf"),
            ("DOC-002", "C-002", b2.batch_id, "SR-204", "eow_investigation_brief.docx", "application/msword"),
            ("DOC-003", "C-002", b2.batch_id, "SR-202", "financial_transaction_analysis.pdf", "application/pdf"),
            ("DOC-004", "C-003", b3.batch_id, "SR-301", "border_checkpoint_report.pdf", "application/pdf"),
            ("DOC-005", "C-003", b3.batch_id, "SR-304", "logistics_investigation_memo.pdf", "application/pdf")
        ]
        
        for d_id, c_id, b_id, sr_id, fname, mtype in docs:
            db.add(Document(document_id=d_id, case_id=c_id, batch_id=b_id, source_record_id=sr_id, filename=fname, storage_uri=f"/synthetic/{fname}", document_hash=d_id, mime_type=mtype))
        db.flush()

        # Entities
        ents = [
            ("P-001", "PERSON", "Aryan", "ARYAN"),
            ("PH-001", "PHONE", "+91-9876543210", "919876543210"),
            ("LOC-001", "LOCATION", "Sector 12 Warehouse", "SECTOR 12 WAREHOUSE"),
            ("PH-002", "PHONE", "+91-9999988888", "919999988888"),
            ("P-002", "PERSON", "Vikram Singh", "VIKRAM SINGH"),
            ("UPI-001", "UPI_ID", "ghost@bank", "GHOST@BANK"),
            ("ORG-001", "ORGANIZATION", "Ghost Shell Co", "GHOST SHELL CO"),
            ("P-003", "PERSON", "Rajan", "RAJAN"),
            ("VEH-001", "VEHICLE", "RJ-14-XYZ", "RJ14XYZ"),
            ("P-004", "PERSON", "Informant X", "INFORMANT X"), # Extra entity
            ("LOC-002", "LOCATION", "Border Post Alpha", "BORDER POST ALPHA") # Extra
        ]
        for e_id, e_type, c_name, n_val in ents:
            db.add(Entity(entity_id=e_id, entity_type=e_type, canonical_name=c_name, normalized_value=n_val, resolution_status="CONFIRMED"))
        db.flush()

        # Fragmented Mentions & Aliases
        mentions = [
            ("M-001", "PERSON", "Aryan", "P-001", "SR-101"),
            ("M-002", "PERSON", "Shadow", "P-001", "SR-101"),
            ("M-003", "PERSON", "Vikram Singh", "P-002", "SR-204"),
            ("M-004", "PERSON", "V. Singh", "P-002", "SR-202"),
            ("M-005", "PERSON", "Vikram S.", "P-002", "SR-304"),
            ("M-006", "PERSON", "Rajan", "P-003", "SR-302"),
            ("M-007", "PERSON", "Raj", "P-003", "SR-305")
        ]
        for m_id, m_type, m_text, r_id, sr_id in mentions:
            db.add(EntityMention(mention_id=m_id, entity_type=m_type, extracted_text=m_text, normalized_value=m_text.upper(), extraction_method="NER", resolved_entity_id=r_id, source_record_id=sr_id))
            db.add(EntityResolutionLog(mention_id=m_id, candidate_entity_id=r_id, decision="CONFIRMED", probability=0.98))
        db.flush()
        
        db.add(EntityAlias(entity_id="P-001", alias="Shadow", normalized_alias="SHADOW", source="SR-101"))
        db.add(EntityAlias(entity_id="P-002", alias="V. Singh", normalized_alias="V SINGH", source="SR-202"))
        db.flush()

        # Case Entities
        case_entities = [
            ("C-001", ["P-001", "PH-001", "LOC-001", "PH-002", "P-004"]),
            ("C-002", ["P-002", "PH-002", "UPI-001", "ORG-001"]),
            ("C-003", ["P-002", "P-003", "VEH-001", "UPI-001", "LOC-002"])
        ]
        for c_id, ent_list in case_entities:
            for e_id in ent_list:
                db.add(CaseEntity(case_id=c_id, entity_id=e_id))
        db.flush()

        # Relationships
        rels = [
            ("R-001", "P-001", "USES", "PH-001", "C-001", "SR-101", "PERSON", "PHONE"),
            ("R-002", "P-001", "LOCATED_AT", "LOC-001", "C-001", "SR-103", "PERSON", "LOCATION"),
            ("R-003", "PH-001", "COMMUNICATES_WITH", "PH-002", "C-001", "SR-102", "PHONE", "PHONE"),
            ("R-004", "P-002", "USES", "PH-002", "C-002", "SR-203", "PERSON", "PHONE"),
            ("R-005", "P-002", "TRANSFERRED_TO", "UPI-001", "C-002", "SR-202", "PERSON", "UPI_ID"),
            ("R-006", "P-002", "OWNS", "ORG-001", "C-002", "SR-201", "PERSON", "ORGANIZATION"),
            ("R-007", "P-002", "ASSOCIATED_WITH", "P-003", "C-003", "SR-304", "PERSON", "PERSON"),
            ("R-008", "P-003", "OWNS", "VEH-001", "C-003", "SR-302", "PERSON", "VEHICLE"),
            ("R-009", "P-003", "OWNS", "UPI-001", "C-003", "SR-303", "PERSON", "UPI_ID"),
            ("R-010", "VEH-001", "LOCATED_AT", "LOC-002", "C-003", "SR-301", "VEHICLE", "LOCATION")
        ]

        for rid, src, rel_type, tgt, cid, sr_id, src_lbl, tgt_lbl in rels:
            db.add(RelationshipAssertion(source_entity_id=src, target_entity_id=tgt, relationship_type=rel_type, status="ACCEPTED", source_record_id=sr_id))
            db.add(Relationship(relationship_id=rid, source_entity_id=src, target_entity_id=tgt, relationship_type=rel_type, status="CONFIRMED"))
            db.add(RelationshipCase(relationship_id=rid, case_id=cid))
            db.flush()
            age_repo.sync_confirmed_relationship(rid, src, tgt, rel_type, src_lbl, tgt_lbl, {"status": "CONFIRMED", "relationship_id": rid})

        # Negative Relationship
        bad_assert = RelationshipAssertion(source_entity_id="P-001", target_entity_id="P-003", relationship_type="ASSOCIATED_WITH", status="NEEDS_REVIEW", source_record_id="SR-104")
        db.add(bad_assert)
        bad_rel = Relationship(relationship_id="R-BAD-001", source_entity_id="P-001", target_entity_id="P-003", relationship_type="ASSOCIATED_WITH", status="NEEDS_REVIEW")
        db.add(bad_rel)
        db.flush()
        db.add(RelationshipCase(relationship_id="R-BAD-001", case_id="C-001"))

        # Evidence
        ev_data = [
            ("EV-001", "C-001", "FIR", "SR-101", "hash1"),
            ("EV-002", "C-001", "CDR Extract", "SR-102", "hash2"),
            ("EV-003", "C-001", "Surveillance Log", "SR-103", "hash3"),
            ("EV-004", "C-002", "Financial Transaction Report", "SR-202", "hash4"),
            ("EV-005", "C-002", "EOW Memo", "SR-204", "hash5"),
            ("EV-006", "C-003", "Border Checkpoint Report", "SR-301", "hash6"),
            ("EV-007", "C-003", "RTO Registry", "SR-302", "hash7"),
            ("EV-008", "C-003", "Logistics Memo", "SR-304", "hash8"),
            ("EV-009", "C-002", "Informant X Tip", "SR-205", "hash9"),
            ("EV-010", "C-001", "Cyber Intel Drop", "SR-104", "hash10"),
            ("EV-011", "C-003", "UPI Account Ledger", "SR-303", "hash11")
        ]
        
        for ev_id, c_id, src_str, sr_id, eh in ev_data:
            db.add(Evidence(evidence_id=ev_id, case_id=c_id, evidence_type="DOC", storage_uri=f"/evidence/{ev_id}", file_hash=eh, source=src_str))
            db.flush()
            db.add(EvidenceCase(evidence_id=ev_id, case_id=c_id))
        db.flush()
        
        # Custody Logs for EV-004
        db.add(EvidenceCustodyLog(evidence_id="EV-004", action="Collected", actor=inv1.user_id))
        db.add(EvidenceCustodyLog(evidence_id="EV-004", action="Transferred to Digital Forensics", actor=inv1.user_id))
        db.add(EvidenceCustodyLog(evidence_id="EV-004", action="Forensic Review", actor=inv1.user_id))
        db.add(EvidenceCustodyLog(evidence_id="EV-004", action="Investigator Review", actor=inv1.user_id))
        db.flush()

        # Findings
        findings = [
            ("C-001", "COMMUNICATION_LINK", "Suspicious cross-case communication detected", "PH-002 bridges Black Web and Syndicate Ghost."),
            ("C-002", "ENTITY_RESOLUTION", "Multiple aliases for Vikram Singh", "V. Singh and Vikram S. resolve to identical entity P-002."),
            ("C-003", "FINANCIAL_LINK", "UPI-001 is a critical financial bridge", "Connects logistics operator Rajan to hawala network."),
            ("C-003", "OPERATIONAL_LINK", "Smuggling vehicle isolated", "Vehicle RJ-14-XYZ physically located at Border Post Alpha."),
            ("C-002", "LEAD", "Informant Tip Review", "Investigate Ghost Shell Co operations.")
        ]
        for c_id, f_type, title, desc in findings:
            db.add(Finding(case_id=c_id, finding_type=f_type, title=title, description=desc, status="NEW"))
        db.flush()

        db.commit()
        print("Data Seeding 9.1 Complete.")

    except Exception as e:
        db.rollback()
        print("Error during seeding:", e)
    finally:
        db.close()

if __name__ == "__main__":
    reset_database()
    seed_data()
