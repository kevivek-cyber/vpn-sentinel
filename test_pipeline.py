import unittest
import os
import joblib
import pandas as pd

class TestVPNSentinelPipeline(unittest.TestCase):

    def setUp(self):

        self.stage1_path = "models/stage1_model.pkl"
        self.stage2_path = "models/stage2_model.pkl"
        self.features_path = "models/features.pkl"


        self.assertTrue(os.path.exists(self.stage1_path), "Stage 1 model pickle missing")
        self.assertTrue(os.path.exists(self.stage2_path), "Stage 2 model pickle missing")
        self.assertTrue(os.path.exists(self.features_path), "Features pickle missing")

        self.model_s1 = joblib.load(self.stage1_path)
        self.model_s2 = joblib.load(self.stage2_path)
        self.features = joblib.load(self.features_path)

    def test_model_inputs(self):

        self.assertEqual(len(self.features), 8)
        self.assertIn('duration', self.features)
        self.assertIn('fwd_pkt_len_mean', self.features)
        self.assertIn('packets_per_sec', self.features)

    def test_stage1_prediction(self):

        flow_iat_mean = 0.6
        flow_iat_std = 0.08
        web_flow = pd.DataFrame([{
            'duration': 5.2,
            'fwd_pkt_len_mean': 280.0,
            'bwd_pkt_len_mean': 750.0,
            'flow_iat_mean': flow_iat_mean,
            'flow_iat_std': flow_iat_std,
            'jitter_ratio': flow_iat_std / flow_iat_mean,
            'packets_per_sec': 45.0,
            'bytes_per_sec': 45.0 * (280.0 + 750.0)
        }])[self.features]

        pred_s1 = self.model_s1.predict(web_flow)[0]

        self.assertEqual(pred_s1, 0, "Web flow incorrectly classified as VPN")

    def test_stage2_prediction(self):

        flow_iat_mean = 0.08
        flow_iat_std = 0.04
        wg_flow = pd.DataFrame([{
            'duration': 14.8,
            'fwd_pkt_len_mean': 855.0,
            'bwd_pkt_len_mean': 945.0,
            'flow_iat_mean': flow_iat_mean,
            'flow_iat_std': flow_iat_std,
            'jitter_ratio': flow_iat_std / flow_iat_mean,
            'packets_per_sec': 400.0,
            'bytes_per_sec': 400.0 * (855.0 + 945.0)
        }])[self.features]

        pred_s1 = self.model_s1.predict(wg_flow)[0]
        self.assertEqual(pred_s1, 1, "WireGuard flow not detected as VPN")

        pred_s2 = self.model_s2.predict(wg_flow)[0]

        self.assertEqual(pred_s2, 1, "VPN protocol not fingerprinted as WireGuard")

if __name__ == '__main__':
    unittest.main()
