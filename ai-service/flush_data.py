import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

dsn = "dbname=postgres user=postgres password=netra_secure_dev_password host=127.0.0.1 port=5433"
with psycopg2.connect(dsn) as conn:
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    with conn.cursor() as cur:
        # Drop and recreate AGE graph
        cur.execute("LOAD 'age';")
        cur.execute("SET search_path = ag_catalog, \"$user\", public;")
        try:
            cur.execute("SELECT drop_graph('crime_network', true);")
            print("Graph 'crime_network' dropped.")
        except Exception as e:
            print("Graph drop error:", e)
            
        try:
            cur.execute("SELECT create_graph('crime_network');")
            print("Graph 'crime_network' recreated.")
        except Exception as e:
            print("Graph create error:", e)

        # Truncate tables
        tables = [
            "relationship_assertions",
            "relationships",
            "entity_mentions",
            "entities",
            "observations",
            "derived_artifacts",
            "processing_runs",
            "evidence",
            "source_records",
            "ingestion_batches",
            "cases"
        ]
        
        for t in tables:
            try:
                cur.execute(f"TRUNCATE TABLE {t} CASCADE;")
                print(f"Truncated {t}")
            except Exception as e:
                print(f"Failed to truncate {t}: {e}")
                
print("Data flushed successfully.")
