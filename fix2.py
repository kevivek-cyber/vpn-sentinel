import json
with open('VPN_Sentinel_Main.ipynb', 'r', encoding='utf-8') as f:
    d = json.load(f)
src = d['cells'][2]['source']
src.insert(5, "import seaborn as sns\n")
d['cells'][2]['source'] = src
with open('VPN_Sentinel_Main.ipynb', 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=1)
