import json
from collections import Counter

# Read the JSON file
with open('', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 60)
print("CHANGE ANALYSIS DISTRIBUTION")
print("=" * 60)

# 1. Basic statistics
print(f"\n📊 BASIC STATISTICS")
print(f"Total rules analyzed: {len(data)}")
print(f"Rules with changes: {sum(1 for rule in data if rule['changes'])}")
print(f"Rules without changes: {sum(1 for rule in data if not rule['changes'])}")

# 2. Change type distribution
print(f"\n🎯 CHANGE TYPE DISTRIBUTION")
change_types = []
change_counts = []

for rule in data:
    for change in rule['changes']:
        change_types.append(change['type'])
        change_counts.append(change['count'])

type_counter = Counter(change_types)
print(f"Total changes detected: {len(change_types)}")
print(f"Unique change types: {len(type_counter)}")

for change_type, count in type_counter.most_common():
    percentage = (count / len(change_types)) * 100
    print(f"  {change_type}: {count} ({percentage:.1f}%)")

# 3. Change count per rule
print(f"\n🔢 CHANGES PER RULE DISTRIBUTION")
changes_per_rule = [len(rule['changes']) for rule in data]
rule_counter = Counter(changes_per_rule)

for num_changes, count in sorted(rule_counter.items()):
    percentage = (count / len(data)) * 100
    print(f"  {num_changes} change(s): {count} rule(s) ({percentage:.1f}%)")

# 4. Most common change counts (x1, x2, etc.)
print(f"\n📈 CHANGE COUNT MAGNITUDE (x1, x2, etc.)")
count_counter = Counter(change_counts)
for count_val, freq in sorted(count_counter.items()):
    percentage = (freq / len(change_types)) * 100
    print(f"  x{count_val}: {freq} occurrences ({percentage:.1f}%)")

# 5. Rules with multiple changes
print(f"\n🔀 RULES WITH MULTIPLE CHANGES")
for rule in data:
    if len(rule['changes']) > 1:
        print(f"\nRule {rule['id']}: {len(rule['changes'])} changes")
        for change in rule['changes']:
            print(f"  - {change['type']} (x{change['count']})")

# 6. Detailed breakdown by rule
print(f"\n📋 DETAILED BREAKDOWN BY RULE")
for rule in data:
    if rule['changes']:
        print(f"\nRule {rule['id']}: {len(rule['changes'])} change(s)")
        for change in rule['changes']:
            print(f"  • {change['description']}")
    else:
        print(f"\nRule {rule['id']}: No changes")

# 7. Summary table
print(f"\n" + "=" * 60)
print("SUMMARY TABLE")
print("=" * 60)
print(f"{'Rule ID':<10} {'# Changes':<12} {'Change Types':<30}")
print("-" * 60)
for rule in data:
    if rule['changes']:
        types = ", ".join([c['type'] for c in rule['changes']][:2])
        if len(rule['changes']) > 2:
            types += f" (+{len(rule['changes'])-2} more)"
    else:
        types = "None"
    print(f"{rule['id']:<10} {len(rule['changes']):<12} {types:<30}")

# 8. Modality changes specifically
print(f"\n🎭 MODALITY CHANGES ANALYSIS")
modality_changes = []
for rule in data:
    for change in rule['changes']:
        if change['type'] == 'modified_modality':
            modality_changes.append(change)

if modality_changes:
    print(f"Total modality changes: {len(modality_changes)}")
    for change in modality_changes:
        print(f"  Rule: {rule['id'] if 'id' in locals() else 'N/A'}, {change['description']}")
else:
    print("No modality changes found")

print(f"\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)