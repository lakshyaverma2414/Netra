from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres')
with engine.connect() as conn:
    # Check evidence_cases
    ec = conn.execute(text("SELECT count(*) FROM evidence_cases")).fetchone()[0]
    print("evidence_cases rows:", ec)
    
    # Check evidence table directly with case_id column
    cols = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='evidence'")).fetchall()
    print("evidence cols:", [c[0] for c in cols])
    
    # Check actual evidence data
    ev = conn.execute(text("SELECT evidence_id, case_id, evidence_type, storage_uri FROM evidence ORDER BY case_id LIMIT 5")).fetchall()
    for r in ev:
        print(f"  ev: {r}")
