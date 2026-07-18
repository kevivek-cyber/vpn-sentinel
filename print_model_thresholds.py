import joblib
import numpy as np

model = joblib.load('models/browser_stage1_model.pkl')
features = joblib.load('models/timing_features.pkl')

print("=== Inspection of Decision Trees in Random Forest ===")
print(f"Features: {features}")


importances = model.feature_importances_
for f, imp in zip(features, importances):
    print(f"  Feature '{f}': Importance = {imp:.4f}")


def make_case(data):
    import pandas as pd
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
    return pd.DataFrame([row])[features].fillna(-1.0)



print("\n--- Scanning is_vpn boundary across Jitter Ratio values ---")
for jit in [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.6, 0.8, 1.0, 1.5, 2.0]:
    sample = make_case({
        'duration': 1.2,
        'flow_iat_mean': 0.030,
        'flow_iat_std': 0.030 * jit,
        'jitter_ratio': jit,
        'packets_per_sec': 12.5
    })
    pred = model.predict(sample)[0]
    prob = model.predict_proba(sample)[0]
    print(f"  Jitter Ratio: {jit:.2f} -> Class: {pred} (Clean Prob: {prob[0]:.2f}, VPN Prob: {prob[1]:.2f})")
