from sqlalchemy import create_engine, text
engine = create_engine("postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres")
with engine.connect() as conn:
    print("--- RELATIONSHIPS ---")
    for row in conn.execute(text("SELECT status, COUNT(*) FROM relationships GROUP BY status;")):
        print(row)
        
    print("--- ASSERTIONS ---")
    for row in conn.execute(text("SELECT COUNT(*) FROM relationship_assertions;")):
        print(row)
