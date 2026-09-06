from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres')
with engine.connect() as conn:
    res = conn.execute(text("SELECT record_id, case_id, processing_status FROM source_records")).fetchall()
    for r in res:
        print(r)
        
    res2 = conn.execute(text("SELECT case_id, count(*) FROM cases GROUP BY case_id")).fetchall()
    print("Cases:", res2)
