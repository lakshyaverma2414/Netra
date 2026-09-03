import json
from app.db.database import SessionLocal
from app.analytics.analytics_service import AnalyticsService

db = SessionLocal()
svc = AnalyticsService(db)
global_graph = svc.repo.get_global_subgraph()
G = svc._build_networkx_graph(global_graph)

edges = G.edges("UPI-001", data=True)
print("Edges for UPI-001:")
for e in edges:
    print(e)
