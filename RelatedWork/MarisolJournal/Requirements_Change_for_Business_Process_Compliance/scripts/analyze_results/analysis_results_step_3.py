import pandas as pd
import re
import numpy as np
from collections import defaultdict

# === Step 1: Load data from Excel file ===
file_path = ""
df = pd.read_excel(file_path)

# === Step 2: Extract TP, FP, FN from string format ===
def extract_counts(field):
    counts = defaultdict(float)
    if pd.isna(field):
        return counts
    entries = re.split(r',\s*', str(field))
    for entry in entries:
        match = re.match(r'(\d+)(?:/(\d+))?([A-Z]+)', entry)
        if match:
            if match.group(2):  # Fraction like 1/2TP
                num = float(match.group(1)) / float(match.group(2))
                label = match.group(3)
                counts[label] += num
                if label == 'TP':
                    counts['FP'] += num  # ambiguous TP also contributes to FP
                elif label == 'FN':
                    counts['TP'] += num  # ambiguous FN also contributes to TP
            else:
                num = float(match.group(1))
                label = match.group(3)
                counts[label] += num
    return counts

# === Step 3: Normalize boolean column ===
df['non_impacting_changes?'] = df['non_impacting_changes?'].astype(str).str.strip().str.lower()

# === Step 4: Compute metrics PER EXECUTION and FIELD ===
def compute_field_metrics_per_execution(field):
    records = []
    for (scenario_id, execution_id), group in df.groupby(['scenario_id', 'execution_id']):
        tp = fp = fn = 0.0
        for val in group[field]:
            counts = extract_counts(val)
            tp += counts['TP']
            fp += counts['FP']
            fn += counts['FN']
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        records.append({
            'scenario_id': scenario_id,
            'execution_id': execution_id,
            'field': field,
            'TP': tp,
            'FP': fp,
            'FN': fn,
            'precision': precision,
            'recall': recall,
            'f1': f1
        })
    return pd.DataFrame(records)

# === Step 5: Apply to all fields ===
fields = ['deviation_type', 'reasoning_about_root_cause', 'reference_in_model']
exec_field_dfs = [compute_field_metrics_per_execution(field) for field in fields]
metrics_per_exec_field = pd.concat(exec_field_dfs, ignore_index=True)

agg_per_scenario_field = (
    metrics_per_exec_field.groupby(['scenario_id', 'field'])
    .agg({
        'TP': 'sum',
        'FP': 'sum',
        'FN': 'sum',
        'precision': ['mean', 'std', 'count'],
        'recall': ['mean', 'std'],
        'f1': ['mean', 'std']
    })
)

# Flatten column names
agg_per_scenario_field.columns = ['_'.join(col).strip() for col in agg_per_scenario_field.columns.values]
agg_per_scenario_field = agg_per_scenario_field.reset_index()

# Add Coefficient of Variation
agg_per_scenario_field['precision_cv'] = agg_per_scenario_field['precision_std'] / agg_per_scenario_field['precision_mean']
agg_per_scenario_field['recall_cv'] = agg_per_scenario_field['recall_std'] / agg_per_scenario_field['recall_mean']
agg_per_scenario_field['f1_cv'] = agg_per_scenario_field['f1_std'] / agg_per_scenario_field['f1_mean']

# Handle inf/nan
agg_per_scenario_field.replace([np.inf, -np.inf], np.nan, inplace=True)
agg_per_scenario_field.fillna({'precision_cv': 0.0, 'recall_cv': 0.0, 'f1_cv': 0.0}, inplace=True)


# === Step 10: Save to Excel ===
output_file = ""

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    metrics_per_exec_field.to_excel(writer, sheet_name="Per Exec Per Field", index=False)
    agg_per_scenario_field.to_excel(writer, sheet_name="Per Scenario by Field", index=False)

print(f"✅ Corrected results written to '{output_file}' with proper execution-level aggregation.")
