import joblib
import pandas as pd
import numpy as np
model_br_s1 = joblib.load('models/browser_stage1_model.pkl')
timing_features = joblib.load('models/timing_features.pkl')
print("=== Evaluating Model on Held-Out Hard Cases ===")
print(f"Model timing features used: {timing_features}\n")
def make_case(data):
    row = {
        'webrtc_ip_mismatch': 0,
        'webrtc_blocked': 0,
        'timezone_mismatch_score': 0,
        'language_mismatch_score': 0,
        'geo_ip_distance_km': np.nan,
        'has_geo_permission': 0,
        'is_datacenter_ip': 0,
        'is_known_vpn_ip': 0,
        'proxy_header_detected': 0
    }
    row.update(data)
    if 'timezone_mismatch' in row:
        row['timezone_mismatch_score'] = row.pop('timezone_mismatch')
    return pd.DataFrame([row])[timing_features].fillna(-1.0)
case_a = make_case({
    'duration': 1.2,
    'flow_iat_mean': 0.040,
    'flow_iat_std': 0.008,
    'jitter_ratio': 0.2,
    'packets_per_sec': 12.5,
    'timezone_mismatch': 0
})
case_b = make_case({
    'duration': 1.42,
    'flow_iat_mean': 0.019,
    'flow_iat_std': 0.035,
    'jitter_ratio': 1.84,
    'packets_per_sec': 10.5,
    'timezone_mismatch': 1
})
pred_a = model_br_s1.predict(case_a)[0]
prob_a = model_br_s1.predict_proba(case_a)[0]
verdict_a = "VPN" if pred_a == 1 else "Clean"
conf_a = prob_a[1] if pred_a == 1 else prob_a[0]
pred_b = model_br_s1.predict(case_b)[0]
prob_b = model_br_s1.predict_proba(case_b)[0]
verdict_b = "VPN" if pred_b == 1 else "Clean"
conf_b = prob_b[1] if pred_b == 1 else prob_b[0]
print(f"Hard Case A (Clean Hotspot - 40ms, 0.2 Jitter Ratio):")
print(f"  -> Predicted class: {pred_a} ({verdict_a})")
print(f"  -> Confidence: {conf_a * 100:.2f}%")
print(f"  -> Expected: 0 (Clean)\n")
print(f"Hard Case B (Fast VPN - 19ms, 1.84 Jitter Ratio):")
print(f"  -> Predicted class: {pred_b} ({verdict_b})")
print(f"  -> Confidence: {conf_b * 100:.2f}%")
print(f"  -> Expected: 1 (VPN)\n")
if pred_a == 0 and pred_b == 1:
    print("SUCCESS: The model successfully decoupled speed from stability and correctly classified both hard cases!")
else:
    print("FAILURE: The model failed to correctly classify the hard cases.")
