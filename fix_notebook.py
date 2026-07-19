import json

with open('VPN_Sentinel_Main.ipynb', 'r', encoding='utf-8') as f:
    d = json.load(f)

for cell in d['cells']:
    if cell['cell_type'] == 'code':
        source = cell['source']
        for i, line in enumerate(source):
            if line == 'flow_features = [\n':
                if len(source) > i+3 and source[i+3] == ']\n':
                    source.insert(i+3, "    'fwd_pkt_len_std', 'bwd_pkt_len_std', 'flow_iat_max', 'flow_iat_min'\n")
                    source.insert(i+3, "    'fwd_pkt_len_max', 'fwd_pkt_len_min', 'bwd_pkt_len_max', 'bwd_pkt_len_min',\n")

with open('VPN_Sentinel_Main.ipynb', 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=1)
