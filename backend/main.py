import os
import re
import time
from collections import defaultdict, deque
import joblib
import numpy as np
import pandas as pd
import shap
from fastapi import FastAPI, Depends, HTTPException, Header, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import List, Optional
from .database import init_db, get_db, FlowInferenceLog
init_db()
STAGE1_PATH = "models/stage1_model.pkl"
STAGE2_PATH = "models/stage2_model.pkl"
BROWSER_STAGE1_PATH = "models/browser_stage1_model.pkl"
BROWSER_STAGE2_PATH = "models/browser_stage2_model.pkl"
FEATURES_PATH = "models/features.pkl"
TIMING_FEATURES_PATH = "models/timing_features.pkl"
if not (os.path.exists(STAGE1_PATH) and os.path.exists(STAGE2_PATH) and os.path.exists(FEATURES_PATH)):
    raise RuntimeError("Models not trained. Please run train_models.py first.")
model_s1 = joblib.load(STAGE1_PATH)
model_s2 = joblib.load(STAGE2_PATH)
features = joblib.load(FEATURES_PATH)
explainer_s1 = shap.TreeExplainer(model_s1)
explainer_s2 = shap.TreeExplainer(model_s2)
model_br_s1 = joblib.load(BROWSER_STAGE1_PATH)
model_br_s2 = joblib.load(BROWSER_STAGE2_PATH)
timing_features = joblib.load(TIMING_FEATURES_PATH)
explainer_br_s1 = shap.TreeExplainer(model_br_s1)
explainer_br_s2 = shap.TreeExplainer(model_br_s2)
app = FastAPI(title="VPN-Sentinel Inference API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
import urllib.request
import json
from fastapi import Request
from math import radians, cos, sin, asin, sqrt
DATACENTER_KEYWORDS = [
    "digitalocean", "m247", "linode", "ovh", "hetzner", "colocrossing", "choopa",
    "clouvider", "leaseweb", "private internet access", "nordvpn", "expressvpn",
    "surfshark", "windscribe", "vpn", "proxy", "tor", "exit-node", "datacenter",
    "hosting", "vps", "hostkey", "aws", "azure", "google cloud", "google-cloud",
    "amazon web services", "microsoft corporation", "ovh SAS", "scaleway", "vultr",
    "obfuscated", "hide my ass", "hidemyass"
]
# Only these indicate an actual anonymising service. The broader datacenter list
# above just means "hosted infrastructure", which is not the same thing.
VPN_KEYWORDS = [
    "vpn", "proxy", "tor", "exit-node", "nordvpn", "expressvpn", "surfshark",
    "private internet access", "windscribe", "hide my ass", "hidemyass",
]
# Short keywords like "tor"/"vps"/"aws" appear inside ordinary words -- "tor" alone
# matches "opera(tor)", "distribu(tor)", "vic(tor)ia" -- which flagged plenty of
# legitimate residential ISPs. Match those on word boundaries; longer keywords are
# distinctive enough for plain substring matching.
def _keyword_matches(keyword: str, text: str) -> bool:
    kw = keyword.lower()
    if len(kw) <= 4:
        return re.search(rf"\b{re.escape(kw)}\b", text) is not None
    return kw in text
# Connections classified as VPN that run longer than this are flagged as a
# Time Limit Exceeded (TLE) policy violation -- e.g. a tunnel that's stayed
# open well past what's expected for the traffic pattern being analyzed.
VPN_TLE_THRESHOLD_SECONDS = 30

# Simple in-memory sliding-window rate limiter for /api/ingest. Good enough for
# a single-process demo deployment; a multi-worker/multi-instance deployment
# would need a shared store (e.g. Redis) instead.
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 30
_rate_limit_buckets: dict = defaultdict(deque)

def enforce_rate_limit(client_key: str):
    now = time.time()
    bucket = _rate_limit_buckets[client_key]
    while bucket and now - bucket[0] > RATE_LIMIT_WINDOW_SECONDS:
        bucket.popleft()
    if len(bucket) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: max {RATE_LIMIT_MAX_REQUESTS} requests per {RATE_LIMIT_WINDOW_SECONDS}s."
        )
    bucket.append(now)

def is_private_ip(ip: Optional[str]) -> bool:
    if not ip:
        return True
    ip = ip.strip()
    return (ip in ("127.0.0.1", "localhost", "::1") or
            ip.startswith("192.168.") or
            ip.startswith("192.0.0.") or
            ip.startswith("10.") or
            ip.startswith("172.16.") or
            ip.startswith("fe80:"))
def get_ip_info(ip: str):
    if is_private_ip(ip):
        return {
            "status": "success",
            "countryCode": "US",
            "country": "United States",
            "city": "N/A (Private IP)",
            "regionName": "",
            "timezone": "America/New_York",
            "lat": 40.7128,
            "lon": -74.0060,
            "isp": "Local ISP",
            "org": "Local Org",
            "as": "AS12345 Local ASN",
            "is_vpn": False,
            "is_datacenter": False,
            "is_tor": False,
            "is_proxy": False
        }
    try:
        url = f"https://api.ipapi.is/?q={ip}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if "location" in data:
                loc = data["location"]
                asn_info = data.get("asn", {})
                return {
                    "status": "success",
                    "countryCode": loc.get("country_code"),
                    "country": loc.get("country"),
                    "city": loc.get("city"),
                    "regionName": loc.get("state"),
                    "timezone": loc.get("timezone"),
                    "lat": loc.get("latitude"),
                    "lon": loc.get("longitude"),
                    "isp": asn_info.get("descr", "Unknown ISP"),
                    "org": data.get("company", {}).get("name", "Unknown Org"),
                    "as": f"AS{asn_info.get('asn')} {asn_info.get('descr')}" if asn_info.get("asn") else "Unknown ASN",
                    "is_vpn": data.get("is_vpn", False),
                    "is_datacenter": data.get("is_datacenter", False),
                    "is_tor": data.get("is_tor", False),
                    "is_proxy": data.get("is_proxy", False)
                }
    except Exception as e:
        print(f"Error calling ipapi.is: {e}")
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,timezone,lat,lon,isp,org,as,query"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if data.get("status") == "success":
                data["is_vpn"] = False
                data["is_datacenter"] = False
                data["is_tor"] = False
                data["is_proxy"] = False
                return data
    except Exception as e:
        print(f"Error calling ip-api: {e}")
    return {
        "status": "fail",
        "countryCode": "US",
        "country": "United States",
        "city": "Unknown",
        "regionName": "",
        "timezone": "America/New_York",
        "lat": 40.7128,
        "lon": -74.0060,
        "isp": "Fallback ISP",
        "org": "Fallback Org",
        "as": "AS00000 Fallback ASN",
        "is_vpn": False,
        "is_datacenter": False,
        "is_tor": False,
        "is_proxy": False
    }
def assess_ip_reputation(ip: str):
    """Looks up an IP and combines the upstream is_vpn/is_datacenter/is_tor/is_proxy
    flags with our own ISP/org/ASN keyword matching, since the ip-api.com fallback
    path never sets those flags itself."""
    http_info = get_ip_info(ip)
    is_datacenter_ip = 1 if http_info.get("is_datacenter") else 0
    is_known_vpn_ip = 1 if (http_info.get("is_vpn") or http_info.get("is_tor") or http_info.get("is_proxy")) else 0
    rep_text = f"{http_info.get('isp', '')} {http_info.get('org', '')} {http_info.get('as', '')}".lower()
    if any(_keyword_matches(kw, rep_text) for kw in DATACENTER_KEYWORDS):
        is_datacenter_ip = 1
    if any(_keyword_matches(kw, rep_text) for kw in VPN_KEYWORDS):
        is_known_vpn_ip = 1
    return http_info, is_datacenter_ip, is_known_vpn_ip

@app.on_event("startup")
def warm_up_ip_lookup():
    # Cold DNS resolution + TLS handshake on the first real request can exceed
    # the lookup timeout, silently falling back to a "clean" IP profile and
    # misclassifying that first request. Prime the resolver/connection here so
    # the first user-facing request isn't the one paying that cost.
    try:
        get_ip_info("1.1.1.1")
    except Exception as e:
        print(f"[startup] IP reputation warm-up failed (non-fatal): {e}")
class FlowInput(BaseModel):
    duration: float = Field(..., example=12.4)
    fwd_pkt_len_mean: float = Field(..., example=850.0)
    bwd_pkt_len_mean: float = Field(..., example=950.0)
    flow_iat_mean: float = Field(..., example=0.08)
    flow_iat_std: float = Field(..., example=0.04)
    packets_per_sec: float = Field(..., example=400.0)
    fwd_pkt_len_max: Optional[float] = Field(default=-1.0, example=1200.0)
    fwd_pkt_len_min: Optional[float] = Field(default=-1.0, example=0.0)
    bwd_pkt_len_max: Optional[float] = Field(default=-1.0, example=1400.0)
    bwd_pkt_len_min: Optional[float] = Field(default=-1.0, example=0.0)
    fwd_pkt_len_std: Optional[float] = Field(default=-1.0, example=250.0)
    bwd_pkt_len_std: Optional[float] = Field(default=-1.0, example=300.0)
    flow_iat_max: Optional[float] = Field(default=-1.0, example=1.2)
    flow_iat_min: Optional[float] = Field(default=-1.0, example=0.0)
    is_browser: bool = Field(default=False, description="Use timing-only model suitable for browser measurements")
    client_ip: Optional[str] = Field(default=None, description="Client IP address")
    webrtc_ip: Optional[str] = Field(default=None, description="WebRTC revealed IP")
    timezone: Optional[str] = Field(default=None, description="Client timezone")
    language: Optional[str] = Field(default=None, description="Client primary language")
    languages: Optional[List[str]] = Field(default=None, description="Client languages list")
    latitude: Optional[float] = Field(default=None, description="Client latitude")
    longitude: Optional[float] = Field(default=None, description="Client longitude")
    has_geo_permission: bool = Field(default=False, description="Whether GPS permission was granted")
    is_virtual_gpu: bool = Field(default=False, description="Whether WebGL reports a software/virtual renderer (datacenter VM signal)")
    is_automation_flagged: bool = Field(default=False, description="Whether navigator.webdriver is set (headless/automation signal)")
    low_font_count: bool = Field(default=False, description="Whether the client has an unusually small installed-font count (VM/headless signal)")
def is_timezone_mismatch(tz_client: Optional[str], tz_ip: Optional[str]) -> int:
    if not tz_client or not tz_ip:
        return 0
    tz_c = tz_client.lower().strip()
    tz_i = tz_ip.lower().strip()
    aliases = {
        "asia/calcutta": "asia/kolkata",
        "asia/saigon": "asia/ho_chi_minh",
        "asia/katmandu": "asia/kathmandu",
        "europe/kiev": "europe/kyiv",
        "america/godthab": "america/nuuk"
    }
    tz_c_norm = aliases.get(tz_c, tz_c)
    tz_i_norm = aliases.get(tz_i, tz_i)
    if tz_c_norm == tz_i_norm:
        return 0
    try:
        from zoneinfo import ZoneInfo
        from datetime import datetime
        now = datetime.now()
        offset_c = now.astimezone(ZoneInfo(tz_client)).utcoffset()
        offset_i = now.astimezone(ZoneInfo(tz_ip)).utcoffset()
        if offset_c == offset_i:
            return 0
    except Exception:
        pass
    return 1

def get_tenant_id(tenant: Optional[str] = Query(None), x_tenant_id: Optional[str] = Header(None)) -> str:
    return tenant or x_tenant_id or "default"

class IngestResponse(BaseModel):
    is_vpn: bool
    vpn_protocol: Optional[str]
    confidence: float
    explanation: str
    is_tle: bool = False
@app.post("/api/ingest", response_model=IngestResponse)
def ingest_flow(flow: FlowInput, request: Request, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    rate_limit_key = request.client.host if request.client else "unknown"
    enforce_rate_limit(rate_limit_key)
    bytes_per_sec = flow.packets_per_sec * (flow.fwd_pkt_len_mean + flow.bwd_pkt_len_mean)
    jitter_ratio = flow.flow_iat_std / flow.flow_iat_mean if flow.flow_iat_mean > 0 else 0.0
    client_ip = flow.client_ip
    if not client_ip:
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            client_ip = x_forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "127.0.0.1"
    proxy_header_detected = 0
    host_header = request.headers.get("host", "").lower()
    is_dev_tunnel = any(dom in host_header for dom in ["lhr.life", "localhost.run", "pinggy", "ngrok", "localtunnel"])
    if not is_dev_tunnel:
        for header_name in ["via", "forwarded", "x-forwarded-for", "x-real-ip"]:
            if request.headers.get(header_name):
                proxy_header_detected = 1
                break
    http_info, is_datacenter_ip, is_known_vpn_ip = assess_ip_reputation(client_ip)
    webrtc_blocked = 1 if (not flow.webrtc_ip or is_private_ip(flow.webrtc_ip)) else 0
    webrtc_ip_mismatch = 0
    if not webrtc_blocked:
        webrtc_info = get_ip_info(flow.webrtc_ip)
        if not webrtc_info.get("countryCode"):
            webrtc_blocked = 1
    if not webrtc_blocked:
        as_http = http_info.get("as", "").split()[0] if http_info.get("as") else ""
        as_webrtc = webrtc_info.get("as", "").split()[0] if webrtc_info.get("as") else ""
        print(f"[DEBUG] client_ip: {client_ip}")
        print(f"[DEBUG] flow.webrtc_ip: {flow.webrtc_ip}")
        print(f"[DEBUG] as_http: {as_http} | as_webrtc: {as_webrtc}")
        print(f"[DEBUG] countryCode_http: {http_info.get('countryCode')} | countryCode_webrtc: {webrtc_info.get('countryCode')}")
        if as_http and as_webrtc and as_http != as_webrtc:
            webrtc_ip_mismatch = 1
        elif http_info.get("countryCode") != webrtc_info.get("countryCode"):
            webrtc_ip_mismatch = 1
    timezone_mismatch_score = is_timezone_mismatch(flow.timezone, http_info.get("timezone"))
    language_mismatch_score = 0
    if flow.language and http_info.get("countryCode"):
        country_lang_map = {
            "US": ["en"], "GB": ["en"], "CA": ["en", "fr"], "AU": ["en"], "NZ": ["en"],
            "DE": ["de"], "AT": ["de"], "CH": ["de", "fr", "it"], "FR": ["fr"], "BE": ["nl", "fr", "de"],
            "NL": ["nl"], "ES": ["es"], "MX": ["es"], "AR": ["es"], "CO": ["es"],
            "IT": ["it"], "IN": ["hi", "en", "ta", "te", "ml", "kn", "gu", "mr", "bn", "pa", "ur"],
            "BR": ["pt"], "PT": ["pt"], "RU": ["ru"], "UA": ["uk", "ru"], "PL": ["pl"],
            "TR": ["tr"], "JP": ["ja"], "KR": ["ko"], "CN": ["zh"], "TW": ["zh"],
            "HK": ["zh", "en"], "SG": ["en", "zh", "ms", "ta"], "ZA": ["en", "af"]
        }
        country = http_info.get("countryCode").upper()
        browser_lang = flow.language.split("-")[0].lower()
        if country in country_lang_map:
            if browser_lang not in country_lang_map[country]:
                language_mismatch_score = 1
    geo_ip_distance_km = None
    if flow.has_geo_permission and flow.latitude is not None and flow.longitude is not None:
        ip_lat = http_info.get("lat")
        ip_lon = http_info.get("lon")
        if ip_lat is not None and ip_lon is not None:
            lon1, lat1, lon2, lat2 = map(radians, [flow.longitude, flow.latitude, ip_lon, ip_lat])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            geo_ip_distance_km = c * 6371.0
    flow_dict = flow.dict()
    flow_dict['bytes_per_sec'] = bytes_per_sec
    flow_dict['jitter_ratio'] = jitter_ratio
    flow_dict['webrtc_ip_mismatch'] = webrtc_ip_mismatch
    flow_dict['webrtc_blocked'] = webrtc_blocked
    flow_dict['timezone_mismatch_score'] = timezone_mismatch_score
    flow_dict['language_mismatch_score'] = language_mismatch_score
    flow_dict['geo_ip_distance_km'] = geo_ip_distance_km if geo_ip_distance_km is not None else np.nan
    flow_dict['has_geo_permission'] = 1 if flow.has_geo_permission else 0
    flow_dict['is_datacenter_ip'] = is_datacenter_ip
    flow_dict['is_known_vpn_ip'] = is_known_vpn_ip
    flow_dict['proxy_header_detected'] = proxy_header_detected
    flow_dict['is_virtual_gpu'] = 1 if flow.is_virtual_gpu else 0
    flow_dict['is_automation_flagged'] = 1 if flow.is_automation_flagged else 0
    flow_dict['low_font_count'] = 1 if flow.low_font_count else 0
    if flow.is_browser:
        active_features = timing_features
        active_model_s1 = model_br_s1
        active_model_s2 = model_br_s2
        active_explainer_s1 = explainer_br_s1
        active_explainer_s2 = explainer_br_s2
    else:
        active_features = features
        active_model_s1 = model_s1
        active_model_s2 = model_s2
        active_explainer_s1 = explainer_s1
        active_explainer_s2 = explainer_s2
    input_df = pd.DataFrame([flow_dict])[active_features]
    input_df_imputed = input_df.fillna(-1.0)
    prob_s1 = active_model_s1.predict_proba(input_df_imputed)[0]
    is_vpn_pred = bool(active_model_s1.predict(input_df_imputed)[0])
    confidence = float(prob_s1[1] if is_vpn_pred else prob_s1[0])
    vpn_proto = None
    explanation_str = ""
    shap_vals_s1 = active_explainer_s1.shap_values(input_df_imputed)
    if isinstance(shap_vals_s1, list):
        class_idx = 1 if is_vpn_pred else 0
        vals = shap_vals_s1[class_idx][0]
    else:
        if len(shap_vals_s1.shape) == 3:
            class_idx = 1 if is_vpn_pred else 0
            vals = shap_vals_s1[0, :, class_idx]
        else:
            vals = shap_vals_s1[0]
    feature_importance = list(zip(active_features, vals))
    feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
    top_feature, top_val = feature_importance[0]
    direction = "increased" if top_val > 0 else "decreased"
    explanation_str = f"Flow classified as {'VPN' if is_vpn_pred else 'Non-VPN'} primarily because feature '{top_feature}' {direction} the prediction confidence."
    if is_vpn_pred:
        prob_s2 = active_model_s2.predict_proba(input_df_imputed)[0]
        proto_idx = int(active_model_s2.predict(input_df_imputed)[0])
        protocols_map = {0: "OpenVPN", 1: "WireGuard", 2: "IKEv2"}
        vpn_proto = protocols_map.get(proto_idx, "Unknown")
        confidence = float(prob_s2[proto_idx])
        shap_vals_s2 = active_explainer_s2.shap_values(input_df_imputed)
        if isinstance(shap_vals_s2, list):
            vals_s2 = shap_vals_s2[proto_idx][0]
        else:
            if len(shap_vals_s2.shape) == 3:
                vals_s2 = shap_vals_s2[0, :, proto_idx]
            else:
                vals_s2 = shap_vals_s2[0]
        feature_importance_s2 = list(zip(active_features, vals_s2))
        feature_importance_s2.sort(key=lambda x: abs(x[1]), reverse=True)
        top_feature_s2, top_val_s2 = feature_importance_s2[0]
        direction_s2 = "higher" if top_val_s2 > 0 else "lower"
        explanation_str += f" Protocol identified as {vpn_proto} due to {direction_s2} value of '{top_feature_s2}'."
    is_tle = bool(is_vpn_pred and flow.duration > VPN_TLE_THRESHOLD_SECONDS)
    if is_tle:
        explanation_str += f" TLE: VPN session duration ({flow.duration:.1f}s) exceeded the {VPN_TLE_THRESHOLD_SECONDS}s policy limit."
    log_entry = FlowInferenceLog(
        tenant_id=tenant_id,
        duration=flow.duration,
        fwd_pkt_len_mean=flow.fwd_pkt_len_mean,
        bwd_pkt_len_mean=flow.bwd_pkt_len_mean,
        flow_iat_mean=flow.flow_iat_mean,
        flow_iat_std=flow.flow_iat_std,
        packets_per_sec=flow.packets_per_sec,
        bytes_per_sec=bytes_per_sec,
        is_vpn=is_vpn_pred,
        vpn_protocol=vpn_proto,
        confidence=confidence,
        explanation=explanation_str,
        webrtc_ip_mismatch=webrtc_ip_mismatch,
        webrtc_blocked=webrtc_blocked,
        timezone_mismatch_score=timezone_mismatch_score,
        language_mismatch_score=language_mismatch_score,
        geo_ip_distance_km=geo_ip_distance_km,
        has_geo_permission=1 if flow.has_geo_permission else 0,
        is_datacenter_ip=is_datacenter_ip,
        is_known_vpn_ip=is_known_vpn_ip,
        proxy_header_detected=proxy_header_detected,
        is_virtual_gpu=1 if flow.is_virtual_gpu else 0,
        is_automation_flagged=1 if flow.is_automation_flagged else 0,
        low_font_count=1 if flow.low_font_count else 0,
        is_tle=1 if is_tle else 0
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return IngestResponse(
        is_vpn=is_vpn_pred,
        vpn_protocol=vpn_proto,
        confidence=confidence,
        explanation=explanation_str,
        is_tle=is_tle
    )
@app.get("/api/lookup")
def lookup_ip(request: Request, ip: Optional[str] = Query(None)):
    # ip-api.com's free tier is HTTP-only; calling it directly from the browser
    # on an HTTPS-served page gets blocked as mixed content ("Failed to fetch").
    # Routing through the backend avoids that entirely since server-to-server
    # HTTP calls aren't subject to the browser's mixed-content policy.
    rate_limit_key = request.client.host if request.client else "unknown"
    enforce_rate_limit(rate_limit_key)

    target_ip = (ip or "").strip()
    if not target_ip:
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            target_ip = x_forwarded_for.split(",")[0].strip()
        else:
            target_ip = request.client.host if request.client else ""

    if not target_ip:
        raise HTTPException(status_code=400, detail="Could not determine an IP address to look up.")

    http_info, is_datacenter_ip, is_known_vpn_ip = assess_ip_reputation(target_ip)
    is_vpn = bool(is_datacenter_ip or is_known_vpn_ip or http_info.get("is_tor") or http_info.get("is_proxy"))

    return {
        "status": http_info.get("status", "fail"),
        "query": target_ip,
        "country": http_info.get("country"),
        "countryCode": http_info.get("countryCode"),
        "regionName": http_info.get("regionName"),
        "city": http_info.get("city"),
        "isp": http_info.get("isp"),
        "org": http_info.get("org"),
        "as": http_info.get("as"),
        "is_vpn": is_vpn,
        "is_datacenter": bool(is_datacenter_ip),
        "is_tor": bool(http_info.get("is_tor")),
        "is_proxy": bool(http_info.get("is_proxy"))
    }
@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    logs = db.query(FlowInferenceLog).filter(FlowInferenceLog.tenant_id == tenant_id).all()
    total = len(logs)
    if total == 0:
        return {
            "total_connections": 0,
            "vpn_count": 0,
            "non_vpn_count": 0,
            "vpn_ratio": 0.0,
            "protocols": {"OpenVPN": 0, "WireGuard": 0, "IKEv2": 0}
        }
    vpn_count = sum(1 for log in logs if log.is_vpn)
    non_vpn_count = total - vpn_count
    protocols = {"OpenVPN": 0, "WireGuard": 0, "IKEv2": 0}
    for log in logs:
        if log.is_vpn and log.vpn_protocol in protocols:
            protocols[log.vpn_protocol] += 1
    return {
        "total_connections": total,
        "vpn_count": vpn_count,
        "non_vpn_count": non_vpn_count,
        "vpn_ratio": round(vpn_count / total, 4),
        "protocols": protocols
    }
@app.get("/api/history")
def get_history(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    logs = db.query(FlowInferenceLog).filter(FlowInferenceLog.tenant_id == tenant_id).order_by(FlowInferenceLog.timestamp.desc()).limit(100).all()
    return [
        {
            "id": log.id,
            "timestamp": log.timestamp.isoformat(),
            "duration": log.duration,
            "fwd_pkt_len_mean": log.fwd_pkt_len_mean,
            "bwd_pkt_len_mean": log.bwd_pkt_len_mean,
            "flow_iat_mean": log.flow_iat_mean,
            "flow_iat_std": log.flow_iat_std,
            "packets_per_sec": log.packets_per_sec,
            "bytes_per_sec": log.bytes_per_sec,
            "is_vpn": log.is_vpn,
            "vpn_protocol": log.vpn_protocol,
            "confidence": round(log.confidence, 4),
            "explanation": log.explanation,
            "is_tle": bool(log.is_tle)
        } for log in logs
    ]
@app.get("/", response_class=HTMLResponse)
def read_dashboard():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/scan", response_class=HTMLResponse)
def read_scan():
    with open("frontend/live_flow_test.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/ip", response_class=HTMLResponse)
def read_ip():
    with open("frontend/ip_checker.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/docs", response_class=HTMLResponse)
def read_docs():
    with open("frontend/integration.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/how", response_class=HTMLResponse)
def read_how():
    with open("frontend/how_it_works.html", "r", encoding="utf-8") as f:
        return f.read()

app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
