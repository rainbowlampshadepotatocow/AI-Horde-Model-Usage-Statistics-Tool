import json
import pandas as pd

# Load the JSON data from the uploaded file
with open('RawModelUsageData.json', 'r', encoding='utf-8') as f:
    usage_data = json.load(f)

# Convert nested JSON to a tidy DataFrame
records = []
for period, models in usage_data.items():
    for model_name, count in models.items():
        records.append({
            'period': period,
            'model': model_name,
            'usage_count': count
        })

df = pd.DataFrame.from_records(records)

# Get top 25 models by usage for each period
top_per_period = df.groupby('period').apply(
    lambda d: d.sort_values('usage_count', ascending=False).head(25)
).reset_index(drop=True)

# Save the DataFrame to CSV
df.to_csv('text_models.csv', index=False)

# Save the top models per period to CSV
top_per_period.to_csv('text_models_top_per_period.csv', index=False)
