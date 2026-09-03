import json
import subprocess
out1 = subprocess.check_output(['node', 'check_ui.mjs', '1']).decode('utf-8')
api_resp1 = json.loads([l for l in out1.split('\n') if l.startswith('API_RESPONSE:')][0].replace('API_RESPONSE:', '').strip())
print("Depth 1 Nodes:", [n['data']['id'] for n in api_resp1['nodes']])

out2 = subprocess.check_output(['node', 'check_ui.mjs', '2']).decode('utf-8')
api_resp2 = json.loads([l for l in out2.split('\n') if l.startswith('API_RESPONSE:')][0].replace('API_RESPONSE:', '').strip())
print("Depth 2 Nodes:", [n['data']['id'] for n in api_resp2['nodes']])
