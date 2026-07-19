with open('frontend/integration.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the content area start
start_idx = content.find('<div class="doc-container">')
if start_idx != -1:
    header = content[:start_idx + len('<div class="doc-container">')]
    footer = '\n    </div>\n</div>\n</body>\n</html>'
    
    # We will replace the active class in the nav bar
    header = header.replace('class="active"', '')
    header = header.replace('<a href="how_it_works.html">📖 How It Works</a>', '<a href="how_it_works.html" class="active">📖 How It Works</a>')
    
    body = """
        <div class="glass-panel" style="grid-column: span 12; border-top: 4px solid var(--accent-primary);">
            <h1 style="font-size: 2.5rem; margin-bottom: 8px;">How It Works</h1>
            <p style="color: var(--text-muted); font-size: 1.1rem; margin-bottom: 30px;">A step-by-step breakdown of the VPN-Sentinel Multi-Stage Inference Pipeline.</p>
            
            <h2 style="font-size: 1.6rem; margin-bottom: 20px; color: var(--accent-safe); display: flex; align-items: center; gap: 10px; margin-top: 0;">
                <span style="background: rgba(0,240,255,0.1); padding: 8px; border-radius: 8px;">1️⃣</span> Traffic Interception & Feature Extraction
            </h2>
            <p style="color: var(--text-muted); line-height: 1.6; font-size: 1.05rem; margin-bottom: 20px;">
                The system captures traffic using a live packet sniffer (<code>live_monitor.py</code>) or receives browser-level telemetry via our REST API. 
                It extracts complex features while disregarding payloads (protecting user privacy):
            </p>
            <ul style="color: var(--text-muted); line-height: 1.6; font-size: 1.05rem; margin-left: 40px; margin-bottom: 40px;">
                <li><strong>Flow Statistics:</strong> Packet Inter-Arrival Time (IAT) mean, variance, jitter ratios, and packet length distributions.</li>
                <li><strong>Browser Context:</strong> WebRTC IP leaks, HTML5 Geolocation vs. IP mismatch, timezone conflicts, and HTTP proxy headers.</li>
            </ul>

            <h2 style="font-size: 1.6rem; margin-bottom: 20px; color: var(--accent-primary); display: flex; align-items: center; gap: 10px;">
                <span style="background: rgba(157,78,221,0.1); padding: 8px; border-radius: 8px;">2️⃣</span> Stage 1: Anomaly Detection
            </h2>
            <p style="color: var(--text-muted); line-height: 1.6; font-size: 1.05rem; margin-bottom: 20px;">
                The extracted features are fed into our <strong>Stage 1 Random Forest Classifier</strong>. 
            </p>
            <ul style="color: var(--text-muted); line-height: 1.6; font-size: 1.05rem; margin-left: 40px; margin-bottom: 40px;">
                <li>Evaluates 16 flow features or 14 browser signals to determine if the traffic originates from a VPN/Proxy or a standard residential ISP.</li>
                <li>Trained against adversarial traffic-shaping (packet padding & timing delays), ensuring high evasion resistance.</li>
            </ul>

            <h2 style="font-size: 1.6rem; margin-bottom: 20px; color: var(--accent-vpn); display: flex; align-items: center; gap: 10px;">
                <span style="background: rgba(255,42,95,0.1); padding: 8px; border-radius: 8px;">3️⃣</span> Stage 2: Protocol Fingerprinting
            </h2>
            <p style="color: var(--text-muted); line-height: 1.6; font-size: 1.05rem; margin-bottom: 20px;">
                If Stage 1 flags the traffic as a VPN, it is immediately passed to the <strong>Stage 2 Protocol Fingerprinter</strong>.
            </p>
            <ul style="color: var(--text-muted); line-height: 1.6; font-size: 1.05rem; margin-left: 40px; margin-bottom: 40px;">
                <li>Classifies the exact tunneling protocol used: <strong>OpenVPN, WireGuard, or IKEv2</strong>.</li>
                <li>Enables granular security policies (e.g., allowing corporate IPSec while blocking consumer WireGuard).</li>
            </ul>

            <h2 style="font-size: 1.6rem; margin-bottom: 20px; color: white; display: flex; align-items: center; gap: 10px;">
                <span style="background: rgba(255,255,255,0.1); padding: 8px; border-radius: 8px;">4️⃣</span> SHAP Explainability & Alerting
            </h2>
            <p style="color: var(--text-muted); line-height: 1.6; font-size: 1.05rem; margin-bottom: 40px;">
                VPN Sentinel doesn't just block traffic—it explains <em>why</em>. A SHAP (SHapley Additive exPlanations) TreeExplainer analyzes the model's decision path, outputting exactly which features (e.g., <code>fwd_pkt_len_std</code> or <code>webrtc_ip_mismatch</code>) contributed most to the VPN classification.
            </p>
            
            <h2 style="font-size: 1.6rem; margin-bottom: 20px; color: white;">Architecture Diagram</h2>
            <div style="background: rgba(0,0,0,0.3); padding: 20px; border-radius: 12px; font-family: monospace; color: var(--text-muted); line-height: 1.5; white-space: pre; overflow-x: auto;">
[Client Traffic]
      │
      ├─► (live_monitor.py / Browser)
      │
      ▼
[FastAPI Ingestion]
      │
      ├─► 16 Flow Features / 14 Context Features
      ▼
[Stage 1: VPN vs Clean]
      │
      ├─► Clean Traffic ────► (Database Log)
      │
      └─► VPN Detected
               │
               ▼
      [Stage 2: Protocol Fingerprint]
               │
               ├─► OpenVPN
               ├─► WireGuard
               └─► IKEv2
               │
               ▼
        [SHAP Explainer]
               │
               ▼
      [Interactive SOC Dashboard]
            </div>
        </div>
    """
    
    full_html = header + body + footer
    with open('frontend/how_it_works.html', 'w', encoding='utf-8') as out:
        out.write(full_html)
    print("Created frontend/how_it_works.html successfully!")
else:
    print("Could not find <div class='doc-container'> in integration.html")
