import json
import os
from difflib import SequenceMatcher

# Define the case study names
case_studies = ["bpmq", "crl", "dcr", "haar", "lyn", "pcl", "ppsl", "status", "sun", "winter", "zasada"]

base_path = "/home/johannesl/Papers/BPM26/Eval"
prep_path = os.path.join(base_path, "UserStudyPrep")

def similarity(a, b):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, a, b).ratio()

def is_substantially_different(req1, req2, threshold=0.60):
    """Check if two requirements are substantially different (similarity below threshold)"""
    sim = similarity(str(req1), str(req2))
    return sim < threshold

def extract_changes(req1, req2):
    """Extract what changed between two requirements"""
    changes = []
    
    # Check for pattern changes
    req1_str = str(req1).lower()
    req2_str = str(req2).lower()
    
    patterns_1_8 = ['timed_alternative', 'loop', 'parallel', 'leads_to_absence', 'precedence_absence']
    patterns_9_12 = ['failure_directly_follows', 'failure_eventually_follows', 'send_exists', 'receive_exists', 'condition']
    
    for p in patterns_9_12:
        if p in req2_str and p not in req1_str:
            changes.append(f"Added: {p}")
    
    for p in patterns_1_8:
        if p in req1_str and p not in req2_str:
            changes.append(f"Removed: {p}")
    
    return changes

# Collect differences
differences = []

for study in case_studies:
    prep_file = os.path.join(prep_path, f"{study}.json")
    with open(prep_file, 'r') as f:
        data = json.load(f)
    
    # Get Generated1-8
    gen_1_8 = {}
    for gen in ["Generated1", "Generated2", "Generated3", "Generated4", "Generated5", "Generated6", "Generated7", "Generated8"]:
        if gen in data:
            gen_1_8[gen] = data[gen]
    
    # Get Generated9-12
    gen_9_12 = {}
    for gen in ["Generated9", "Generated10", "Generated11", "Generated12"]:
        if gen in data:
            gen_9_12[gen] = data[gen]
    
    # Aggregate requirements by rule ID
    rules_1_8 = {}
    rules_9_12 = {}
    
    for gen, reqs in gen_1_8.items():
        for rule_id, rule_text in reqs.items():
            if rule_id not in rules_1_8:
                rules_1_8[rule_id] = []
            rules_1_8[rule_id].append((gen, rule_text))
    
    for gen, reqs in gen_9_12.items():
        for rule_id, rule_text in reqs.items():
            if rule_id not in rules_9_12:
                rules_9_12[rule_id] = []
            rules_9_12[rule_id].append((gen, rule_text))
    
    # Compare rules
    for rule_id in sorted(set(rules_1_8.keys()) & set(rules_9_12.keys())):
        # Get average requirement for each group
        req_1_8_sample = rules_1_8[rule_id][0][1] if rules_1_8[rule_id] else ""
        req_9_12_sample = rules_9_12[rule_id][0][1] if rules_9_12[rule_id] else ""
        
        if is_substantially_different(req_1_8_sample, req_9_12_sample):
            changes = extract_changes(req_1_8_sample, req_9_12_sample)
            
            differences.append({
                'study': study,
                'rule_id': rule_id,
                'full_1_8': req_1_8_sample,
                'full_9_12': req_9_12_sample,
                'similarity': similarity(req_1_8_sample, req_9_12_sample),
                'changes': changes,
                'unique_1_8': len(set(req[1] for req in rules_1_8[rule_id])),
                'unique_9_12': len(set(req[1] for req in rules_9_12[rule_id]))
            })

# Sort by similarity (most different first)
differences.sort(key=lambda x: x['similarity'])

print("=" * 120)
print("SUBSTANTIAL DIFFERENCES BETWEEN GENERATED1-8 AND GENERATED9-12")
print("=" * 120)
print(f"\nFound {len(differences)} substantially different rules out of all rules analyzed")
print(f"Average similarity: {sum(d['similarity'] for d in differences) / len(differences):.1%}\n")

for i, diff in enumerate(differences, 1):
    print(f"\n{'─' * 120}")
    print(f"{i}. {diff['study'].upper()} - Rule {diff['rule_id']} | Similarity: {diff['similarity']:5.1%} | Variations: Gen1-8={diff['unique_1_8']}, Gen9-12={diff['unique_9_12']}")
    print(f"{'─' * 120}")
    
    if diff['changes']:
        print(f"KEY CHANGES: {', '.join(diff['changes'])}")
    
    print(f"\n┌─ Generated1-8 (typical):")
    lines_1_8 = diff['full_1_8'].split(' and ')
    for line in lines_1_8:
        print(f"│  {line.strip()}")
    
    print(f"\n├─ Generated9-12 (typical):")
    lines_9_12 = diff['full_9_12'].split(' and ')
    for line in lines_9_12:
        print(f"│  {line.strip()}")
    print(f"└─")

print(f"\n{'=' * 120}")
print("SUMMARY OF CHANGES")
print(f"{'=' * 120}")
print(f"\nTotal substantially different rules: {len(differences)}")
print(f"Files affected: {len(set(d['study'] for d in differences))}")
print(f"  - {', '.join(sorted(set(d['study'] for d in differences)))}")
print(f"\nMost different rule: {differences[0]['study'].upper()} - {differences[0]['rule_id']} ({differences[0]['similarity']:.1%})")
print(f"Least different rule: {differences[-1]['study'].upper()} - {differences[-1]['rule_id']} ({differences[-1]['similarity']:.1%})")

# Count pattern changes
added_patterns = set()
removed_patterns = set()
for diff in differences:
    for change in diff['changes']:
        if change.startswith('Added:'):
            added_patterns.add(change.replace('Added: ', ''))
        elif change.startswith('Removed:'):
            removed_patterns.add(change.replace('Removed: ', ''))

if added_patterns or removed_patterns:
    print(f"\nPattern changes introduced:")
    if added_patterns:
        print(f"  ✓ Added: {', '.join(sorted(added_patterns))}")
    if removed_patterns:
        print(f"  ✗ Removed: {', '.join(sorted(removed_patterns))}")
