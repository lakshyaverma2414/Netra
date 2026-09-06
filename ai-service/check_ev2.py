from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres')
with engine.connect() as conn:
    # evidence HAS a case_id column directly - just use it
    ev = conn.execute(text("SELECT evidence_id, case_id, evidence_type, storage_uri FROM evidence WHERE case_id LIKE 'C-0%' ORDER BY case_id")).fetchall()
    print(f"Evidence with case_id C-0*: {len(ev)} rows")
    for r in ev:
        print(f"  {r[1]} | {r[2]} | {r[3][:80]}")
