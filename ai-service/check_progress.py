from sqlalchemy import create_engine, text
engine = create_engine("postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres")
with engine.connect() as conn:
    print("--- CASES COUNT ---")
    res = conn.execute(text("SELECT COUNT(*) FROM cases;"))
    print(res.fetchone()[0])
    
    print("--- EVIDENCE COUNT ---")
    res = conn.execute(text("SELECT COUNT(*) FROM evidence;"))
    print(res.fetchone()[0])
