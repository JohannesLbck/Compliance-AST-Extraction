import os
import json
from collections import Counter
from typing import List

def analyze_single_requirement_file(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, dict):
                return {"filename": filepath, "requirements": [data]}
            elif isinstance(data, list):
                return {"filename": filepath, "requirements": data}
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
    return {"filename": filepath, "requirements": []}

def extract_actions(req: dict) -> List[dict]:
    actions = []
    pre = req.get("precondition", {})
    for key in ["and", "or", "not"]:
        actions.extend(pre.get(key, []))
    norms = req.get("norms", [])
    for norm in norms:
        act = norm.get("action")
        if act:
            actions.append(act)
    return actions

def analyze_requirements(requirements: List[dict], label: str = "GLOBAL") -> dict:
    stats = {
        "label": label,
        "total_requirements": len(requirements),
        "total_norms": 0,
        "total_precondition_actions": 0,
        "total_norm_actions": 0,
        "dimensions": Counter(),
        "compliance_patterns": Counter(),
        "modalities": Counter(),
        "activities_lengths": [],
        "resources_lengths": [],
        "data_value_keys": Counter(),
        "temporal_constraint_keys": Counter(),
        "fields_present": Counter(),
    }

    for req in requirements:
        norms = req.get("norms", [])
        stats["total_norms"] += len(norms)
        for norm in norms:
            stats["modalities"][norm.get("modality", "UNKNOWN")] += 1

        pre = req.get("precondition", {})
        for key in ["and", "or", "not"]:
            actions = pre.get(key, [])
            stats["total_precondition_actions"] += len(actions)

        actions = extract_actions(req)

        for act in actions:
            stats["dimensions"][act.get("dimension", "UNKNOWN")] += 1
            stats["compliance_patterns"][act.get("compliance_pattern", "UNKNOWN")] += 1

            if "activities" in act:
                stats["fields_present"]["activities"] += 1
                stats["activities_lengths"].append(len(act["activities"]))

            if "resources" in act:
                stats["fields_present"]["resources"] += 1
                stats["resources_lengths"].append(len(act["resources"]))

            for dv in act.get("data_values", []):
                for key in ["element", "value", "domain", "format", "purpose", "origin"]:
                    if key in dv:
                        stats["data_value_keys"][key] += 1

            for tc in act.get("temporal_constraints", []):
                for key in ["interval_minutes", "min_duration_minutes", "max_duration_minutes",
                            "window_start", "window_end", "schedule", "event", "recurrence"]:
                    if key in tc:
                        stats["temporal_constraint_keys"][key] += 1

        stats["total_norm_actions"] += len(norms)
    return stats

def print_stats(stats: dict):
    print(f"\n📄 FILE: {stats['label']}")
    print("---------------------------------------")
    print(f"Total requirements: {stats['total_requirements']}")
    print(f"Total norms: {stats['total_norms']}")
    print(f"Total precondition actions: {stats['total_precondition_actions']}")
    print(f"Total norm actions: {stats['total_norm_actions']}")
    print(f"Total actions: {stats['total_precondition_actions'] + stats['total_norm_actions']}")

    print("\n→ Dimension distribution:")
    for k, v in stats["dimensions"].items():
        print(f"   {k}: {v}")

    print("\n→ Compliance pattern distribution:")
    for k, v in stats["compliance_patterns"].items():
        print(f"   {k}: {v}")

    print("\n→ Modality distribution:")
    for k, v in stats["modalities"].items():
        print(f"   {k}: {v}")

    print("\n→ Action field presence:")
    for k, v in stats["fields_present"].items():
        print(f"   {k}: {v} actions")

    if stats["activities_lengths"]:
        print("\n→ Activities list length (min/max/avg):",
              min(stats["activities_lengths"]), "/",
              max(stats["activities_lengths"]), "/",
              round(sum(stats["activities_lengths"]) / len(stats["activities_lengths"]), 2))

    if stats["resources_lengths"]:
        print("\n→ Resources list length (min/max/avg):",
              min(stats["resources_lengths"]), "/",
              max(stats["resources_lengths"]), "/",
              round(sum(stats["resources_lengths"]) / len(stats["resources_lengths"]), 2))

    print("\n→ Data value subfields usage:")
    for k, v in stats["data_value_keys"].items():
        print(f"   {k}: {v}")

    print("\n→ Temporal constraint subfields usage:")
    for k, v in stats["temporal_constraint_keys"].items():
        print(f"   {k}: {v}")

def main(folder_path: str):
    all_stats = []
    total_requirements = []

    files = [f for f in os.listdir(folder_path) if f.endswith(".json") and os.path.isfile(os.path.join(folder_path, f))]
    for file in files:
        file_path = os.path.join(folder_path, file)
        data = analyze_single_requirement_file(file_path)
        stats = analyze_requirements(data["requirements"], label=file)
        print_stats(stats)
        all_stats.extend(data["requirements"])

    # Global summary
    if all_stats:
        global_stats = analyze_requirements(all_stats, label="GLOBAL SUMMARY")
        print_stats(global_stats)

if __name__ == "__main__":
    folder_path = "Add here folder where the formalized files are"
    main(folder_path)
