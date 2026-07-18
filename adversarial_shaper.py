import pandas as pd
import numpy as np

def apply_evasion(df, padding_factor=0.2, timing_factor=0.3):
    """
    Applies traffic-shaping perturbations to simulate evasion:
    - Packet Padding: increases mean packet lengths.
    - Timing Randomization: increases flow inter-arrival time and decreases packet rates.
    """
    perturbed_df = df.copy()


    vpn_mask = perturbed_df['is_vpn'] == 1


    fwd_padding = 1.0 + np.random.uniform(0.1, 0.5, size=vpn_mask.sum())
    bwd_padding = 1.0 + np.random.uniform(0.1, 0.5, size=vpn_mask.sum())

    perturbed_df.loc[vpn_mask, 'fwd_pkt_len_mean'] *= fwd_padding
    perturbed_df.loc[vpn_mask, 'bwd_pkt_len_mean'] *= bwd_padding


    timing_delay = 1.0 + np.random.uniform(0.2, 1.0, size=vpn_mask.sum())
    perturbed_df.loc[vpn_mask, 'flow_iat_mean'] *= timing_delay
    perturbed_df.loc[vpn_mask, 'flow_iat_std'] *= timing_delay


    perturbed_df.loc[vpn_mask, 'packets_per_sec'] /= timing_delay


    perturbed_df['bytes_per_sec'] = perturbed_df['packets_per_sec'] * (perturbed_df['fwd_pkt_len_mean'] + perturbed_df['bwd_pkt_len_mean'])

    return perturbed_df

if __name__ == '__main__':
    print("Loading test data...")
    try:
        test_df = pd.read_csv('data/test_flows.csv')
        perturbed_df = apply_evasion(test_df)
        perturbed_df.to_csv('data/test_flows_adversarial.csv', index=False)
        print("Generated adversarial test dataset at data/test_flows_adversarial.csv")
    except FileNotFoundError:
        print("Error: data/test_flows.csv not found. Please run data_generator.py first.")
