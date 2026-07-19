import os

filepath = r"c:\Users\Vivek\Desktop\vpn sentinel\frontend\index.html"
with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update global JS setup and theming
old_setup = """        const BACKEND_URL = (window.location.protocol === 'file:' || window.location.origin === 'null')
            ? 'http://127.0.0.1:8000'
            : window.location.origin;
        const API_URL = `${BACKEND_URL}/api`;"""

new_setup = """        const BACKEND_URL = (window.location.protocol === 'file:' || window.location.origin === 'null')
            ? 'http://127.0.0.1:8000'
            : window.location.origin;
        const API_URL = `${BACKEND_URL}/api`;
        
        // Multi-Tenant Architecture & Dynamic Theming
        const urlParams = new URLSearchParams(window.location.search);
        const tenantId = urlParams.get('tenant') || 'default';
        const primaryColor = urlParams.get('primary');
        if (primaryColor) {
            document.documentElement.style.setProperty('--accent-primary', '#' + primaryColor);
            document.documentElement.style.setProperty('--accent-safe', '#' + primaryColor);
        }
        
        // Show Tenant ID in UI if present
        window.addEventListener('DOMContentLoaded', () => {
            if (tenantId !== 'default') {
                document.querySelector('.header-title').innerHTML += ` <span style="font-size:0.8rem; color:var(--text-muted); background:rgba(255,255,255,0.05); padding:4px 8px; border-radius:6px; margin-left:12px;">Tenant: ${tenantId}</span>`;
            }
        });"""
html = html.replace(old_setup, new_setup)

# 2. Update fetch URLs
html = html.replace("fetch(`${API_URL}/stats`)", "fetch(`${API_URL}/stats?tenant=${tenantId}`)")
html = html.replace("fetch(`${API_URL}/history`)", "fetch(`${API_URL}/history?tenant=${tenantId}`)")
html = html.replace("fetch(`${API_URL}/ingest`", "fetch(`${API_URL}/ingest?tenant=${tenantId}`")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(html)
