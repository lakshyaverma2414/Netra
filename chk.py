from sqlalchemy import create_engine, text
engine = create_engine('postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres')
with engine.connect() as conn:
    print("--- user_permissions ---")
    res = conn.execute(text("SELECT * FROM user_permissions LIMIT 5;"))
    for row in res: print(row)
