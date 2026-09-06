from sqlalchemy import create_engine, text
engine = create_engine('postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres')
with engine.connect() as conn:
    c = conn.execute(text("SELECT count(*) FROM case_entities")).scalar()
    print("case_entities:", c)
    c2 = conn.execute(text("SELECT count(*) FROM relationship_cases")).scalar()
    print("relationship_cases:", c2)
