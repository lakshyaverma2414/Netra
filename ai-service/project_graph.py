from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.graph.projection_service import ProjectionService

engine = create_engine("postgresql://postgres:netra_secure_dev_password@localhost:5433/postgres")
Session = sessionmaker(bind=engine)
db = Session()
svc = ProjectionService(db)
res = svc.project_all()
print("Projection Result:", res)
