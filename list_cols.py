from sqlalchemy import create_engine, text
engine = create_engine('postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres')
with engine.connect() as conn:
    print("--- cases cols ---")
    res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'cases';"))
    for row in res: print(row[0])
    print("--- user_permissions cols ---")
    res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'user_permissions';"))
    for row in res: print(row[0])
    print("--- users cols ---")
    res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'users';"))
    for row in res: print(row[0])
