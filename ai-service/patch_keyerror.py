import re

with open('app/api/graph.py', 'r') as f:
    code = f.read()

# Fix the keyerror issue just in case
code = code.replace('e["data"]["status"] == "CONFIRMED"', 'e["data"].get("status") == "CONFIRMED"')

with open('app/api/graph.py', 'w') as f:
    f.write(code)
