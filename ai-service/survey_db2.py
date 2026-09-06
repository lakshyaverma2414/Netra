from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres')
with engine.connect() as conn:
    print("=== All evidence storage_uris ===")
    ev = conn.execute(text("SELECT evidence_id, evidence_type, storage_uri, case_id FROM evidence")).fetchall()
    for r in ev:
        print(f"  {r[3]} | {r[1]} | {r[2]}")
    
    print("\n=== Observations ===")
    obs = conn.execute(text("SELECT * FROM observations LIMIT 5")).fetchall()
    cols = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='observations'")).fetchall()
    print("Cols:", [c[0] for c in cols])
    for r in obs:
        print(f"  {r}")
