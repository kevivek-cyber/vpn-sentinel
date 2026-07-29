# 🚀 LinkedIn Share Kit: VPN Sentinel / VPNCheck

This file contains the complete copy and asset guide for promoting your project on LinkedIn. Open this in your editor, copy the text, and follow the image attachment guide.

---

## 📷 Image Assets to Attach
Before posting, make sure to upload the **three generated dark-mode images** located in your project folder:
1. `performance_summary.png` (Accuracies & Robustness stats)
2. `flow_importance.png` (Top 10 raw packet timing features)
3. `browser_importance.png` (14 browser telemetry signals)

![Performance Summary](file:///c:/Users/Vivek/Desktop/vpn%20sentinel/performance_summary.png)
![Flow Importance](file:///c:/Users/Vivek/Desktop/vpn%20sentinel/flow_importance.png)
![Browser Importance](file:///c:/Users/Vivek/Desktop/vpn%20sentinel/browser_importance.png)

---

## 📝 LinkedIn Post Copy (Copy and Paste)

🚀 **Excited to share my latest cybersecurity project: VPN Sentinel — an AI-powered Network Security & VPN Detection engine!**

Commercial VPNs and proxies are widely used to bypass geo-restrictions, mask automated bots, or hide fraudulent activity. Traditional detection relies on IP blacklists, which are easily bypassed by dynamic IPs and residential proxies.

To solve this, I built **VPN Sentinel** (now live at `vpncheck.in` 🌐), which shifts the focus from "who the IP is" to "how the connection behaves".

Here is how the multi-stage machine learning system works:

🛡️ **1. Dual-Channel Analysis:**
* **Network Flow Channel:** Sniffs low-level packet timings (Inter-Arrival Times, packet length standard deviations, and jitter ratios) using `live_monitor.py` for routing infrastructure.
* **Browser Telemetry Channel:** Analyzes high-level environmental mismatches (WebRTC IP leaks, timezone contradictions, and HTTP proxy headers) for web applications.

🧠 **2. The 6-Model Pipeline:**
Rather than relying on one classifier, the pipeline uses 4 Random Forest classifiers and 2 SHAP explainers:
* **Stage 1 (VPN Detector):** Achieves **97.1% accuracy** on network flows and **99.67% accuracy** on browser telemetry to detect tunnels.
* **Stage 2 (Protocol Fingerprinter):** Identifies the exact protocol (**WireGuard** at 100% accuracy, **OpenVPN** at 95%, or **IKEv2** at 91%).
* **SHAP Explainability Layer:** Interprets the models' decision trees in real-time, outputting exactly *why* a connection was flagged.

💻 **3. Defensive Adversarial Robustness:**
* To resist traffic-shaping (packet padding or latency spoofing), I built an **Adversarial Shaper** that trains the models against delay-shifting noise, keeping protocol fingerprinting highly secure (**92.67% adversarial accuracy**).

📊 **4. Glassmorphism SOC Dashboard & Widget:**
* Built a responsive dark-mode dashboard featuring a real-time **Leaflet.js** map plotting threats globally, along with dynamic statistics.
* Created a lightweight JavaScript widget (`vpn-widget.js`) that embeds into any site to poll stats and trigger alerts instantly.

**Tech Stack:**
* Python | FastAPI | SQLAlchemy | SQLite | Uvicorn
* Scikit-Learn | SHAP | Pandas | NumPy
* HTML5 | CSS Grid & Flexbox | Leaflet.js | Chart.js

🔗 Check out the project here: [Insert Your GitHub Link]
🌐 Try the live site: https://vpncheck.in

(I've attached the feature importances and performance charts generated directly from the model training runs!)

I'd love to hear your thoughts on this? How are you handling VPN/proxy detection in your systems? 

#cybersecurity #machinelearning #python #fastapi #networksecurity #datascience #webdevelopment #infosec #ai

---

## 💡 Quick Tips for Posting:
* **GitHub Link:** Replace `[Insert Your GitHub Link]` with your real repository URL.
* **Algorithm Booster:** LinkedIn ranks posts higher if the links are placed in the **first comment** instead of the main text. You can change the links section to: `(Links to GitHub and the live site are in the comments below! 👇)` and post them as the first comment.
