import json
with open('VPN_Sentinel_Main.ipynb', 'r', encoding='utf-8') as f:
    d = json.load(f)
src = d['cells'][-2]['source']
new_src = [line.replace(", algorithm='SAMME'", "") for line in src]
d['cells'][-2]['source'] = new_src
with open('VPN_Sentinel_Main.ipynb', 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=1)
