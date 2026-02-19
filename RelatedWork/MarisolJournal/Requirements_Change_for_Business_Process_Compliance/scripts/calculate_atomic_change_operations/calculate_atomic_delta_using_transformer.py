from datetime import datetime
import argparse
import json
from sentence_transformers import SentenceTransformer, util

# Initialize argument parser
parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()

# Load input JSON
with open(args.input, "r", encoding="utf-8") as f:
    requirements = json.load(f)

# Ensure input contains exactly two versions
if len(requirements) != 2:
    raise ValueError("Input JSON must contain exactly two requirement versions.")

old_requirement = requirements[0]
new_requirement = requirements[1]

# Load sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')
SIMILARITY_THRESHOLD = 0.85

def semantic_similarity(text1, text2):
    emb1 = model.encode(text1, convert_to_tensor=True)
    emb2 = model.encode(text2, convert_to_tensor=True)
    return util.cos_sim(emb1, emb2).item()

def compare_temporal_validity(old, new):
    changes = []
    old_start = datetime.fromisoformat(old['start'])
    old_end = datetime.fromisoformat(old['end'])
    new_start = datetime.fromisoformat(new['start'])
    new_end = datetime.fromisoformat(new['end'])

    if new_end > old_end:
        changes.append({"change": "extend", "element": "temporal_validity", "old": old, "new": new})
    elif new_end < old_end:
        changes.append({"change": "shorten", "element": "temporal_validity", "old": old, "new": new})
    elif new_start != old_start:
        changes.append({"change": "modify", "element": "temporal_validity", "old": old, "new": new})
    return changes

def compare_modalities(old_mod, new_mod):
    if old_mod != new_mod:
        return [{
            "change": f"{old_mod} -> {new_mod}",
            "element": "modality",
            "old": old_mod,
            "new": new_mod
        }]
    return []

def compare_compliance_pattern(old_action, new_action):
    if old_action.get("compliance_pattern") != new_action.get("compliance_pattern"):
        return [{
            "change": "switch_compliance_pattern",
            "element": "compliance_pattern",
            "old": old_action.get("compliance_pattern"),
            "new": new_action.get("compliance_pattern")
        }]
    return []

def detect_logical_operator_changes(old_prec, new_prec):
    changes = []
    for logic in ['and', 'or', 'not']:
        for other_logic in ['and', 'or', 'not']:
            if logic != other_logic:
                moved = [a for a in old_prec.get(logic, []) if a in new_prec.get(other_logic, [])]
                if moved:
                    changes.append({
                        "change": f"{logic.upper()} -> {other_logic.upper()}",
                        "element": "logical_operator",
                        "moved_actions": moved
                    })
    return changes

def compare_actions(old_action, new_action):
    changes = []
    if old_action.get("dimension") != new_action.get("dimension"):
        changes.append({
            "change": "modify",
            "element": "dimension",
            "old": old_action.get("dimension"),
            "new": new_action.get("dimension")
        })

    for field in ["activities", "resources", "data_values", "temporal_constraints"]:
        if old_action.get(field) != new_action.get(field):
            changes.append({
                "change": f"modify_{field}",
                "element": field,
                "old": old_action.get(field),
                "new": new_action.get(field)
            })
    return changes

def compare_action_lists(old_list, new_list, dimension):
    changes = []
    matched_new_ids = set()

    for old in old_list:
        best_match = None
        best_score = 0.0
        old_text = json.dumps(old, sort_keys=True)

        for new in new_list:
            if id(new) in matched_new_ids:
                continue
            new_text = json.dumps(new, sort_keys=True)
            score = semantic_similarity(old_text, new_text)

            if score > best_score and score >= SIMILARITY_THRESHOLD:
                best_match = new
                best_score = score

        if best_match:
            matched_new_ids.add(id(best_match))
            sub_changes = compare_actions(old, best_match)
            for sc in sub_changes:
                changes.append({
                    "change": sc.get("change", "modify"),
                    "element": f"action.{sc['element']}",
                    "old": sc.get("old"),
                    "new": sc.get("new"),
                    "similarity": best_score
                })
        else:
            changes.append({
                "change": "delete",
                "element": "action",
                "old": old
            })

    for added in new_list:
        if id(added) not in matched_new_ids:
            changes.append({
                "change": "add",
                "element": "action",
                "new": added
            })

    return changes

def compare_norms(old_norms, new_norms):
    changes = []
    for i, (o, n) in enumerate(zip(old_norms, new_norms)):
        changes.extend(compare_modalities(o["modality"], n["modality"]))
        changes.extend(compare_compliance_pattern(o["action"], n["action"]))
        changes.extend(compare_actions(o["action"], n["action"]))
    if len(new_norms) > len(old_norms):
        for extra in new_norms[len(old_norms):]:
            changes.append({"change": "add", "element": "norm", "new": extra})
    elif len(new_norms) < len(old_norms):
        for missing in old_norms[len(new_norms):]:
            changes.append({"change": "delete", "element": "norm", "old": missing})
    return changes

def compare_preconditions(old_prec, new_prec):
    changes = []
    logic_changes = detect_logical_operator_changes(old_prec, new_prec)
    changes.extend(logic_changes)
    for logic in ['and', 'or', 'not']:
        old_list = old_prec.get(logic, [])
        new_list = new_prec.get(logic, [])
        changes.extend(compare_action_lists(old_list, new_list, logic))
    return changes

# Run the comparison
all_changes = []
if old_requirement["precondition"] != new_requirement["precondition"]:
    all_changes.extend(compare_preconditions(old_requirement["precondition"], new_requirement["precondition"]))

if old_requirement["norms"] != new_requirement["norms"]:
    all_changes.extend(compare_norms(old_requirement["norms"], new_requirement["norms"]))

if old_requirement["temporal_validity"] != new_requirement["temporal_validity"]:
    all_changes.extend(compare_temporal_validity(old_requirement["temporal_validity"], new_requirement["temporal_validity"]))

requirement_id = new_requirement.get("input_id", "UNKNOWN_REQ")

for i, c in enumerate(all_changes, start=1):
    c["change_id"] = f"{requirement_id}_c{i}"

delta_output = {
    "requirement_id": requirement_id,
    "from_version": old_requirement.get("input_version", 1),
    "to_version": new_requirement.get("input_version", 2),
    "changes": all_changes
}

with open(args.output, "w", encoding="utf-8") as f:
    json.dump(delta_output, f, indent=2, ensure_ascii=False)
