from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres')
with engine.connect() as conn:
    # Check all evidence
    ev = conn.execute(text("SELECT evidence_id, case_id, evidence_type, storage_uri FROM evidence LIMIT 10")).fetchall()
    print(f"All evidence: {len(ev)} rows (showing up to 10)")
    for r in ev:
        print(f"  case={r[1]} | type={r[2]} | {r[3][:80] if r[3] else 'NULL'}")
