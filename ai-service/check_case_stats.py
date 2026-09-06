import json
import urllib.request

for case_id in [f"C-{i:03d}" for i in range(1, 11)]:
    try:
        req = urllib.request.urlopen(f"http://127.0.0.1:8000/api/v1/analytics/cases/{case_id}/network")
        data = json.loads(req.read().decode())
        print(f"Case {case_id}: {data['entities_analyzed']} entities, {len(data['leads'])} leads")
    except Exception as e:
        print(f"Error {case_id}: {e}")
