# 🛡️ VPN Sentinel

**Detects VPN and proxy usage in real time — from raw network traffic or straight from a browser — and explains *why* it flagged something, not just that it did.**

![Security](https://img.shields.io/badge/Security-VPN_Sentinel-4f7cff?style=for-the-badge&logo=shield)
![Python](https://img.shields.io/badge/Python-3.11+-4f7cff?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-2dd4a7?style=for-the-badge&logo=fastapi)

**🌐 Live demo:** [vpncheck.in](https://vpncheck.in) &nbsp;•&nbsp; **📓 Full walkthrough notebook:** [`VPN_Sentinel_Main.ipynb`](VPN_Sentinel_Main.ipynb)

---

## 🧭 What is this?

Most VPN detectors just check an IP against a blocklist — easy for any half-decent VPN to evade. VPN Sentinel combines that with *behavioral* signals that are much harder to fake: how packets are timed, whether a browser's WebRTC leaks its real IP, whether the GPU looks like a cloud VM instead of a real laptop, whether the browser is being driven by automation. It's a two-stage ML pipeline:

- **Stage 1** — is this traffic VPN or clean? (Random Forest, trained on real packet captures + synthetic data, resistant to adversarial evasion)
- **Stage 2** — if it's a VPN, which protocol? (OpenVPN, WireGuard, or IKEv2)
- **Explainability** — every prediction ships with a SHAP breakdown of exactly which feature drove the decision, in plain language

There are two parallel models depending on what data is available: a **Flow Model** for raw network packet statistics, and a **Browser Model** for client-side telemetry when you only have a web request to work with.

### Why this is more than "prompted an LLM to build an app"

The interesting part isn't the feature list — it's the bugs that surfaced from actually stress-testing the pipeline end-to-end, not just eyeballing a demo:
- The model claimed adversarial robustness in its docs, but Stage 1 had never actually been trained on adversarial examples — only Stage 2 had. Fixed and verified (adversarial accuracy went from a real ~40-57% collapse to 98%).
- Stage 1 and Stage 2 were trained on two datasets with incompatible feature scales, so they silently disagreed about what "VPN" looks like — every demo button on the dashboard was misclassified as a result. Fixed by aligning both training sets.
- A cold-start network timeout was silently misclassifying the first request after every server restart, because a slow DNS lookup was falling back to a "clean" default under time pressure.

---

## ⚙️ How It Works: Step-by-Step

VPN Sentinel relies on a highly robust **Multi-Stage Inference Pipeline**. Depending on the data source, traffic is routed through either our **Flow Model** (for raw network packets) or our **Browser Model** (for web application traffic).

### 1️⃣ Traffic Interception & Feature Extraction
The system captures traffic using a live packet sniffer (`project/ml/live_monitor.py`) or receives browser-level telemetry via our REST API. It extracts complex features while disregarding payloads (protecting user privacy):
- **Flow Statistics:** Packet Inter-Arrival Time (IAT) mean, variance, jitter ratios, and packet length distributions.
- **Browser Context:** WebRTC IP leaks, timezone/language conflicts, connection timing patterns, WebGL GPU fingerprint, and HTTP proxy headers.

### 2️⃣ Stage 1: Anomaly Detection (VPN vs. Non-VPN)
The extracted features are fed into our **Stage 1 Random Forest Classifier**. 
- The model evaluates 16 flow features or 17 browser signals to determine if the traffic originates from a VPN/Proxy or a standard residential ISP.
- Trained against adversarial traffic-shaping (packet padding & timing delays), ensuring high evasion resistance.

### 3️⃣ Stage 2: Protocol Fingerprinting
If Stage 1 flags the traffic as a VPN, it is immediately passed to the **Stage 2 Protocol Fingerprinter**.
- The model classifies the exact tunneling protocol used: **OpenVPN, WireGuard, or IKEv2**.
- This enables granular security policies (e.g., allowing corporate IPSec while blocking consumer WireGuard).

### 4️⃣ SHAP Explainability & Alerting
VPN Sentinel doesn't just block traffic—it explains *why*. 
- A SHAP (SHapley Additive exPlanations) TreeExplainer analyzes the model's decision path.
- It outputs exactly which features (e.g., `fwd_pkt_len_std` or `webrtc_ip_mismatch`) contributed most to the VPN classification.

---

## 📊 System Architecture Visualized

```mermaid
graph TD
    %% Core Inputs
    Client([Client Traffic]) --> Sniffer[live_monitor.py / Browser]
    Sniffer --> |16 Flow Features| API[FastAPI Ingestion]
    Sniffer --> |17 Context Features| API
    
    %% Processing
    API --> |Feature Validation| Imputer{Missing Data Imputation}
    Imputer --> Stage1[Stage 1: VPN vs Clean]
    
    %% Stage 1 Logic
    Stage1 -->|Clean Traffic| DB[(Database Log)]
    Stage1 -->|VPN Detected| Stage2[Stage 2: Protocol Fingerprint]
    
    %% Stage 2 Logic
    Stage2 --> OpenVPN(OpenVPN)
    Stage2 --> WireGuard(WireGuard)
    Stage2 --> IKEv2(IKEv2)
    
    %% Explainability
    OpenVPN --> SHAP[SHAP Explainer]
    WireGuard --> SHAP
    IKEv2 --> SHAP
    
    SHAP --> |Confidence & Explanations| DB
    
    %% Output
    DB --> Dashboard[[Interactive SOC Dashboard]]
    
    %% Styling
    classDef api fill:#2dd4a7,stroke:#fff,stroke-width:2px,color:#000;
    classDef model fill:#4f7cff,stroke:#fff,stroke-width:2px,color:#fff;
    classDef db fill:#ef4a5a,stroke:#fff,stroke-width:2px,color:#fff;
    classDef dash fill:#f0a83c,stroke:#fff,stroke-width:2px,color:#000;
    
    class API api;
    class Stage1,Stage2,SHAP model;
    class DB db;
    class Dashboard dash;
```

---

## 🧠 Model Features Breakdown

Our models are trained on highly specific dimensions to prevent overfitting and guarantee accuracy.

| Model Type | Features Used | Key Data Points |
| :--- | :--- | :--- |
| **Flow Model** | 16 Features | `duration`, `packets_per_sec`, Packet length constraints (min/max/std), IAT constraints (min/max/std), `jitter_ratio` |
| **Browser Model** | 17 Features | Timing basics + `webrtc_blocked`, `timezone_mismatch_score`, `language_mismatch_score`, `is_datacenter_ip`, `is_virtual_gpu`, `is_automation_flagged`, `low_font_count` |

---

## 🚀 Key Capabilities

- **Adversarial Robustness:** Resists traffic shaping, packet padding, and evasion tools.
- **Real-Time SOC Dashboard:** Live frontend mapping global threats and traffic logs, responsive on desktop and mobile.
- **Protocol Deep-Dive:** Distinguishes between modern UDP/TCP VPN protocols seamlessly.
- **No-Payload Inspection:** 100% privacy-compliant; we never decrypt or inspect packet payloads (Deep Packet Inspection is not required).
- **TLE Policy Enforcement:** VPN sessions that run past a configurable duration threshold (default 30s) are flagged as a Time Limit Exceeded policy violation.
- **Rate Limiting:** `/api/ingest` is capped per-client to prevent abuse of the inference pipeline.

---

## 📁 Project Structure

```
.
├── README.md
├── VPN_Sentinel_Main.ipynb        # 📓 Full analysis walkthrough — start here
└── project/                       # The application itself
    ├── backend/                   #   FastAPI inference API
    │   ├── main.py                #     routes, feature extraction, model serving
    │   └── database.py            #     SQLAlchemy models + migrations
    ├── frontend/                  #   Dashboard, browser scan, threat intel, docs
    ├── ml/                        #   Training pipeline
    │   ├── train_models.py        #     trains + exports all four models
    │   ├── data_generator.py      #     synthetic dataset generation
    │   ├── adversarial_shaper.py  #     traffic-shaping evasion simulation
    │   └── live_monitor.py        #     live packet sniffer
    ├── models/                    #   Trained .pkl artifacts + feature lists
    ├── notebooks/                 #   Supporting/earlier analysis notebooks
    ├── widget/                    #   Embeddable third-party widget
    ├── Dockerfile
    └── requirements.txt
```

---

## 🛠️ Getting Started

Run these from inside the **`project/`** directory:

```bash
cd project
```

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Train the models:**
   ```bash
   python ml/train_models.py
   ```
3. **Start the API server:**
   ```bash
   uvicorn backend.main:app --reload
   ```
4. **Access the dashboard:** open `http://localhost:8000/` in your browser.

Optionally, to capture live network traffic (requires Admin/root):
```bash
python ml/live_monitor.py
```

The walkthrough notebook lives at the repo root and resolves paths into
`project/` automatically, so run Jupyter from the root:
```bash
jupyter notebook VPN_Sentinel_Main.ipynb
```

> **Deploying:** the app is not at the repository root, so set your platform's
> root/base directory to `project` (on Render: *Settings → Build & Deploy →
> Root Directory*). The start command itself stays `uvicorn backend.main:app`.
