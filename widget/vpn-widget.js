(function() {

    const css = `
        .vpn-sentinel-badge {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(17, 24, 39, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 12px 18px;
            color: #f3f4f6;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 0 15px rgba(59, 130, 246, 0.2);
            backdrop-filter: blur(10px);
            z-index: 999999;
            transition: all 0.3s ease;
            width: 250px;
        }

        .vpn-sentinel-badge:hover {
            transform: translateY(-2px);
            border-color: rgba(255, 255, 255, 0.2);
        }

        .vpn-sentinel-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }

        .vpn-sentinel-title {
            font-weight: 700;
            font-size: 0.85rem;
            letter-spacing: 0.5px;
            color: #9ca3af;
            text-transform: uppercase;
        }

        .vpn-sentinel-indicator {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.75rem;
            color: #10b981;
        }

        .vpn-sentinel-dot {
            width: 7px;
            height: 7px;
            background-color: #10b981;
            border-radius: 50%;
            display: inline-block;
        }

        .vpn-sentinel-dot.alert {
            background-color: #ef4444;
            box-shadow: 0 0 8px #ef4444;
        }

        .vpn-sentinel-counter {
            font-size: 1.8rem;
            font-weight: 800;
            margin: 4px 0;
            display: flex;
            align-items: baseline;
            gap: 4px;
        }

        .vpn-sentinel-counter span {
            font-size: 0.8rem;
            color: #9ca3af;
            font-weight: 400;
        }

        .vpn-sentinel-detail {
            font-size: 0.75rem;
            color: #9ca3af;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            margin-top: 8px;
            padding-top: 8px;
            display: flex;
            justify-content: space-between;
        }
    `;


    const style = document.createElement('style');
    style.innerHTML = css;
    document.head.appendChild(style);


    const container = document.createElement('div');
    container.className = 'vpn-sentinel-badge';
    container.innerHTML = `
        <div class="vpn-sentinel-header">
            <span class="vpn-sentinel-title">VPN-Sentinel Widget</span>
            <span class="vpn-sentinel-indicator" id="vsw-status">
                <span class="vpn-sentinel-dot"></span>Active
            </span>
        </div>
        <div class="vpn-sentinel-counter">
            <span id="vsw-tunnels">0</span>
            <span>Active Tunnels</span>
        </div>
        <div class="vpn-sentinel-detail">
            <span>OpenVPN/WG/IKEv2:</span>
            <span id="vsw-breakdown">0/0/0</span>
        </div>
    `;
    document.body.appendChild(container);


    const API_URL = "http://127.0.0.1:8000/api/stats";

    async function updateWidget() {
        try {
            const res = await fetch(API_URL);
            if (!res.ok) throw new Error("Offline");

            const stats = await res.json();

            const tunnelsCount = stats.vpn_count;
            document.getElementById('vsw-tunnels').innerText = tunnelsCount;

            const breakdown = `${stats.protocols.OpenVPN || 0}/${stats.protocols.WireGuard || 0}/${stats.protocols.IKEv2 || 0}`;
            document.getElementById('vsw-breakdown').innerText = breakdown;

            const statusIndicator = document.getElementById('vsw-status');
            if (tunnelsCount > 0) {
                statusIndicator.innerHTML = '<span class="vpn-sentinel-dot alert"></span>ALERT';
                statusIndicator.style.color = '#ef4444';
            } else {
                statusIndicator.innerHTML = '<span class="vpn-sentinel-dot"></span>Secure';
                statusIndicator.style.color = '#10b981';
            }
        } catch (e) {
            const statusIndicator = document.getElementById('vsw-status');
            statusIndicator.innerHTML = '<span class="vpn-sentinel-dot" style="background-color:#6b7280;"></span>Offline';
            statusIndicator.style.color = '#6b7280';
        }
    }


    updateWidget();
    setInterval(updateWidget, 4000);
})();
