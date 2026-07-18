import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import shap
from adversarial_shaper import apply_evasion


os.makedirs('models', exist_ok=True)


print("Loading datasets...")
train_df = pd.read_csv('data/train_flows.csv')
test_df = pd.read_csv('data/test_flows.csv')
test_adv_df = pd.read_csv('data/test_flows_adversarial.csv')


if os.path.exists('vpn_sentinel_training_data.csv'):
    print("Loading Claude-generated browser dataset from 'vpn_sentinel_training_data.csv'...")
    claude_df = pd.read_csv('vpn_sentinel_training_data.csv')
    from sklearn.model_selection import train_test_split as tts
    train_br_df, test_br_df = tts(claude_df, test_size=0.2, random_state=42, stratify=claude_df['is_vpn'])
else:
    train_br_df = pd.read_csv('data/train_browser_flows.csv')
    test_br_df = pd.read_csv('data/test_browser_flows.csv')


features = [
    'duration', 'fwd_pkt_len_mean', 'bwd_pkt_len_mean',
    'flow_iat_mean', 'flow_iat_std', 'jitter_ratio', 'packets_per_sec', 'bytes_per_sec'
]


print("Creating adversarial training samples to improve robustness (Adversarial Retraining)...")

vpn_train_df = train_df[train_df['is_vpn'] == 1].copy()
adv_vpn_train_df = apply_evasion(vpn_train_df)


train_df_robust = pd.concat([train_df, adv_vpn_train_df], ignore_index=True)


print("\n--- Training Robust Stage 1: VPN vs Non-VPN (250 estimators) ---")
X_train_s1 = train_df_robust[features]
y_train_s1 = train_df_robust['is_vpn']
X_test_s1 = test_df[features]
y_test_s1 = test_df['is_vpn']

clf_s1 = RandomForestClassifier(n_estimators=250, random_state=42, n_jobs=-1)
clf_s1.fit(X_train_s1, y_train_s1)


y_pred_s1 = clf_s1.predict(X_test_s1)
print("Stage 1 Test Classification Report (Clean Data):")
print(classification_report(y_test_s1, y_pred_s1, target_names=['Non-VPN', 'VPN']))


print("\n--- Training Robust Stage 2: Protocol Fingerprinting (250 estimators) ---")

vpn_train_df_robust = train_df_robust[train_df_robust['is_vpn'] == 1]
X_train_s2 = vpn_train_df_robust[features]
y_train_s2 = vpn_train_df_robust['vpn_protocol']

clf_s2 = RandomForestClassifier(n_estimators=250, random_state=42, n_jobs=-1)
clf_s2.fit(X_train_s2, y_train_s2)


vpn_test_df = test_df[test_df['is_vpn'] == 1]
X_test_s2 = vpn_test_df[features]
y_test_s2 = vpn_test_df['vpn_protocol']

y_pred_s2 = clf_s2.predict(X_test_s2)
print("Stage 2 Test Classification Report (Clean Data):")
print(classification_report(y_test_s2, y_pred_s2, target_names=['OpenVPN', 'WireGuard', 'IKEv2']))


print("\n--- Training Browser-Level Classifiers (Timing-only features) ---")
timing_features = [
    'duration', 'flow_iat_mean', 'flow_iat_std', 'jitter_ratio', 'packets_per_sec',
    'webrtc_ip_mismatch', 'webrtc_blocked', 'timezone_mismatch_score', 'language_mismatch_score',
    'geo_ip_distance_km', 'has_geo_permission', 'is_datacenter_ip', 'is_known_vpn_ip', 'proxy_header_detected'
]

def apply_feature_noise(X_df, random_state=42):
    np.random.seed(random_state)
    X_pert = X_df.copy()
    perturb_cols = [
        'is_datacenter_ip', 'is_known_vpn_ip', 'timezone_mismatch_score', 
        'language_mismatch_score', 'webrtc_ip_mismatch', 'webrtc_blocked', 
        'proxy_header_detected'
    ]
    for col in perturb_cols:
        if col in X_pert.columns:
            mask = np.random.rand(len(X_pert)) < 0.3
            X_pert.loc[mask, col] = (1 - X_pert.loc[mask, col]).astype(int)
    return X_pert

X_train_br1 = train_br_df[timing_features].fillna(-1.0)
y_train_br1 = train_br_df['is_vpn']
X_test_br1 = test_br_df[timing_features].fillna(-1.0)
y_test_br1 = test_br_df['is_vpn']

clf_browser_s1 = RandomForestClassifier(n_estimators=250, random_state=42, n_jobs=-1)
X_train_br1_pert = apply_feature_noise(X_train_br1)
clf_browser_s1.fit(X_train_br1_pert, y_train_br1)

y_pred_br1 = clf_browser_s1.predict(X_test_br1)
acc_br1 = accuracy_score(y_test_br1, y_pred_br1)
print(f"Browser Stage 1 Model Accuracy (Multi-Signal): {acc_br1:.4f}")


vpn_train_br_df = train_br_df[train_br_df['is_vpn'] == 1]
X_train_br2 = vpn_train_br_df[timing_features].fillna(-1.0)
y_train_br2 = vpn_train_br_df['vpn_protocol']

vpn_test_br_df = test_br_df[test_br_df['is_vpn'] == 1]
X_test_br2 = vpn_test_br_df[timing_features].fillna(-1.0)
y_test_br2 = vpn_test_br_df['vpn_protocol']

clf_browser_s2 = RandomForestClassifier(n_estimators=250, random_state=42, n_jobs=-1)
X_train_br2_pert = apply_feature_noise(X_train_br2)
clf_browser_s2.fit(X_train_br2_pert, y_train_br2)

y_pred_br2 = clf_browser_s2.predict(X_test_br2)
acc_br2 = accuracy_score(y_test_br2, y_pred_br2)
print(f"Browser Stage 2 Model Accuracy (Multi-Signal): {acc_br2:.4f}")


print("\n--- Evaluating Adversarial Robustness ---")
X_test_adv_s1 = test_adv_df[features]
y_test_adv_s1 = test_adv_df['is_vpn']

y_pred_adv_s1 = clf_s1.predict(X_test_adv_s1)
acc_s1_clean = accuracy_score(y_test_s1, y_pred_s1)
acc_s1_adv = accuracy_score(y_test_adv_s1, y_pred_adv_s1)
print(f"Stage 1 Clean Accuracy: {acc_s1_clean:.4f}")
print(f"Stage 1 Adversarial Accuracy: {acc_s1_adv:.4f} (Drop: {acc_s1_clean - acc_s1_adv:.4f})")


vpn_test_adv_df = test_adv_df[test_adv_df['is_vpn'] == 1]
X_test_adv_s2 = vpn_test_adv_df[features]
y_test_adv_s2 = vpn_test_adv_df['vpn_protocol']

y_pred_adv_s2 = clf_s2.predict(X_test_adv_s2)
acc_s2_clean = accuracy_score(y_test_s2, y_pred_s2)
acc_s2_adv = accuracy_score(y_test_adv_s2, y_pred_adv_s2)
print(f"Stage 2 Clean Accuracy: {acc_s2_clean:.4f}")
print(f"Stage 2 Adversarial Accuracy: {acc_s2_adv:.4f} (Drop: {acc_s2_clean - acc_s2_adv:.4f})")


print("\n--- Integrating SHAP Explainability ---")
explainer_s1 = shap.TreeExplainer(clf_s1)
explainer_s2 = shap.TreeExplainer(clf_s2)


sample_vpn = vpn_test_df.iloc[0:1]
sample_features = sample_vpn[features]

shap_values_s1 = explainer_s1.shap_values(sample_features)
print("Sample SHAP analysis complete for Stage 1.")


joblib.dump(clf_s1, 'models/stage1_model.pkl')
joblib.dump(clf_s2, 'models/stage2_model.pkl')
joblib.dump(clf_browser_s1, 'models/browser_stage1_model.pkl')
joblib.dump(clf_browser_s2, 'models/browser_stage2_model.pkl')
joblib.dump(features, 'models/features.pkl')
joblib.dump(timing_features, 'models/timing_features.pkl')
print("\nModels successfully saved to 'models/' directory.")
