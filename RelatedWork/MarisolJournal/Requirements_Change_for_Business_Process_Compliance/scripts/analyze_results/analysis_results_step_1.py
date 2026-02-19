import pandas as pd
import re
from collections import defaultdict

# === Step 1: Load the Excel file ===
file_path = ""
df = pd.read_excel(file_path)

# === Step 2: Assign scenario based on requirement_id ===
def get_scenario(req_id):
    num = int(req_id[1:])
    if 1 <= num <= 7:
        return "emergencies_scenario"
    elif 8 <= num <= 13:
        return "SIM_card_scenario"
    elif 14 <= num <= 20:
        return "blood_donation_scenario"
    else:
        return "unknown"

df["scenario"] = df["requirement_id"].apply(get_scenario)

# === Step 3: Parse annotation lines ===
def parse_lines_simple(text):
    counts = defaultdict(float)
    if pd.isna(text):
        return counts
    for line in str(text).splitlines():
        match = re.match(r'(\d+)([A-Z]+)\s*-\s*(precondition|norm)', line.strip(), re.IGNORECASE)
        if match:
            count = int(match.group(1))
            label = match.group(2).upper()
            target = match.group(3).lower()
            counts[(target, label)] += count
    return counts

# === Step 4: Metric calculation ===
def compute_all_metrics(tp, fp, fn, tn=None):
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
    accuracy = (tp + tn) / (tp + fp + fn + tn) if tn is not None and (tp + fp + fn + tn) else 0
    specificity = tn / (tn + fp) if tn is not None and (tn + fp) else 0
    balanced_accuracy = (recall + specificity) / 2 if tn is not None else None
    return precision, recall, f1, accuracy, specificity, balanced_accuracy

# === Step 5: Per scenario and global computation ===
results = []
global_totals = defaultdict(float)

for scenario, group in df.groupby("scenario"):
    scenario_totals = defaultdict(float)

    for _, row in group.iterrows():
        counts = parse_lines_simple(row["clean_formalization_eval_v2"])
        for key, value in counts.items():
            scenario_totals[key] += value
            global_totals[key] += value  # accumulate for global metrics

    for target in ["precondition", "norm"]:
        tp = scenario_totals[(target, "TP")]
        fp = scenario_totals[(target, "FP")]
        fn = scenario_totals[(target, "FN")]
        tn = scenario_totals.get((target, "TN"))

        precision, recall, f1, accuracy, specificity, balanced_accuracy = compute_all_metrics(tp, fp, fn, tn)
        results.append({
            "Scenario": scenario,
            "Target": target,
            "TP": tp,
            "FP": fp,
            "FN": fn,
            "TN": tn,
            "Precision": precision,
            "Recall": recall,
            "F1": f1,
            "Accuracy": accuracy if tn is not None else None,
            "Specificity": specificity if tn is not None else None,
            "Balanced Accuracy": balanced_accuracy if tn is not None else None
        })

# === Step 6: Global Metrics ===
for target in ["precondition", "norm"]:
    tp = global_totals[(target, "TP")]
    fp = global_totals[(target, "FP")]
    fn = global_totals[(target, "FN")]
    tn = global_totals.get((target, "TN"))

    precision, recall, f1, accuracy, specificity, balanced_accuracy = compute_all_metrics(tp, fp, fn, tn)
    results.append({
        "Scenario": "ALL",
        "Target": target,
        "TP": tp,
        "FP": fp,
        "FN": fn,
        "TN": tn,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "Accuracy": accuracy if tn is not None else None,
        "Specificity": specificity if tn is not None else None,
        "Balanced Accuracy": balanced_accuracy if tn is not None else None
    })

# === Step 7: Save to Excel ===
results_df = pd.DataFrame(results)

output_path = ""
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    results_df[results_df["Scenario"] != "ALL"].to_excel(writer, sheet_name="Per Scenario", index=False)
    results_df[results_df["Scenario"] == "ALL"].to_excel(writer, sheet_name="Global Totals", index=False)

print(f"\n✅ Results saved to: {output_path}")
