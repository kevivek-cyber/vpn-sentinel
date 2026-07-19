import os, glob

for file in glob.glob('frontend/*.html'):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if Integration Guide link exists
    if 'href="integration.html"' in content and 'href="how_it_works.html"' not in content:
        content = content.replace('<a href="integration.html">🔌 Integration Guide</a>', '<a href="integration.html">🔌 Integration Guide</a>\n            <a href="how_it_works.html">📖 How It Works</a>')
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
