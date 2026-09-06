from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres')
with engine.connect() as conn:
    print("=== Cases ===")
    r = conn.execute(text("SELECT case_id, title FROM cases WHERE case_id LIKE 'C-0%' ORDER BY case_id")).fetchall()
    for row in r: print(f"  {row[0]}: {row[1]}")

    print("\n=== Evidence ===")
    r = conn.execute(text("SELECT case_id, evidence_type, storage_uri FROM evidence ORDER BY case_id")).fetchall()
    for row in r: print(f"  {row[0]} | {row[1]} | {row[2][-60:]}")

    print("\n=== Ingestion Batches ===")
    r = conn.execute(text("SELECT batch_id, case_id, dataset_id, status, records_received FROM ingestion_batches ORDER BY case_id")).fetchall()
    for row in r: print(f"  {row[1]} | {row[2]} | status={row[3]} | records={row[4]}")

    print("\n=== Observations ===")
    r = conn.execute(text("SELECT count(*) FROM observations")).fetchone()
    print(f"  Total: {r[0]}")

    print("\n=== Entities ===")
    r = conn.execute(text("SELECT count(*) FROM entities")).fetchone()
    print(f"  Total: {r[0]}")

    print("\n=== Assertions ===")
    r = conn.execute(text("SELECT status, count(*) FROM relationship_assertions GROUP BY status")).fetchall()
    for row in r: print(f"  {row[0]}: {row[1]}")

    print("\n=== Canonical Relationships ===")
    r = conn.execute(text("SELECT count(*) FROM relationships")).fetchone()
    print(f"  Total: {r[0]}")
