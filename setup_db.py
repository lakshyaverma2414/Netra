import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

dsn_old = "dbname=postgres user=postgres password=netra_admin host=127.0.0.1 port=5433"
try:
    with psycopg2.connect(dsn_old) as conn:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            # Change postgres password
            cur.execute("ALTER USER postgres WITH PASSWORD 'netra_secure_dev_password';")
            
            # Create netra_app role
            cur.execute("DROP ROLE IF EXISTS netra_app;")
            cur.execute("CREATE ROLE netra_app WITH LOGIN PASSWORD 'netra_app_password';")
            cur.execute("GRANT ALL PRIVILEGES ON DATABASE postgres TO netra_app;")
            cur.execute("GRANT USAGE ON SCHEMA public TO netra_app;")
            cur.execute("GRANT CREATE ON SCHEMA public TO netra_app;")
            # AGE requires specific permissions
            cur.execute("GRANT USAGE ON SCHEMA ag_catalog TO netra_app;")
            
            # Install pgvector if missing
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            print("Security rotation and pgvector installation completed.")
except Exception as e:
    print(f"Error: {e}")

