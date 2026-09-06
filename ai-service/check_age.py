from sqlalchemy import create_engine, text
engine = create_engine('postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres')
with engine.connect() as conn:
    conn.execute(text("LOAD 'age'"))
    conn.execute(text('SET search_path = ag_catalog, "$user", public'))
    res = conn.execute(text("SELECT * FROM cypher('crime_network', $$ MATCH (n) RETURN count(n) $$) as (c agtype);")).scalar()
    print("Vertices in crime_network:", res)
    res2 = conn.execute(text("SELECT * FROM cypher('crime_network', $$ MATCH ()-[e]->() RETURN count(e) $$) as (c agtype);")).scalar()
    print("Edges in crime_network:", res2)
