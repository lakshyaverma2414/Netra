import json
import subprocess
out1 = subprocess.check_output(['node', 'check_ui.mjs', '1']).decode('utf-8')
api_resp1 = json.loads([l for l in out1.split('\n') if l.startswith('API_RESPONSE:')][0].replace('API_RESPONSE:', '').strip())
print("Nodes Depth 1:", [n['data']['id'] for n in api_resp1['nodes']])
