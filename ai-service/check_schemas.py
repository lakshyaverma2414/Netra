from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres')

with engine.connect() as conn:
    print("Mentions schema:")
    for row in conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='entity_mentions'")): print(row[0])
    print("Assertions schema:")
    for row in conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='relationship_assertions'")): print(row[0])
    print("Observations schema:")
    for row in conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='observations'")): print(row[0])
