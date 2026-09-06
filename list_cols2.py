from sqlalchemy import create_engine, text
engine = create_engine('postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres')
with engine.connect() as conn:
    print("--- case_links cols ---")
    res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'case_links';"))
    for row in res: print(row[0])
