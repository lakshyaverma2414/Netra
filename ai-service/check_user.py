from sqlalchemy import create_engine, text
engine = create_engine("postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres")
with engine.connect() as conn:
    res = conn.execute(text("SELECT id, username FROM users WHERE username = 'OFFICER_001';"))
    for row in res:
        print(row)
