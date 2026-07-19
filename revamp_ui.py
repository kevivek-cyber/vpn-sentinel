import os

filepath = r"c:\Users\Vivek\Desktop\vpn sentinel\frontend\index.html"
with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace root variables
old_root = """        :root {
            --bg-color: #0b0f19;
            --panel-bg: rgba(17, 24, 39, 0.7);
            --border-color: rgba(255, 255, 255, 0.08);
            --accent-primary: #3b82f6;
            --accent-vpn: #ef4444;
            --accent-safe: #10b981;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --glass-blur: 16px;
        }"""
new_root = """        :root {
            --bg-color: #03050a;
            --panel-bg: rgba(10, 15, 30, 0.45);
            --border-color: rgba(255, 255, 255, 0.1);
            --accent-primary: #9d4edd;
            --accent-vpn: #ff2a5f;
            --accent-safe: #00f0ff;
            --text-main: #ffffff;
            --text-muted: #a0aec0;
            --glass-blur: 24px;
        }"""
html = html.replace(old_root, new_root)

# Replace body styles
old_body = """        body {
            background-color: var(--bg-color);
            background-image:
                radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(239, 68, 68, 0.1) 0px, transparent 50%);
            color: var(--text-main);
            min-height: 100vh;
            overflow-x: hidden;
        }"""
new_body = """        body {
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(157, 78, 221, 0.12) 0px, transparent 40%),
                radial-gradient(circle at 85% 30%, rgba(0, 240, 255, 0.12) 0px, transparent 40%),
                radial-gradient(circle at 50% 80%, rgba(255, 42, 95, 0.08) 0px, transparent 40%);
            background-attachment: fixed;
            background-size: 200% 200%;
            animation: bgShift 15s ease infinite;
            color: var(--text-main);
            min-height: 100vh;
            overflow-x: hidden;
        }

        @keyframes bgShift {
            0% { background-position: 0% 0%; }
            50% { background-position: 100% 100%; }
            100% { background-position: 0% 0%; }
        }

        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }"""
html = html.replace(old_body, new_body)

# Replace logo background
old_logo = "background: linear-gradient(135deg, var(--accent-primary), var(--accent-vpn));"
new_logo = "background: linear-gradient(135deg, var(--accent-primary), var(--accent-safe)); box-shadow: 0 0 20px rgba(0, 240, 255, 0.5);"
html = html.replace(old_logo, new_logo)

# Replace stat card styles
old_stat_card = """        .stat-card {
            grid-column: span 1;
            background: var(--panel-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            backdrop-filter: blur(var(--glass-blur));
            transition: transform 0.2s ease, border-color 0.2s ease;
        }

        .stat-card:hover {
            transform: translateY(-4px);
            border-color: rgba(255, 255, 255, 0.15);
        }"""
new_stat_card = """        .stat-card, .chart-container-large, .chart-container-small, .simulator-panel, .log-panel {
            animation: fadeUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            opacity: 0;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        
        .stat-card:nth-child(1) { animation-delay: 0.1s; }
        .stat-card:nth-child(2) { animation-delay: 0.2s; }
        .stat-card:nth-child(3) { animation-delay: 0.3s; }
        .stat-card:nth-child(4) { animation-delay: 0.4s; }
        .chart-container-large { animation-delay: 0.5s; }
        .chart-container-small { animation-delay: 0.6s; }
        .simulator-panel { animation-delay: 0.7s; }
        .log-panel { animation-delay: 0.8s; }

        .stat-card {
            grid-column: span 1;
            background: var(--panel-bg);
            border: 1px solid var(--border-color);
            border-top: 1px solid rgba(255,255,255,0.15);
            border-left: 1px solid rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 24px;
            backdrop-filter: blur(var(--glass-blur));
            -webkit-backdrop-filter: blur(var(--glass-blur));
            transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.3s ease, border-color 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 15px 40px 0 rgba(0, 0, 0, 0.5), 0 0 20px rgba(157, 78, 221, 0.15);
            border-color: rgba(255, 255, 255, 0.3);
        }"""
html = html.replace(old_stat_card, new_stat_card)

# Replace stat value gradient
old_stat_value = """        .stat-value {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 6px;
        }"""
new_stat_value = """        .stat-value {
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 6px;
            background: linear-gradient(135deg, #ffffff, #a0aec0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }"""
html = html.replace(old_stat_value, new_stat_value)

# Update Chart containers borders
old_chart_borders = "border: 1px solid var(--border-color);"
new_chart_borders = "border: 1px solid var(--border-color); border-top: 1px solid rgba(255,255,255,0.15); border-left: 1px solid rgba(255,255,255,0.1);"
html = html.replace(old_chart_borders, new_chart_borders)

# Add hover effects to sim buttons
old_sim_btn = """        .sim-btn:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateY(-2px);
        }"""
new_sim_btn = """        .sim-btn:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }"""
html = html.replace(old_sim_btn, new_sim_btn)

# Vibrant hover for vpn button
old_sim_vpn_hover = """        .sim-btn.vpn:hover {
            background: rgba(239, 68, 68, 0.15);
        }"""
new_sim_vpn_hover = """        .sim-btn.vpn:hover {
            background: rgba(255, 42, 95, 0.2);
            box-shadow: 0 0 15px rgba(255, 42, 95, 0.4);
            border-color: var(--accent-vpn);
        }"""
html = html.replace(old_sim_vpn_hover, new_sim_vpn_hover)

# Vibrant hover for safe button
old_sim_safe_hover = """        .sim-btn.safe:hover {
            background: rgba(16, 185, 129, 0.15);
        }"""
new_sim_safe_hover = """        .sim-btn.safe:hover {
            background: rgba(0, 240, 255, 0.2);
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.4);
            border-color: var(--accent-safe);
        }"""
html = html.replace(old_sim_safe_hover, new_sim_safe_hover)

# Vibrant hover for adv button
old_sim_adv = """        .sim-btn.adv {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(59, 130, 246, 0.2));
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .sim-btn.adv:hover {
            filter: brightness(1.2);
        }"""
new_sim_adv = """        .sim-btn.adv {
            background: linear-gradient(135deg, rgba(255, 42, 95, 0.2), rgba(157, 78, 221, 0.3));
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        .sim-btn.adv:hover {
            background: linear-gradient(135deg, rgba(255, 42, 95, 0.4), rgba(157, 78, 221, 0.5));
            box-shadow: 0 0 20px rgba(157, 78, 221, 0.6);
            transform: translateY(-3px);
        }"""
html = html.replace(old_sim_adv, new_sim_adv)

# Update chartjs colors in javascript
html = html.replace("borderColor: '#10b981'", "borderColor: '#00f0ff'") # safe
html = html.replace("borderColor: '#ef4444'", "borderColor: '#ff2a5f'") # vpn
html = html.replace("backgroundColor: ['#ef4444', '#3b82f6', '#a855f7']", "backgroundColor: ['#ff2a5f', '#00f0ff', '#9d4edd']")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(html)
