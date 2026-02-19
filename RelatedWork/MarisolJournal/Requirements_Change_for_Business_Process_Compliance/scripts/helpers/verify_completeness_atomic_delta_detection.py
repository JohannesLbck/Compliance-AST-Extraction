from datetime import datetime
import json

# === Base requirement definition ===
base = {
    "id": "r_test",
    "precondition": {"and": [], "or": [], "not": []},
    "norms": [
        {
            "modality": "obligation",
            "action": {
                "dimension": "control_flow",
                "compliance_pattern": "existence_of_A",
                "activities": ["A"]
            }
        }
    ],
    "temporal_validity": {
        "start": "2023-01-01T00:00:00Z",
        "end": "2024-01-01T00:00:00Z"
    },
    "input_id": "r_test"
}

def clone(obj):
    return json.loads(json.dumps(obj))

test_cases = []

def add_case(name, mod_func):
    v1 = clone(base)
    v2 = clone(base)
    v1["input_version"] = "1"
    v2["input_version"] = "2"
    mod_func(v2, v1)
    v1["id"] = f"{name}_v1"
    v2["id"] = f"{name}_v2"
    test_cases.append((name, v1, v2))

# === Define test cases ===
add_case("temporal_validity_extend", lambda v2, v1: v2["temporal_validity"].update({"end": "2025-01-01T00:00:00Z"}))
add_case("temporal_validity_shorten", lambda v2, v1: v2["temporal_validity"].update({"end": "2023-06-01T00:00:00Z"}))
add_case("temporal_start_modify", lambda v2, v1: v2["temporal_validity"].update({"start": "2023-02-01T00:00:00Z"}))
add_case("modality_change", lambda v2, v1: v2["norms"][0].update({"modality": "permission"}))
add_case("compliance_pattern_change", lambda v2, v1: v2["norms"][0]["action"].update({"compliance_pattern": "absence_of_A"}))
add_case("dimension_change", lambda v2, v1: v2["norms"][0]["action"].update({"dimension": "data"}))
add_case("activities_change", lambda v2, v1: v2["norms"][0]["action"].update({"activities": ["A", "B"]}))
add_case("resources_modify", lambda v2, v1: (v1["norms"][0]["action"].update({"resources": ["X"]}), v2["norms"][0]["action"].update({"resources": ["X", "Y"]})))
add_case("temporal_constraints_add", lambda v2, v1: v2["norms"][0]["action"].update({"temporal_constraints": [{"min_duration_minutes": 30, "max_duration_minutes": 60}]}))
add_case("data_values_add", lambda v2, v1: v2["norms"][0]["action"].update({"data_values": [{"element": "flag", "value": "yes"}]}))
add_case("norm_add", lambda v2, v1: v2["norms"].append({"modality": "prohibition", "action": {"dimension": "resource", "compliance_pattern": "usage_of_R", "resources": ["res1"]}}))
add_case("norm_delete", lambda v2, v1: v2.update({"norms": []}))
add_case("precondition_action_add", lambda v2, v1: v2["precondition"]["and"].append({"dimension": "data", "compliance_pattern": "data_in_domain", "data_values": [{"element": "age", "domain": [18, 19]}]}))
add_case("precondition_action_delete", lambda v2, v1: v1["precondition"]["not"].append({"dimension": "control_flow", "compliance_pattern": "existence_of_A", "activities": ["Z"]}))
add_case("logical_operator_change", lambda v2, v1: (
    v1["precondition"]["and"].append({"dimension": "data", "compliance_pattern": "data_in_domain", "data_values": [{"element": "status", "domain": ["ok"]}]}),
    v2["precondition"]["or"].append({"dimension": "data", "compliance_pattern": "data_in_domain", "data_values": [{"element": "status", "domain": ["ok"]}]}))
)

# === Change detection functions ===
def compare_temporal_validity(old, new):
    changes = []
    old_start = datetime.fromisoformat(old['start'].replace("Z", "+00:00"))
    old_end = datetime.fromisoformat(old['end'].replace("Z", "+00:00"))
    new_start = datetime.fromisoformat(new['start'].replace("Z", "+00:00"))
    new_end = datetime.fromisoformat(new['end'].replace("Z", "+00:00"))
    if new_end > old_end:
        changes.append({"change": "extend", "element": "temporal_validity", "old": old, "new": new})
    elif new_end < old_end:
        changes.append({"change": "shorten", "element": "temporal_validity", "old": old, "new": new})
    elif new_start != old_start:
        changes.append({"change": "modify", "element": "temporal_validity", "old": old, "new": new})
    return changes

def compare_modalities(old, new):
    return [{"change": f"{old} -> {new}", "element": "modality", "old": old, "new": new}] if old != new else []

def compare_compliance_pattern(o, n):
    if o.get("compliance_pattern") != n.get("compliance_pattern"):
        return [{"change": "switch_compliance_pattern", "element": "compliance_pattern", "old": o.get("compliance_pattern"), "new": n.get("compliance_pattern")}]
    return []

def compare_actions(o, n):
    changes = []
    if o.get("dimension") != n.get("dimension"):
        changes.append({"change": "modify", "element": "dimension", "old": o.get("dimension"), "new": n.get("dimension")})
    for f in ["activities", "resources", "data_values", "temporal_constraints"]:
        if o.get(f) != n.get(f):
            changes.append({"change": f"modify_{f}", "element": f, "old": o.get(f), "new": n.get(f)})
    return changes

def compare_norms(old_norms, new_norms):
    changes = []
    for i, (o, n) in enumerate(zip(old_norms, new_norms)):
        changes += compare_modalities(o["modality"], n["modality"])
        changes += compare_compliance_pattern(o["action"], n["action"])
        changes += compare_actions(o["action"], n["action"])
    if len(new_norms) > len(old_norms):
        for extra in new_norms[len(old_norms):]:
            changes.append({"change": "add", "element": "norm", "new": extra})
    elif len(new_norms) < len(old_norms):
        for extra in old_norms[len(new_norms):]:
            changes.append({"change": "delete", "element": "norm", "old": extra})
    return changes

def detect_logical_operator_changes(old_prec, new_prec):
    changes = []
    for logic in ['and', 'or', 'not']:
        for other in ['and', 'or', 'not']:
            if logic != other:
                moved = [a for a in old_prec.get(logic, []) if a in new_prec.get(other, [])]
                if moved:
                    changes.append({
                        "change": f"{logic.upper()} -> {other.upper()}",
                        "element": "logical_operator",
                        "moved_actions": moved
                    })
    return changes

def compare_action_lists(old_list, new_list):
    changes = []
    matched_ids = set()
    for o in old_list:
        match = next((n for n in new_list if id(n) not in matched_ids and o.get("compliance_pattern") == n.get("compliance_pattern")), None)
        if match:
            matched_ids.add(id(match))
            changes += compare_actions(o, match)
        else:
            changes.append({"change": "delete", "element": "action", "old": o})
    for n in new_list:
        if id(n) not in matched_ids:
            changes.append({"change": "add", "element": "action", "new": n})
    return changes

def compare_preconditions(o, n):
    changes = detect_logical_operator_changes(o, n)
    for logic in ["and", "or", "not"]:
        changes += compare_action_lists(o.get(logic, []), n.get(logic, []))
    return changes

# === Run test cases ===
for name, v1, v2 in test_cases:
    changes = []

    if v1["temporal_validity"] != v2["temporal_validity"]:
        changes += compare_temporal_validity(v1["temporal_validity"], v2["temporal_validity"])
    if v1["norms"] != v2["norms"]:
        changes += compare_norms(v1["norms"], v2["norms"])
    if v1["precondition"] != v2["precondition"]:
        changes += compare_preconditions(v1["precondition"], v2["precondition"])

    for i, c in enumerate(changes, 1):
        c["change_id"] = f"{name}_c{i}"

    print(f"\n=== Test case: {name} ===")
    print(json.dumps(changes, indent=2))
