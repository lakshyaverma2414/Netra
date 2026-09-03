import psycopg2
from psycopg2.extras import RealDictCursor

dsn = "dbname=postgres user=postgres password=netra_secure_dev_password host=127.0.0.1 port=5433"
with psycopg2.connect(dsn) as conn:
    with conn.cursor() as cur:
        # Create cases
        cur.execute("INSERT INTO cases (case_id, case_number, title) VALUES ('CASE-001', 'CASE-001-NUM', 'Case 1');")
        cur.execute("INSERT INTO cases (case_id, case_number, title) VALUES ('CASE-002', 'CASE-002-NUM', 'Case 2');")
        
        # Create shared phone
        cur.execute("INSERT INTO entities (entity_id, entity_type, canonical_name, normalized_value) VALUES ('PHONE-TEST-1', 'PHONE', '9876543210', '9876543210');")
        
        # Link to cases
        cur.execute("INSERT INTO case_entities (case_id, entity_id) VALUES ('CASE-001', 'PHONE-TEST-1');")
        cur.execute("INSERT INTO case_entities (case_id, entity_id) VALUES ('CASE-002', 'PHONE-TEST-1');")
        
        print("Cross-case test data seeded successfully.")
    conn.commit()
