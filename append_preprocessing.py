import json
with open('VPN_Sentinel_Main.ipynb', 'r', encoding='utf-8') as f:
    d = json.load(f)
new_cells = [
    {
        'cell_type': 'markdown',
        'metadata': {},
        'source': [
            '## 9. Appendix: Real-World Dataset Preprocessing\n',
            'This section details the historical data preprocessing, cleaning, and scaling applied to our real-world packet capture dataset (`vpn-non_vpn new data.csv`).'
        ]
    },
    {
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': [
            '# Read CSV data file\n',
            'import pandas as pd\n',
            'raw_data = pd.read_csv("vpn-non_vpn new data.csv")\n',
            'raw_data.head()'
        ]
    },
    {
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': ['raw_data.info()']
    },
    {
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': ['raw_data.describe()']
    },
    {
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': [
            '# Class Distribution\n',
            'import matplotlib.pyplot as plt\n',
            'classes = raw_data[\'Label\'].value_counts()\n',
            'classes.plot(kind = \'bar\',rot = 0, color=[\'
            'plt.title("Class Distribution")\n',
            'plt.xlabel("Class")\n',
            'plt.ylabel("Frequency")\n',
            'plt.show()'
        ]
    },
    {
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': [
            '# Data Cleaning: Remove missing values and unuseful features (like IPs and Ports which are first 7 columns)\n',
            'cleaned_data = raw_data.dropna(axis=0).copy()\n',
            'data_useful_feat = cleaned_data[cleaned_data.columns[7:]].copy()\n',
            '\n',
            '# Encode labels\n',
            'from sklearn.preprocessing import LabelEncoder\n',
            'label_encoder = LabelEncoder()\n',
            'data_useful_feat[\'Label\']= label_encoder.fit_transform(data_useful_feat[\'Label\'])\n',
            'data_useful_feat.head()'
        ]
    },
    {
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': [
            '# Apply Min-Max Scaling\n',
            'def min_max_scaling(df):\n',
            '    df_norm = df.copy()\n',
            '    for column in df_norm.columns:\n',
            '        if column != \'Label\' and pd.api.types.is_numeric_dtype(df_norm[column]):\n',
            '            df_norm[column] = (df_norm[column] - df_norm[column].min()) / (df_norm[column].max() - df_norm[column].min())\n',
            '    return df_norm\n',
            '\n',
            'min_max_scaled = min_max_scaling(data_useful_feat)\n',
            'min_max_scaled_cleaned = min_max_scaled.dropna(axis=1).copy()\n',
            'min_max_scaled_cleaned.head()'
        ]
    },
    {
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': [
            '# Feature Selection: Selecting features having absolute correlation values above 0.2\n',
            'corr_features = [\'Fwd Pkt Len Min\', \'Bwd Pkt Len Max\',  \'Bwd Pkt Len Mean\', \n',
            '                  \'Bwd Pkt Len Std\', \'Pkt Len Mean\', \'Pkt Len Std\', \'Down/Up Ratio\', \n',
            '                  \'Pkt Size Avg\', \'Bwd Seg Size Avg\', \'Init Bwd Win Byts\', \'Label\']\n',
            'Final_dataframe = min_max_scaled_cleaned[corr_features].copy()\n',
            'Final_dataframe.head()'
        ]
    }
]
d['cells'].extend(new_cells)
with open('VPN_Sentinel_Main.ipynb', 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=1)
