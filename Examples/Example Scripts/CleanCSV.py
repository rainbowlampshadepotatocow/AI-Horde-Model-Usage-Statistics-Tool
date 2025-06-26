import pandas as pd
import re

# Load data
csv_path = 'models.csv' #Whitelist of models
xlsx_path = 'text_models_usage.xlsx'

# Read files
df = pd.read_excel(xlsx_path, sheet_name='Month')
models_df = pd.read_csv(csv_path)

# Extract short names
df['raw_short'] = df['model'].astype(str).str.split('/').str[-1]
models_df['model_short'] = models_df['name'].astype(str).str.split('/').str[-1]

# Map for correct capitals
model_short_map = {ms.lower(): ms for ms in models_df['model_short']}

# Quant stripping regex
quant_pattern = re.compile(r'(?i)([._-](?:iMat|iMatrix|i\d+|IQ?\d+|Q\d+|b\d+|c\d+|ch\d+|bpw|h\d+|exl\d+).*)$')

def strip_quant(name):
    return quant_pattern.sub('', name)

def map_to_whitelist(raw):
    for short_lower, short_orig in model_short_map.items():
        if raw.lower().endswith(short_lower):
            return short_orig
    return None

# Apply mapping and cleaning
df['mapped'] = df['raw_short'].apply(map_to_whitelist)
df['cleaned'] = df['raw_short'].apply(strip_quant)
df['unified_name'] = df.apply(lambda r: r['mapped'] if r['mapped'] else r['cleaned'], axis=1)

# Group and sum
merged = df.groupby('unified_name', as_index=False)['usage_count'].sum()

# Save and preview
output_path = 'text_models_merged_full_v3.xlsx'
merged.to_excel(output_path, index=False)

print("Saved the full merged spreadsheet.")
