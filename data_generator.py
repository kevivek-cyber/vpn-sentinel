import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split


np.random.seed(42)

def generate_flows(num_samples=5000):
    """
    Generates synthetic flow-level statistics for network traffic.
    """
    data = []

    for _ in range(num_samples):
        is_vpn = np.random.choice([0, 1], p=[0.6, 0.4])
        protocol = -1

        if is_vpn == 0:
            traffic_type = np.random.choice(['web', 'streaming', 'voip'])
            if traffic_type == 'web':
                duration = np.random.exponential(scale=5.0) + 0.1
                fwd_pkt_len_mean = np.random.normal(loc=300, scale=100)
                bwd_pkt_len_mean = np.random.normal(loc=800, scale=300)
                flow_iat_mean = np.random.normal(loc=0.5, scale=0.2)
                flow_iat_std = np.random.normal(loc=0.08, scale=0.03)
                packets_per_sec = np.random.normal(loc=50, scale=20)
            elif traffic_type == 'streaming':
                duration = np.random.exponential(scale=30.0) + 5.0
                fwd_pkt_len_mean = np.random.normal(loc=1200, scale=150)
                bwd_pkt_len_mean = np.random.normal(loc=1400, scale=50)
                flow_iat_mean = np.random.normal(loc=0.05, scale=0.01)
                flow_iat_std = np.random.normal(loc=0.008, scale=0.002)
                packets_per_sec = np.random.normal(loc=800, scale=150)
            else:
                duration = np.random.normal(loc=45.0, scale=15.0)
                fwd_pkt_len_mean = np.random.normal(loc=120, scale=20)
                bwd_pkt_len_mean = np.random.normal(loc=120, scale=20)
                flow_iat_mean = np.random.normal(loc=0.02, scale=0.002)
                flow_iat_std = np.random.normal(loc=0.003, scale=0.001)
                packets_per_sec = np.random.normal(loc=100, scale=10)
        else:
            protocol = np.random.choice([0, 1, 2], p=[0.4, 0.4, 0.2])
            if protocol == 0:
                duration = np.random.exponential(scale=20.0) + 2.0
                fwd_pkt_len_mean = np.random.normal(loc=600, scale=150)
                bwd_pkt_len_mean = np.random.normal(loc=700, scale=150)
                flow_iat_mean = np.random.normal(loc=0.15, scale=0.05)
                flow_iat_std = np.random.normal(loc=0.18, scale=0.05)
                packets_per_sec = np.random.normal(loc=200, scale=50)
            elif protocol == 1:
                duration = np.random.exponential(scale=15.0) + 1.0
                fwd_pkt_len_mean = np.random.normal(loc=850, scale=50)
                bwd_pkt_len_mean = np.random.normal(loc=950, scale=50)
                flow_iat_mean = np.random.normal(loc=0.08, scale=0.02)
                flow_iat_std = np.random.normal(loc=0.09, scale=0.02)
                packets_per_sec = np.random.normal(loc=400, scale=80)
            else:
                duration = np.random.exponential(scale=25.0) + 5.0
                fwd_pkt_len_mean = np.random.normal(loc=500, scale=100)
                bwd_pkt_len_mean = np.random.normal(loc=600, scale=100)
                flow_iat_mean = np.random.normal(loc=0.25, scale=0.08)
                flow_iat_std = np.random.normal(loc=0.28, scale=0.08)
                packets_per_sec = np.random.normal(loc=120, scale=30)

        duration = max(0.01, duration)
        fwd_pkt_len_mean = max(40, fwd_pkt_len_mean)
        bwd_pkt_len_mean = max(40, bwd_pkt_len_mean)
        flow_iat_mean = max(0.001, flow_iat_mean)
        flow_iat_std = max(0.0005, flow_iat_std)
        packets_per_sec = max(1.0, packets_per_sec)

        bytes_per_sec = packets_per_sec * (fwd_pkt_len_mean + bwd_pkt_len_mean)
        jitter_ratio = flow_iat_std / flow_iat_mean

        data.append({
            'duration': duration,
            'fwd_pkt_len_mean': fwd_pkt_len_mean,
            'bwd_pkt_len_mean': bwd_pkt_len_mean,
            'flow_iat_mean': flow_iat_mean,
            'flow_iat_std': flow_iat_std,
            'jitter_ratio': jitter_ratio,
            'packets_per_sec': packets_per_sec,
            'bytes_per_sec': bytes_per_sec,
            'is_vpn': is_vpn,
            'vpn_protocol': protocol
        })

    df = pd.DataFrame(data)
    return df

def generate_browser_flows(num_samples=5000):
    """
    Generates realistic browser-level HTTP ping test characteristics and multi-signal metadata.
    """
    data = []

    for _ in range(num_samples):
        is_vpn = np.random.choice([0, 1], p=[0.5, 0.5])
        protocol = -1

        if is_vpn == 0:

            flow_iat_mean = np.random.uniform(0.005, 0.150)
            jitter_ratio = np.random.uniform(0.05, 1.45)
            flow_iat_std = flow_iat_mean * jitter_ratio
            duration = np.random.normal(loc=2.0, scale=0.5)


            webrtc_blocked = np.random.choice([0, 1], p=[0.95, 0.05])
            webrtc_ip_mismatch = 0
            timezone_mismatch_score = 0
            language_mismatch_score = 0
            has_geo_permission = np.random.choice([0, 1], p=[0.60, 0.40])
            if has_geo_permission == 1:
                geo_ip_distance_km = max(0.0, np.random.normal(loc=15.0, scale=10.0))
            else:
                geo_ip_distance_km = np.nan
            is_datacenter_ip = 0
            is_known_vpn_ip = 0
            proxy_header_detected = 0
        else:

            protocol = np.random.choice([0, 1, 2], p=[0.4, 0.4, 0.2])
            flow_iat_mean = np.random.uniform(0.005, 0.350)
            jitter_ratio = np.random.uniform(0.50, 2.50)
            flow_iat_std = flow_iat_mean * jitter_ratio

            if protocol == 0:
                duration = np.random.normal(loc=2.2, scale=0.3)
            elif protocol == 1:
                duration = np.random.normal(loc=1.8, scale=0.2)
            else:
                duration = np.random.normal(loc=2.6, scale=0.4)


            webrtc_blocked = np.random.choice([0, 1], p=[0.60, 0.40])
            if webrtc_blocked == 1:
                webrtc_ip_mismatch = 0
            else:
                webrtc_ip_mismatch = np.random.choice([0, 1], p=[0.30, 0.70])

            timezone_mismatch_score = np.random.choice([0, 1], p=[0.20, 0.80])
            language_mismatch_score = np.random.choice([0, 1], p=[0.30, 0.70])
            has_geo_permission = np.random.choice([0, 1], p=[0.70, 0.30])
            if has_geo_permission == 1:
                geo_ip_distance_km = max(50.0, np.random.normal(loc=1500.0, scale=800.0))
            else:
                geo_ip_distance_km = np.nan

            is_datacenter_ip = np.random.choice([0, 1], p=[0.15, 0.85])
            is_known_vpn_ip = np.random.choice([0, 1], p=[0.25, 0.75])
            proxy_header_detected = np.random.choice([0, 1], p=[0.80, 0.20])

        duration = max(0.2, duration)
        flow_iat_mean = max(0.001, flow_iat_mean)
        flow_iat_std = max(0.0005, flow_iat_std)
        packets_per_sec = 15.0 / duration

        data.append({
            'duration': duration,
            'fwd_pkt_len_mean': 350.0,
            'bwd_pkt_len_mean': 200.0,
            'flow_iat_mean': flow_iat_mean,
            'flow_iat_std': flow_iat_std,
            'jitter_ratio': jitter_ratio,
            'packets_per_sec': packets_per_sec,
            'bytes_per_sec': packets_per_sec * 550.0,
            'webrtc_ip_mismatch': webrtc_ip_mismatch,
            'webrtc_blocked': webrtc_blocked,
            'timezone_mismatch_score': timezone_mismatch_score,
            'language_mismatch_score': language_mismatch_score,
            'geo_ip_distance_km': geo_ip_distance_km,
            'has_geo_permission': has_geo_permission,
            'is_datacenter_ip': is_datacenter_ip,
            'is_known_vpn_ip': is_known_vpn_ip,
            'proxy_header_detected': proxy_header_detected,
            'is_vpn': is_vpn,
            'vpn_protocol': protocol
        })

    df = pd.DataFrame(data)
    return df

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    print("Generating simulated network flows...")
    df = generate_flows(30000)
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['is_vpn'])
    train_df.to_csv('data/train_flows.csv', index=False)
    test_df.to_csv('data/test_flows.csv', index=False)

    print("Generating browser-level latency flow datasets...")
    df_br = generate_browser_flows(15000)
    train_br, test_br = train_test_split(df_br, test_size=0.2, random_state=42, stratify=df_br['is_vpn'])
    train_br.to_csv('data/train_browser_flows.csv', index=False)
    test_br.to_csv('data/test_browser_flows.csv', index=False)


    df_br.to_csv('vpn_sentinel_training_data.csv', index=False)

    print("Data generation complete.")
