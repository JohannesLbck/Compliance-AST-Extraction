import pandas as pd
import numpy as np

# === CONFIG ===
EXCEL_FILE = ""

# === FUNCTIONS FOR METRICS ===
def consistency_index(matrix):
    """Normalized inverse mean distance."""
    dists = matrix.where(~np.eye(matrix.shape[0], dtype=bool)).stack()
    if len(dists) == 0:
        return np.nan
    mean_dist = dists.mean()
    max_dist = dists.max() if dists.max() != 0 else 1
    return 1 - (mean_dist / max_dist)

def stability_ratio(matrix, threshold=2):
    """Proportion of distances ≤ threshold."""
    dists = matrix.where(~np.eye(matrix.shape[0], dtype=bool)).stack()
    return (dists <= threshold).mean()

def variability_index(matrix):
    """Standard deviation of all pairwise distances."""
    dists = matrix.where(~np.eye(matrix.shape[0], dtype=bool)).stack()
    return dists.std()

# === SCENARIO MAPPING ===
def assign_scenario(req_name):
    """
    Extract the numeric part of the requirement name, e.g. 'r13' -> 13.
    Adapt this if your sheet names differ in format.
    """
    # Find integer inside the requirement label
    num = int(''.join(filter(str.isdigit, req_name)))
    if 1 <= num <= 7:
        return "emergencies_scenario"
    elif 8 <= num <= 13:
        return "SIM_card_scenario"
    elif 14 <= num <= 20:
        return "blood_donation_scenario"
    else:
        return "unknown_scenario"

# === MAIN SCRIPT ===
summary_rows = []

xlsx = pd.ExcelFile(EXCEL_FILE)

for sheet in xlsx.sheet_names:
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet, index_col=0).fillna(0)

    CI = consistency_index(df)
    SR = stability_ratio(df)
    VI = variability_index(df)

    scenario = assign_scenario(sheet)

    summary_rows.append({
        "Requirement": sheet,
        "Scenario": scenario,
        "Consistency Index (CI)": CI,
        "Stability Ratio (SR)": SR,
        "Variability Index (VI)": VI,
    })

summary_df = pd.DataFrame(summary_rows)

# Print summary
print("\n=== Stability Summary for All Requirements ===\n")
print(summary_df.to_string(index=False))

# Save requirement-level summary
summary_df.to_excel("stability_summary.xlsx", index=False)
print("\nSaved per-requirement summary to 'stability_summary.xlsx'")

# === AGGREGATE BY SCENARIO ===
scenario_summary = summary_df.groupby("Scenario").agg({
    "Consistency Index (CI)": "mean",
    "Stability Ratio (SR)": "mean",
    "Variability Index (VI)": "mean",
}).reset_index()

print("\n=== Scenario-Level Summary ===\n")
print(scenario_summary.to_string(index=False))

# Save scenario-level summary
scenario_summary.to_excel("scenario_summary.xlsx", index=False)
print("\nSaved scenario summary to 'scenario_summary.xlsx'")
