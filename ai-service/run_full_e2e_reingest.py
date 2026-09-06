"""
NETRA — Full E2E Reseed + Reingest
====================================
1. Discover the 10 benchmark TXT files from the corpus directory on disk
2. Insert evidence + evidence_cases rows for each case
3. Run the full unstructured pipeline (Qwen -> ER -> Validation -> graph projection)
4. Print summary report

Run with:
    NETRA_ONTOLOGY_V1_ENABLED=true python3 run_full_e2e_reingest.py
"""

import os
import sys
import uuid
import logging
import hashlib
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

sys.path.insert(0, "/mnt/d/NETRA/SIH2026/ai-service")
os.environ["NETRA_ONTOLOGY_V1_ENABLED"] = "true"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s"
)
logger = logging.getLogger("e2e_reingest")

DB_URL = "postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres"
CORPUS_ROOT = "/mnt/d/sahaay/NETRA_10_CASE_EVIDENCE_CORPUS_multimedia_v2/NETRA_10_CASE_EVIDENCE_CORPUS_FINAL"

# Map case_id -> TXT filename
CASE_FILES = {
    "C-001": "C-001_1993_Bombay_Bomb_Blast.txt",
    "C-002": "C-002_Pradeep_Jain_Murder_Abu_Salem.txt",
    "C-003": "C-003_26_11_Mumbai_Attacks.txt",
    "C-004": "C-004_Parliament_Attack.txt",
    "C-005": "C-005_Rajiv_Gandhi_Assassination.txt",
    "C-006": "C-006_Red_Fort_Attack.txt",
    "C-007": "C-007_Dilsukhnagar_Twin_Blasts.txt",
    "C-008": "C-008_NSEL_Scam.txt",
    "C-009": "C-009_PNB_Nirav_Modi_Fraud.txt",
    "C-010": "C-010_Satyam_Scam.txt",
}


# ─────────────────────────────────────────────
# STEP 1: Flush derived AI data only
# ─────────────────────────────────────────────
def flush_derived_data():
    logger.info("=== STEP 1: Flushing derived AI data (preserving cases) ===")
    dsn = "dbname=postgres user=postgres password=netra_secure_dev_password host=127.0.0.1 port=5433"

    with psycopg2.connect(dsn) as conn:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute("LOAD 'age';")
            cur.execute("SET search_path = ag_catalog, \"$user\", public;")
            try:
                cur.execute("SELECT drop_graph('crime_network', true);")
                logger.info("  AGE graph dropped.")
            except Exception as e:
                logger.warning(f"  Graph drop: {e}")
            try:
                cur.execute("SELECT create_graph('crime_network');")
                logger.info("  AGE graph recreated.")
            except Exception as e:
                logger.warning(f"  Graph create: {e}")

            # Flush derived tables only — do NOT truncate 'cases' or 'evidence'
            derived_tables = [
                "relationship_assertion_links",
                "relationship_assertions",
                "relationship_cases",
                "relationships",
                "case_entities",
                "entity_mentions",
                "entity_resolution_log",
                "entity_aliases",
                "entities",
                "event_entities",
                "events",
                "derived_artifacts",
                "processing_runs",
                "observations",
                "evidence_cases",
                "evidence",
                "source_records",
                "ingestion_batches",
            ]
            for t in derived_tables:
                try:
                    cur.execute(f"TRUNCATE TABLE {t} CASCADE;")
                    logger.info(f"  Truncated: {t}")
                except Exception as e:
                    logger.warning(f"  Failed to truncate {t}: {e}")

    logger.info("Flush complete.")


# ─────────────────────────────────────────────
# STEP 2: Reseed evidence rows from disk
# ─────────────────────────────────────────────
def reseed_evidence():
    logger.info("\n=== STEP 2: Reseeding evidence from disk corpus ===")
    engine = create_engine(DB_URL)
    seeded = []

    with engine.connect() as conn:
        for case_id, filename in CASE_FILES.items():
            filepath = os.path.join(CORPUS_ROOT, case_id, filename)

            if not os.path.exists(filepath):
                logger.warning(f"  File NOT found: {filepath} — skipping {case_id}")
                continue

            file_hash = hashlib.sha256(open(filepath, "rb").read()).hexdigest()
            ev_id = str(uuid.uuid4())

            conn.execute(text("""
                INSERT INTO evidence (evidence_id, case_id, evidence_type, storage_uri, file_hash,
                                      provenance_status, collected_at)
                VALUES (:ev_id, :case_id, 'TXT', :uri, :hash, 'VERIFIED', :now)
                ON CONFLICT DO NOTHING
            """), {
                "ev_id": ev_id,
                "case_id": case_id,
                "uri": filepath,
                "hash": file_hash,
                "now": datetime.now(timezone.utc)
            })

            conn.execute(text("""
                INSERT INTO evidence_cases (evidence_id, case_id)
                VALUES (:ev_id, :case_id)
                ON CONFLICT DO NOTHING
            """), {"ev_id": ev_id, "case_id": case_id})

            conn.commit()
            seeded.append((case_id, ev_id, filepath))
            logger.info(f"  Seeded: {case_id} -> {filename}")

    logger.info(f"Evidence reseeded: {len(seeded)} files.")
    return seeded


# ─────────────────────────────────────────────
# STEP 3: Run full pipeline per evidence file
# ─────────────────────────────────────────────
def reingest_all(seeded_evidence):
    logger.info("\n=== STEP 3: Running full AI pipeline per evidence file ===")
    engine = create_engine(DB_URL)
    Session = sessionmaker(bind=engine)

    from app.ingestion.core.batch_manager import BatchManager
    from app.ingestion.pipelines.unstructured_pipeline import process_unstructured_evidence

    results = []

    for case_id, ev_id, filepath in seeded_evidence:
        db = Session()
        try:
            logger.info(f"\n--- {case_id}: {os.path.basename(filepath)} ---")

            bm = BatchManager(db)
            batch = bm.create_batch(
                dataset_id="DS_UNSTRUCTURED",
                case_id=case_id,
                original_filename=filepath,
                file_type="TXT",
                file_hash=hashlib.sha256(open(filepath, "rb").read()).hexdigest()
            )

            process_unstructured_evidence(db, batch.batch_id, filepath, "TXT", case_id)
            logger.info(f"  ✓ Done: {case_id}")
            results.append({"case_id": case_id, "status": "SUCCESS"})

        except Exception as e:
            logger.error(f"  ✗ Failed: {case_id}: {e}", exc_info=True)
            results.append({"case_id": case_id, "status": f"FAILED: {str(e)[:100]}"})
        finally:
            db.close()

    return results


# ─────────────────────────────────────────────
# STEP 4: Final report
# ─────────────────────────────────────────────
def print_summary(pipeline_results):
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        entities  = conn.execute(text("SELECT count(*) FROM entities")).fetchone()[0]
        events    = conn.execute(text("SELECT count(*) FROM events")).fetchone()[0]
        total_a   = conn.execute(text("SELECT count(*) FROM relationship_assertions")).fetchone()[0]
        confirmed = conn.execute(text("SELECT count(*) FROM relationship_assertions WHERE status='CONFIRMED'")).fetchone()[0]
        review    = conn.execute(text("SELECT count(*) FROM relationship_assertions WHERE status='NEEDS_REVIEW'")).fetchone()[0]
        cand      = conn.execute(text("SELECT count(*) FROM relationship_assertions WHERE status='CANDIDATE'")).fetchone()[0]
        rejected  = conn.execute(text("SELECT count(*) FROM relationship_assertions WHERE status='REJECTED'")).fetchone()[0]
        canonical = conn.execute(text("SELECT count(*) FROM relationships WHERE status='CONFIRMED'")).fetchone()[0]

    # --- STEP 4: Project to Apache AGE ---
    print("\n=== STEP 4: Projecting to Apache AGE Graph ===")
    from app.graph.projection_service import ProjectionService
    from sqlalchemy.orm import Session
    with Session(engine) as db_session:
        proj = ProjectionService(db_session)
        proj_res = proj.project_all()
        print(f"  Projected: {proj_res['vertices_updated']} vertices, {proj_res['edges_updated']} edges.")

    # --- FINAL REPORT ---
    print("\n" + "="*62)
    print("  NETRA FULL E2E REINGEST — FINAL REPORT")
    print("="*62)
    for r in pipeline_results:
        icon = "✓" if r["status"] == "SUCCESS" else "✗"
        print(f"  {icon} {r['case_id']}: {r['status']}")
    print()
    print(f"  Entities resolved          : {entities}")
    print(f"  Events projected           : {events}")
    print(f"  Total relationship assertions: {total_a}")
    print(f"    ✓ CONFIRMED              : {confirmed}")
    print(f"    ⚠ NEEDS_REVIEW           : {review}")
    print(f"    ○ CANDIDATE              : {cand}")
    print(f"    ✗ REJECTED               : {rejected}")
    print(f"  Canonical relationships    : {canonical}  (AGE-ready)")
    print("="*62)
    print("  Check the portal now — graphs should be populated.")
    print("="*62 + "\n")


if __name__ == "__main__":
    flush_derived_data()
    seeded = reseed_evidence()
    if not seeded:
        logger.error("No evidence seeded — aborting. Check corpus path.")
        sys.exit(1)
    results = reingest_all(seeded)
    print_summary(results)
