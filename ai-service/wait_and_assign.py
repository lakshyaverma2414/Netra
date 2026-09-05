import time
from sqlalchemy import create_engine, text
engine = create_engine("postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres")
with engine.connect() as conn:
    while True:
        res = conn.execute(text("SELECT COUNT(*) FROM cases;"))
        cnt = res.fetchone()[0]
        print(f"Cases count: {cnt}")
        if cnt == 10:
            print("10 cases reached! Assigning to OFFICER_001...")
            conn.execute(text("UPDATE cases SET created_by = (SELECT user_id FROM users WHERE username = 'OFFICER_001') WHERE case_id LIKE 'C-0%';"))
            conn.commit()
            print("Assignment done.")
            break
        time.sleep(5)
