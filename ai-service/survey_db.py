from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres')
with engine.connect() as conn:
    # Check what data is backing the 10 benchmark cases
    print("=== 10 Benchmark Cases ===")
    cases = conn.execute(text("SELECT case_id, title FROM cases WHERE case_id LIKE 'C-0%' ORDER BY case_id")).fetchall()
    for c in cases:
        print(f"  {c[0]}: {c[1]}")

    print("\n=== Evidence per case ===")
    ev = conn.execute(text("SELECT ec.case_id, count(*) FROM evidence e JOIN evidence_cases ec ON e.evidence_id = ec.evidence_id GROUP BY ec.case_id ORDER BY ec.case_id")).fetchall()
    for r in ev:
        print(f"  {r[0]}: {r[1]} evidence files")

    print("\n=== Current assertions ===")
    a = conn.execute(text("SELECT status, count(*) FROM relationship_assertions GROUP BY status")).fetchall()
    for r in a:
        print(f"  {r[0]}: {r[1]}")

    print("\n=== Current canonical relationships ===")
    r2 = conn.execute(text("SELECT status, count(*) FROM relationships GROUP BY status")).fetchall()
    for r in r2:
        print(f"  {r[0]}: {r[1]}")

    print("\n=== Evidence files (storage_uri) for C-001 to C-010 ===")
    ev2 = conn.execute(text("""
        SELECT ec.case_id, e.storage_uri, e.evidence_type
        FROM evidence e
        JOIN evidence_cases ec ON e.evidence_id = ec.evidence_id
        WHERE ec.case_id LIKE 'C-0%'
        ORDER BY ec.case_id
    """)).fetchall()
    for r in ev2:
        print(f"  {r[0]} | {r[2]} | {r[1]}")
