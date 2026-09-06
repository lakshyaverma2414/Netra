from sqlalchemy import create_engine, text
import pandas as pd

engine = create_engine("postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres")
with engine.connect() as conn:
    print("--- Source Records Status ---")
    res = conn.execute(text("SELECT processing_status, COUNT(*) FROM source_records GROUP BY processing_status")).fetchall()
    print(res)
    
    print("\n--- Relationship Assertions Evidence Status ---")
    res2 = conn.execute(text("SELECT status, count(*), count(source_record_id) as has_evidence FROM relationship_assertions GROUP BY status")).fetchall()
    print(res2)
