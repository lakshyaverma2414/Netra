import requests

# 1. First get the findings for C-003 to get a valid finding_id
res = requests.get("http://127.0.0.1:8000/api/v1/analytics/cases/C-003/network")
data = res.json()
if not data.get("leads"):
    print("No leads found!")
else:
    finding_id = data["leads"][0]["finding_id"]
    print(f"Finding ID: {finding_id}")
    
    # 2. Try to submit feedback
    fb_res = requests.post(f"http://127.0.0.1:8000/api/v1/findings/{finding_id}/feedback", json={
        "decision": "CONFIRM",
        "reason": "Test"
    })
    print(f"Status Code: {fb_res.status_code}")
    print(f"Response: {fb_res.text}")
