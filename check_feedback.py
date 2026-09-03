from app.db.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
columns = inspector.get_columns('investigator_feedback')
for c in columns:
    print(c['name'], c['type'])
