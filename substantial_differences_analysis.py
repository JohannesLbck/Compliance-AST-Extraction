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
            # Check if there's variety within each group
            unique_1_8 = len(set(req[1] for req in rules_1_8[rule_id]))
            unique_9_12 = len(set(req[1] for req in rules_9_12[rule_id]))
            
            differences.append({
                'study': study,
                'rule_id': rule_id,
                'sample_1_8': req_1_8_sample[:100] + ('...' if len(req_1_8_sample) > 100 else ''),
                'sample_9_12': req_9_12_sample[:100] + ('...' if len(req_9_12_sample) > 100 else ''),
                'full_1_8': req_1_8_sample,
                'full_9_12': req_9_12_sample,
                'similarity': similarity(req_1_8_sample, req_9_12_sample),
                'unique_1_8': unique_1_8,
                'unique_9_12': unique_9_12
            })

print("=" * 100)
print("SUBSTANTIAL DIFFERENCES BETWEEN GENERATED1-8 AND GENERATED9-12")
print("=" * 100)
print(f"\nFound {len(differences)} substantially different rules\n")

# Sort by similarity (most different first)
differences.sort(key=lambda x: x['similarity'])

for i, diff in enumerate(differences, 1):
    print(f"\n{'-' * 100}")
    print(f"{i}. {diff['study'].upper()} - {diff['rule_id']} (similarity: {diff['similarity']:.1%})")
    print(f"{'-' * 100}")
    print(f"\nGenerated1-8 sample:")
    print(f"  {diff['sample_1_8']}")
    print(f"\nGenerated9-12 sample:")
    print(f"  {diff['sample_9_12']}")
    print(f"\nUnique variations: Gen1-8={diff['unique_1_8']}, Gen9-12={diff['unique_9_12']}")

print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)
print(f"\nTotal rules with substantial differences: {len(differences)}")
print(f"Average similarity: {sum(d['similarity'] for d in differences) / len(differences):.1%}")
print(f"Most different: {differences[0]['study'].upper()} - {differences[0]['rule_id']} ({differences[0]['similarity']:.1%})")
print(f"Least different: {differences[-1]['study'].upper()} - {differences[-1]['rule_id']} ({differences[-1]['similarity']:.1%})")

print("\n" + "=" * 100)
print("DETAILED COMPARISON OF TOP 5 MOST DIFFERENT RULES")
print("=" * 100)

for i, diff in enumerate(differences[:5], 1):
    print(f"\n{'=' * 100}")
    print(f"{i}. {diff['study'].upper()} - {diff['rule_id']} (Similarity: {diff['similarity']:.1%})")
    print(f"{'=' * 100}")
    print(f"\nGenerated1-8 (typical):")
    print(f"  {diff['full_1_8']}\n")
    print(f"Generated9-12 (typical):")
    print(f"  {diff['full_9_12']}")
