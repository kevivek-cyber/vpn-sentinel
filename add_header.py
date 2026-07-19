import json
with open('VPN_Sentinel_Main.ipynb', 'r', encoding='utf-8') as f:
    d = json.load(f)
new_cell = {
    'cell_type': 'markdown',
    'metadata': {},
    'source': [
        '<div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; border: 2px solid #3498db; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);">\n',
        '  <h1 style="color: #2c3e50; text-align: center; font-family: \'Segoe UI\', Tahoma, Geneva, Verdana, sans-serif;">🛡️ VPN-Sentinel: Advanced Network Traffic Classification</h1>\n',
        '  <hr style="border-top: 2px solid #3498db; width: 60%;">\n',
        '  <h3 style="color: #34495e; font-family: \'Segoe UI\', Tahoma, Geneva, Verdana, sans-serif;"><b>Project Overview</b></h3>\n',
        '  <p style="font-size: 16px; color: #333; line-height: 1.6;">\n',
        '    This notebook provides a comprehensive end-to-end machine learning pipeline for detecting and classifying Virtual Private Network (VPN) traffic vs. Non-VPN traffic. The analysis encompasses everything from deep exploratory data analysis (EDA), data cleaning, and feature selection to robust model evaluation.\n',
        '  </p>\n',
        '  <br>\n',
        '  <h3 style="color: #34495e; font-family: \'Segoe UI\', Tahoma, Geneva, Verdana, sans-serif;"><b>Core Machine Learning Models Evaluated:</b></h3>\n',
        '  <ul style="font-size: 16px; color: #333; line-height: 1.8;">\n',
        '    <li>🌳 <b>Decision Tree Classifier</b></li>\n',
        '    <li>📊 <b>Gaussian Naive Bayes</b></li>\n',
        '    <li>🌲 <b>Random Forest Classifier</b></li>\n',
        '    <li>🚀 <b>AdaBoost Classifier</b></li>\n',
        '  </ul>\n',
        '  <br>\n',
        '  <p style="font-size: 14px; color: #7f8c8d; font-style: italic; text-align: center;">\n',
        '    *This notebook integrates historical data preprocessing insights alongside comprehensive multi-model ROC Curve and Confusion Matrix comparisons.*\n',
        '  </p>\n',
        '</div>'
    ]
}
d['cells'].insert(0, new_cell)
with open('VPN_Sentinel_Main.ipynb', 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=1)
