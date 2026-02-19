import pandas as pd

# ---------------------------------------------------
# Unified DataFrame with levels and results
# ---------------------------------------------------
df = pd.DataFrame([
    ["r1",  "change_in_activity",         "emergencies_scenario", "TP"],
    ["r2",  "change_in_role",             "emergencies_scenario", "FP"],
    ["r3",  "change_in_role",             "emergencies_scenario", "FP"],
    ["r3",  "add_precondition",           "emergencies_scenario", "TP"],
    ["r3",  "delete_norm",                "emergencies_scenario", "FN"],
    ["r4",  "add_precondition",           "emergencies_scenario", "TP"],
    ["r5",  "change_modality",            "emergencies_scenario", "TP"],
    ["r6",  "add_precondition",           "emergencies_scenario", "TP"],
    ["r7",  "switch_compliance_pattern",  "emergencies_scenario", "TP"],
    ["r8",  "change_modality",            "SIM_card_scenario", "TP"],
    ["r9",  "add_requirement",            "SIM_card_scenario", "TP"],
    ["r10", "change_in_role",             "SIM_card_scenario", "FN"],
    ["r11", "change_modality",            "SIM_card_scenario", "TP"],
    ["r11", "switch_pattern",             "SIM_card_scenario", "TP"],
    ["r11", "add_norm",                   "SIM_card_scenario", "TP"],
    ["r12", "delete_requirement",         "SIM_card_scenario", "TP"],
    ["r13", "change_in_data",             "SIM_card_scenario", "TP"],
    ["r14", "delete_precondition",        "blood_donation_scenario", "TP"],
    ["r15", "delete_norm",                "blood_donation_scenario", "FN"],
    ["r16", "delete_requirement",         "blood_donation_scenario", "TP"],
    ["r17", "change_time_constraint",     "blood_donation_scenario", "TP"],
    ["r17", "delete_action",              "blood_donation_scenario", "TP"],
    ["r17", "delete_norm",                "blood_donation_scenario", "TP"],
    ["r18", "add_requirement",            "blood_donation_scenario", "TP"],
    ["r19", "change_modality",            "blood_donation_scenario", "TP"],
    ["r20", "changed_logical_operator",   "blood_donation_scenario", "FP"],
], columns=["requirement_id", "change_type", "level", "result"])


# ---------------------------------------------------
# Compute metrics per level
# ---------------------------------------------------
rows = []

for level in sorted(df["level"].unique()):
    sub = df[df["level"] == level]

    TP = (sub["result"] == "TP").sum()
    FP = (sub["result"] == "FP").sum()
    FN = (sub["result"] == "FN").sum()

    # Precision
    precision = TP / (TP + FP) if (TP + FP) > 0 else None

    # Recall
    recall = TP / (TP + FN) if (TP + FN) > 0 else None

    # F1-score
    if precision is not None and recall is not None and (precision + recall) > 0:
        f1 = 2 * precision * recall / (precision + recall)
    else:
        f1 = None

    rows.append([level, TP, FP, FN, precision, recall, f1])

results = pd.DataFrame(rows, columns=["level", "TP", "FP", "FN", "precision", "recall", "f1_score"])

print("\n=== METRICS PER LEVEL ===")
print(results.to_string(index=False))

output_path = ""

results.to_excel(output_path, index=False)

print(f"\nSaved metrics to: {output_path}")
