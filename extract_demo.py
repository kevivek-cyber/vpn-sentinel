import json
with open('ipynb demo/vpn_non-vpn_classification.ipynb', 'r', encoding='utf-8') as f:
    d = json.load(f)
with open('demo_extracted.txt', 'w', encoding='utf-8') as out:
    for i, cell in enumerate(d['cells']):
        out.write(f'--- CELL {i} TYPE: {cell["cell_type"]} ---\n')
        out.write(''.join(cell['source']) + '\n\n')
