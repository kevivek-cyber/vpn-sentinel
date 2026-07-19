import os

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VPN-Sentinel | Enterprise SOC Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        :root {
            --bg-color: #03050a;
            --panel-bg: rgba(10, 15, 30, 0.45);
            --sidebar-bg: rgba(6, 9, 18, 0.85);
            --border-color: rgba(255, 255, 255, 0.1);
            --accent-primary: #9d4edd;
            --accent-vpn: #ff2a5f;
            --accent-safe: #00f0ff;
            --text-main: #ffffff;
            --text-muted: #a0aec0;
            --glass-blur: 24px;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Outfit', sans-serif;
            scrollbar-width: thin;
            scrollbar-color: rgba(255, 255, 255, 0.2) transparent;
        }

        body {
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(157, 78, 221, 0.12) 0px, transparent 40%),
                radial-gradient(circle at 85% 30%, rgba(0, 240, 255, 0.12) 0px, transparent 40%),
                radial-gradient(circle at 50% 80%, rgba(255, 42, 95, 0.08) 0px, transparent 40%);
            background-attachment: fixed;
            background-size: 200% 200%;
            animation: bgShift 15s ease infinite;
            color: var(--text-main);
            overflow-x: hidden;
            display: flex;
            height: 100vh;
        }

        @keyframes bgShift {
            0% { background-position: 0% 0%; }
            50% { background-position: 100% 100%; }
            100% { background-position: 0% 0%; }
        }

        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Sidebar Layout */
        .sidebar {
            width: 260px;
            background: var(--sidebar-bg);
            border-right: 1px solid var(--border-color);
            backdrop-filter: blur(var(--glass-blur));
            display: flex;
            flex-direction: column;
            padding: 24px;
            z-index: 100;
        }

        .logo-container {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 40px;
            cursor: pointer;
        }

        .logo-icon {
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-safe));
            box-shadow: 0 0 20px rgba(0, 240, 255, 0.5);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 1.2rem;
            color: white;
        }

        .logo-text {
            display: flex;
            flex-direction: column;
            line-height: 1.1;
            font-size: 1.1rem;
            font-weight: 800;
            letter-spacing: 1px;
        }

        .nav-links {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .nav-links a {
            color: var(--text-muted);
            text-decoration: none;
            font-size: 1rem;
            font-weight: 500;
            padding: 12px 16px;
            border-radius: 12px;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .nav-links a.active {
            background: rgba(157, 78, 221, 0.15);
            color: white;
            border-left: 4px solid var(--accent-primary);
        }

        .nav-links a:hover:not(.active) {
            background: rgba(255, 255, 255, 0.05);
            color: white;
            transform: translateX(5px);
        }

        /* Main Content */
        .main-content {
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
            overflow-x: hidden;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 40px;
            border-bottom: 1px solid var(--border-color);
            background: rgba(11, 15, 25, 0.2);
            backdrop-filter: blur(10px);
            position: sticky;
            top: 0;
            z-index: 50;
        }

        .header-title {
            font-size: 1.4rem;
            font-weight: 600;
        }

        .status-badge {
            background: rgba(0, 240, 255, 0.1);
            color: var(--accent-safe);
            border: 1px solid rgba(0, 240, 255, 0.2);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.15);
        }

        .status-dot {
            width: 10px;
            height: 10px;
            background-color: var(--accent-safe);
            border-radius: 50%;
            animation: pulse 1.5s infinite;
            box-shadow: 0 0 10px var(--accent-safe);
        }

        @keyframes pulse {
            0% { transform: scale(0.9); opacity: 0.6; }
            50% { transform: scale(1.1); opacity: 1; }
            100% { transform: scale(0.9); opacity: 0.6; }
        }

        .dashboard-container {
            padding: 40px;
            max-width: 1800px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 24px;
            width: 100%;
        }

        .glass-panel {
            background: var(--panel-bg);
            border: 1px solid var(--border-color);
            border-top: 1px solid rgba(255,255,255,0.15);
            border-left: 1px solid rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 24px;
            backdrop-filter: blur(var(--glass-blur));
            -webkit-backdrop-filter: blur(var(--glass-blur));
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            animation: fadeUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            opacity: 0;
            transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
        }

        .stat-card {
            grid-column: span 1;
        }

        .stat-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 15px 40px 0 rgba(0, 0, 0, 0.5), 0 0 20px rgba(157, 78, 221, 0.15);
            border-color: rgba(255, 255, 255, 0.3);
        }

        .stat-card:nth-child(1) { animation-delay: 0.1s; }
        .stat-card:nth-child(2) { animation-delay: 0.2s; }
        .stat-card:nth-child(3) { animation-delay: 0.3s; }
        .stat-card:nth-child(4) { animation-delay: 0.4s; }
        .map-container { animation-delay: 0.5s; grid-column: span 2; height: 350px; padding: 0; overflow: hidden; display: flex; flex-direction: column;}
        .chart-container-small { animation-delay: 0.6s; grid-column: span 1; height: 350px;}
        .simulator-panel { animation-delay: 0.7s; grid-column: span 4; }
        .log-panel { animation-delay: 0.8s; grid-column: span 4; }

        .stat-header {
            color: var(--text-muted);
            font-size: 0.95rem;
            font-weight: 500;
            margin-bottom: 12px;
        }

        .stat-value {
            font-size: 2.8rem;
            font-weight: 800;
            margin-bottom: 6px;
            background: linear-gradient(135deg, #ffffff, #a0aec0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .stat-sub {
            font-size: 0.85rem;
            color: var(--text-muted);
        }

        .chart-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 20px;
            color: var(--text-main);
        }

        /* Leaflet Map overrides */
        #threatMap {
            flex-grow: 1;
            width: 100%;
            background: #020617; /* dark water */
        }
        .leaflet-container {
            font-family: 'Outfit', sans-serif;
            background: transparent !important;
        }
        .leaflet-control-attribution {
            display: none;
        }

        /* Simulator Grid */
        .simulator-grid {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 16px;
            margin-top: 20px;
        }

        .sim-btn {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 16px;
            border-radius: 12px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .sim-btn:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        }

        .sim-btn.safe:hover {
            background: rgba(0, 240, 255, 0.15);
            box-shadow: 0 0 20px rgba(0, 240, 255, 0.3);
            border-color: var(--accent-safe);
        }

        .sim-btn.vpn:hover {
            background: rgba(255, 42, 95, 0.15);
            box-shadow: 0 0 20px rgba(255, 42, 95, 0.3);
            border-color: var(--accent-vpn);
        }

        .sim-btn.adv {
            background: linear-gradient(135deg, rgba(255, 42, 95, 0.15), rgba(157, 78, 221, 0.2));
            border: 1px solid rgba(255, 255, 255, 0.2);
            grid-column: span 2;
        }
        
        .sim-btn.adv:hover {
            background: linear-gradient(135deg, rgba(255, 42, 95, 0.3), rgba(157, 78, 221, 0.4));
            box-shadow: 0 0 25px rgba(157, 78, 221, 0.5);
            border-color: var(--accent-primary);
        }

        /* Logs Table */
        .table-wrapper {
            overflow-x: auto;
            margin-top: 16px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            padding: 16px;
            color: var(--text-muted);
            font-size: 0.9rem;
            font-weight: 600;
            border-bottom: 2px solid var(--border-color);
            text-align: left;
        }
        td {
            padding: 16px;
            font-size: 0.95rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        tr:hover td {
            background: rgba(255, 255, 255, 0.03);
        }

        .badge {
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-block;
        }
        .badge.vpn-flag {
            background: rgba(255, 42, 95, 0.15);
            color: var(--accent-vpn);
            border: 1px solid rgba(255, 42, 95, 0.3);
        }
        .badge.safe-flag {
            background: rgba(0, 240, 255, 0.15);
            color: var(--accent-safe);
            border: 1px solid rgba(0, 240, 255, 0.3);
        }
        .badge.adv-flag {
            background: rgba(157, 78, 221, 0.2);
            color: #d8b4fe;
            border: 1px solid rgba(157, 78, 221, 0.4);
            box-shadow: 0 0 10px rgba(157, 78, 221, 0.3);
        }
        
        .threat-score-high { color: var(--accent-vpn); font-weight: bold; }
        .threat-score-low { color: var(--accent-safe); }

        .explain-box {
            font-size: 0.85rem;
            color: var(--text-muted);
            background: rgba(255, 255, 255, 0.03);
            padding: 8px 12px;
            border-radius: 8px;
            border-left: 3px solid var(--accent-primary);
            max-width: 400px;
            line-height: 1.4;
        }

        /* Toast Notifications */
        #toast-container {
            position: fixed;
            bottom: 30px;
            right: 30px;
            display: flex;
            flex-direction: column;
            gap: 15px;
            z-index: 9999;
        }
        
        .toast {
            background: rgba(15, 23, 42, 0.95);
            border-left: 4px solid var(--accent-vpn);
            border-radius: 12px;
            padding: 16px 24px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5), 0 0 20px rgba(255, 42, 95, 0.2);
            backdrop-filter: blur(10px);
            display: flex;
            flex-direction: column;
            gap: 5px;
            transform: translateX(120%);
            animation: slideInToast 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
        }
        
        .toast.fade-out {
            animation: slideOutToast 0.5s ease forwards;
        }

        @keyframes slideInToast {
            to { transform: translateX(0); }
        }
        @keyframes slideOutToast {
            to { transform: translateX(120%); opacity: 0; }
        }
        
        .toast-title { font-weight: 700; color: white; display: flex; align-items: center; gap: 8px;}
        .toast-title .icon { color: var(--accent-vpn); }
        .toast-msg { font-size: 0.9rem; color: var(--text-muted); }

    </style>
</head>
<body>

    <nav class="sidebar">
        <div class="logo-container">
            <div class="logo-icon">VS</div>
            <div class="logo-text">
                <span>VPN</span>
                <span style="color: var(--accent-safe)">SENTINEL</span>
            </div>
        </div>
        
        <div class="nav-links">
            <a href="index.html" class="active">📊 SOC Dashboard</a>
            <a href="live_flow_test.html">🌐 Browser ML Scan</a>
            <a href="ip_checker.html">🛡️ Threat Intel</a>
            <a href="#">⚙️ AI Settings</a>
            <a href="#">📄 Reports</a>
        </div>
        
        <div style="margin-top: auto; padding: 20px; background: rgba(255,255,255,0.03); border-radius: 16px; border: 1px solid var(--border-color);">
            <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 8px;">System Health</p>
            <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden;">
                <div style="width: 95%; height: 100%; background: var(--accent-safe);"></div>
            </div>
            <p style="font-size: 0.8rem; color: white; margin-top: 8px; text-align: right;">95% Optimal</p>
        </div>
    </nav>

    <main class="main-content">
        <header>
            <div class="header-title">Live Traffic Analytics</div>
            <div class="status-badge" id="backend-status">
                <div class="status-dot"></div>
                Connecting to Core...
            </div>
        </header>

        <div class="dashboard-container">

            <div class="glass-panel stat-card">
                <div class="stat-header">Total Handled Connections</div>
                <div class="stat-value" id="card-total">0</div>
                <div class="stat-sub">Live monitored flows</div>
            </div>
            <div class="glass-panel stat-card">
                <div class="stat-header">Active VPN Tunnels</div>
                <div class="stat-value" id="card-vpn" style="background: linear-gradient(135deg, #ff2a5f, #ff7b93); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">0</div>
                <div class="stat-sub" id="card-vpn-ratio">0% tunnel ratio</div>
            </div>
            <div class="glass-panel stat-card">
                <div class="stat-header">Clean Traffic</div>
                <div class="stat-value" id="card-safe" style="background: linear-gradient(135deg, #00f0ff, #8affff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">0</div>
                <div class="stat-sub">Normal web & VoIP activity</div>
            </div>
            <div class="glass-panel stat-card">
                <div class="stat-header">Evasion Attempts</div>
                <div class="stat-value" id="card-adv" style="background: linear-gradient(135deg, #9d4edd, #d8b4fe); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">0</div>
                <div class="stat-sub">Adversarial flows blocked</div>
            </div>

            
            <div class="glass-panel map-container">
                <div class="chart-title" style="padding: 24px 24px 0 24px;">Global Threat Map</div>
                <div id="threatMap"></div>
            </div>

            <div class="glass-panel chart-container-small">
                <div class="chart-title">Time Series Volume</div>
                <div style="position: relative; height: 230px;">
                    <canvas id="timeSeriesChart"></canvas>
                </div>
            </div>
            
            <div class="glass-panel chart-container-small">
                <div class="chart-title">Protocol Distribution</div>
                <div style="position: relative; height: 230px; display: flex; justify-content: center;">
                    <canvas id="pieChart"></canvas>
                </div>
            </div>


            <div class="glass-panel simulator-panel">
                <div class="chart-title" style="margin-bottom: 8px;">Traffic Simulation Console</div>
                <p style="font-size: 0.9rem; color: var(--text-muted);">Simulate real-time packets to trigger ML classifications and SHAP explanations. Threat locations are randomly generated for the map.</p>
                <div class="simulator-grid">
                    <button class="sim-btn safe" onclick="simulateTraffic('web')">Simulate Web Traffic</button>
                    <button class="sim-btn safe" onclick="simulateTraffic('voip')">Simulate VoIP Session</button>
                    <button class="sim-btn vpn" onclick="simulateTraffic('wireguard')">Simulate WireGuard</button>
                    <button class="sim-btn vpn" onclick="simulateTraffic('openvpn')">Simulate OpenVPN</button>
                    <button class="sim-btn adv" onclick="simulateTraffic('adversarial')">⚠️ Launch Adversarial Evasion</button>
                </div>
            </div>

            <div class="glass-panel log-panel">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <div class="chart-title" style="margin: 0;">Real-Time Threat Logs</div>
                    <div>
                        <input type="text" placeholder="Search IP or Protocol..." style="padding: 8px 16px; border-radius: 8px; border: 1px solid var(--border-color); background: rgba(0,0,0,0.3); color: white; outline: none; width: 250px;">
                    </div>
                </div>
                
                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>Timestamp</th>
                                <th>Source IP / Threat Score</th>
                                <th>Flow Profile</th>
                                <th>AI Prediction</th>
                                <th>Confidence</th>
                                <th>SHAP Justification</th>
                            </tr>
                        </thead>
                        <tbody id="log-body">
                            <tr>
                                <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 30px;">
                                    No logs ingested yet. Use the Simulator above.
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

        </div>
    </main>

    <div id="toast-container"></div>

    <script>
        const BACKEND_URL = (window.location.protocol === 'file:' || window.location.origin === 'null')
            ? 'http://127.0.0.1:8000'
            : window.location.origin;
        const API_URL = `${BACKEND_URL}/api`;
        
        let timeSeriesChart = null;
        let pieChart = null;
        let threatMap = null;
        let advCount = 0;

        // Initialize Map
        function initMap() {
            // Dark map tiles (CartoDB Dark Matter)
            threatMap = L.map('threatMap', {zoomControl: false, attributionControl: false}).setView([20, 0], 2);
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                subdomains: 'abcd',
                maxZoom: 20
            }).addTo(threatMap);
        }

        // Add Marker to Map
        function addMapMarker(isVpn, isAdv) {
            if(!threatMap) return;
            const lat = (Math.random() - 0.5) * 140; 
            const lng = (Math.random() - 0.5) * 300;
            
            let color = '#00f0ff'; // safe
            if (isAdv) color = '#9d4edd'; // adv
            else if (isVpn) color = '#ff2a5f'; // vpn
            
            const circle = L.circleMarker([lat, lng], {
                radius: isAdv ? 8 : (isVpn ? 6 : 4),
                fillColor: color,
                color: color,
                weight: 1,
                opacity: 0.8,
                fillOpacity: 0.6
            }).addTo(threatMap);
            
            // Auto remove after 10 seconds to not clutter
            setTimeout(() => {
                threatMap.removeLayer(circle);
            }, 10000);
        }

        function showToast(title, msg) {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.innerHTML = `
                <div class="toast-title"><span class="icon">⚠️</span> ${title}</div>
                <div class="toast-msg">${msg}</div>
            `;
            container.appendChild(toast);
            
            setTimeout(() => {
                toast.classList.add('fade-out');
                setTimeout(() => toast.remove(), 500);
            }, 5000);
        }

        function initCharts() {
            const ctxTS = document.getElementById('timeSeriesChart').getContext('2d');
            timeSeriesChart = new Chart(ctxTS, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        { label: 'Clean', data: [], borderColor: '#00f0ff', tension: 0.3, fill: false },
                        { label: 'VPN', data: [], borderColor: '#ff2a5f', tension: 0.3, fill: false }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#f3f4f6' } } },
                    scales: {
                        x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#a0aec0'} },
                        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#a0aec0'} }
                    }
                }
            });

            const ctxPie = document.getElementById('pieChart').getContext('2d');
            pieChart = new Chart(ctxPie, {
                type: 'doughnut',
                data: {
                    labels: ['OpenVPN', 'WireGuard', 'IKEv2'],
                    datasets: [{
                        data: [0, 0, 0],
                        backgroundColor: ['#ff2a5f', '#00f0ff', '#9d4edd'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { color: '#f3f4f6' } }
                    },
                    cutout: '75%'
                }
            });
        }

        async function checkBackend() {
            try {
                const res = await fetch(`${API_URL}/stats`);
                if (res.ok) {
                    const badge = document.getElementById('backend-status');
                    badge.innerHTML = '<div class="status-dot"></div> Live Monitoring Active';
                    badge.style.color = 'var(--accent-safe)';
                    badge.style.borderColor = 'rgba(0, 240, 255, 0.3)';
                    badge.style.background = 'rgba(0, 240, 255, 0.1)';
                    return true;
                }
            } catch (err) {}
            return false;
        }

        function generateRandomIP() {
            return `${Math.floor(Math.random()*255)}.${Math.floor(Math.random()*255)}.${Math.floor(Math.random()*255)}.${Math.floor(Math.random()*255)}`;
        }
        
        function generateThreatScore(isVpn, isAdv) {
            if (isAdv) return Math.floor(Math.random() * 15) + 85; // 85-99
            if (isVpn) return Math.floor(Math.random() * 30) + 50; // 50-80
            return Math.floor(Math.random() * 20) + 1; // 1-20
        }

        async function fetchStats() {
            if (!(await checkBackend())) return;

            const statsRes = await fetch(`${API_URL}/stats`);
            const stats = await statsRes.json();

            document.getElementById('card-total').innerText = stats.total_connections;
            document.getElementById('card-vpn').innerText = stats.vpn_count;
            document.getElementById('card-safe').innerText = stats.non_vpn_count;
            document.getElementById('card-vpn-ratio').innerText = `${Math.round(stats.vpn_ratio * 100)}% tunnel ratio`;
            document.getElementById('card-adv').innerText = advCount; // Client side tracker for demo

            pieChart.data.datasets[0].data = [
                stats.protocols.OpenVPN || 0,
                stats.protocols.WireGuard || 0,
                stats.protocols.IKEv2 || 0
            ];
            pieChart.update();

            const historyRes = await fetch(`${API_URL}/history`);
            const history = await historyRes.json();

            const tbody = document.getElementById('log-body');
            if (history.length === 0) return;

            const timeLabels = history.slice(0, 10).reverse().map(h => new Date(h.timestamp).toLocaleTimeString());
            const vpnData = history.slice(0, 10).reverse().map((h, i) => history.slice(0, i+1).filter(x => x.is_vpn).length);
            const safeData = history.slice(0, 10).reverse().map((h, i) => history.slice(0, i+1).filter(x => !x.is_vpn).length);

            timeSeriesChart.data.labels = timeLabels;
            timeSeriesChart.data.datasets[0].data = safeData;
            timeSeriesChart.data.datasets[1].data = vpnData;
            timeSeriesChart.update();

            tbody.innerHTML = history.map(log => {
                const dateStr = new Date(log.timestamp).toLocaleTimeString();
                
                // Determine if it was adversarial (High fwd_pkt_len_mean for demo purposes)
                const isAdv = log.fwd_pkt_len_mean > 1000;
                
                let predBadge = `<span class="badge safe-flag">Clean</span>`;
                if (isAdv) predBadge = `<span class="badge adv-flag">Adversarial Attempt</span>`;
                else if (log.is_vpn) predBadge = `<span class="badge vpn-flag">VPN: ${log.vpn_protocol}</span>`;
                
                const threatScore = generateThreatScore(log.is_vpn, isAdv);
                const scoreColor = threatScore > 75 ? 'threat-score-high' : 'threat-score-low';

                return `
                    <tr>
                        <td style="font-weight: 500;">${dateStr}</td>
                        <td style="font-family: monospace;">
                            ${generateRandomIP()}<br>
                            <span class="${scoreColor}">Threat Score: ${threatScore}/100</span>
                        </td>
                        <td style="color: var(--text-muted); font-size: 0.8rem; font-family: monospace;">
                            Dur: ${log.duration.toFixed(2)}s<br>
                            Len: ${log.fwd_pkt_len_mean.toFixed(0)} Fwd / ${log.bwd_pkt_len_mean.toFixed(0)} Bwd
                        </td>
                        <td>${predBadge}</td>
                        <td style="font-weight: 700; color: white;">${(log.confidence * 100).toFixed(1)}%</td>
                        <td>
                            <div class="explain-box">${log.explanation}</div>
                        </td>
                    </tr>
                `;
            }).join('');
        }

        async function simulateTraffic(type) {
            let flowData = {};
            let isAdv = false;

            if (type === 'web') {
                flowData = { duration: 2.5, fwd_pkt_len_mean: 300, bwd_pkt_len_mean: 800, flow_iat_mean: 0.5, flow_iat_std: 0.2, packets_per_sec: 40 };
            } else if (type === 'voip') {
                flowData = { duration: 40, fwd_pkt_len_mean: 120, bwd_pkt_len_mean: 120, flow_iat_mean: 0.02, flow_iat_std: 0.005, packets_per_sec: 100 };
            } else if (type === 'wireguard') {
                flowData = { duration: 15, fwd_pkt_len_mean: 850, bwd_pkt_len_mean: 950, flow_iat_mean: 0.08, flow_iat_std: 0.04, packets_per_sec: 400 };
            } else if (type === 'openvpn') {
                flowData = { duration: 20, fwd_pkt_len_mean: 600, bwd_pkt_len_mean: 700, flow_iat_mean: 0.15, flow_iat_std: 0.1, packets_per_sec: 200 };
            } else if (type === 'adversarial') {
                isAdv = true;
                advCount++;
                showToast("Adversarial Evasion Detected", "High-volume padded traffic packet intercepted matching evasion signatures. Connection dropped.");
                flowData = { duration: 15, fwd_pkt_len_mean: 1200, bwd_pkt_len_mean: 1300, flow_iat_mean: 0.35, flow_iat_std: 0.2, packets_per_sec: 80 };
            }

            // Map Animation
            addMapMarker(type !== 'web' && type !== 'voip', isAdv);

            try {
                const res = await fetch(`${API_URL}/ingest`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(flowData)
                });
                if (res.ok) fetchStats();
            } catch (err) {}
        }

        window.onload = () => {
            initMap();
            initCharts();
            fetchStats();
            setInterval(fetchStats, 3000);
        };
    </script>
</body>
</html>
"""

filepath = r"c:\Users\Vivek\Desktop\vpn sentinel\frontend\index.html"
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(html_content)
