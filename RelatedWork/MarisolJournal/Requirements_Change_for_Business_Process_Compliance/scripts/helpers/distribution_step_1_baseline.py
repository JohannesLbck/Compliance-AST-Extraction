import json
from collections import Counter
import pandas as pd

# Load the JSON data
with open('', 'r', encoding='utf-8') as f:
    data = json.load(f)


def get_statistics(rules):
    stats = {
        'summary': {},
        'version_analysis': {},
        'norm_analysis': {},
        'precondition_analysis': {},
        'parameter_analysis': {},
        'count_distribution': {},
        'action_analysis': {},
        'version_differences': []
    }

    # 1. Basic counts
    stats['summary']['total_rules'] = len(rules)
    stats['summary']['both_versions_count'] = sum(1 for r in rules if r.get('both_versions', False))
    stats['summary']['separate_versions_count'] = len(rules) - stats['summary']['both_versions_count']

    # Initialize counters
    norm_types = Counter()
    operators = Counter()
    actions = Counter()
    parameters = Counter()
    precondition_parameters = Counter()
    precondition_counts = Counter()
    norm_counts = Counter()
    all_parameters = []
    version_differences = []

    for rule in rules:
        rule_id = rule['id']

        if rule.get('both_versions', False):
            # Both versions have same structure
            pre = rule.get('precondition')
            norm = rule.get('norm')

            if pre:
                actions[pre.get('action', 'unknown')] += 1
                if 'operator' in pre:
                    operators[pre['operator']] += 1
                precondition_counts[pre.get('count', 1)] += 1
                if 'parameters' in pre:
                    for p in pre['parameters']:
                        precondition_parameters[p] += 1

            if norm:
                norm_types[norm['type']] += 1
                norm_counts[norm.get('count', 1)] += 1
                params = norm.get('parameters', [])
                all_parameters.extend(params)
                for param in params:
                    parameters[param] += 1
        else:
            for version in ['version_1', 'version_2']:
                version_data = rule['versions'][version]

                pre = version_data.get('precondition')
                norm = version_data.get('norm')

                if pre:
                    actions[pre.get('action', 'unknown')] += 1
                    if 'operator' in pre:
                        operators[pre['operator']] += 1
                    precondition_counts[pre.get('count', 1)] += 1
                    if 'parameters' in pre:
                        for p in pre['parameters']:
                            precondition_parameters[p] += 1

                if norm:
                    norm_types[norm['type']] += 1
                    norm_counts[norm.get('count', 1)] += 1
                    params = norm.get('parameters', [])
                    all_parameters.extend(params)
                    for param in params:
                        parameters[param] += 1

            # Version differences
            v1 = rule['versions']['version_1']
            v2 = rule['versions']['version_2']

            differences = []

            prec1 = v1['precondition']
            prec2 = v2['precondition']
            if (prec1 is None and prec2 is not None) or (prec1 is not None and prec2 is None):
                differences.append('precondition_presence')
            elif prec1 and prec2:
                for key in ['action', 'operator', 'count']:
                    if prec1.get(key) != prec2.get(key):
                        differences.append(f'precondition_{key}')
                if prec1.get('parameters', []) != prec2.get('parameters', []):
                    differences.append('precondition_parameters')

            norm1 = v1['norm']
            norm2 = v2['norm']
            if (norm1 is None and norm2 is not None) or (norm1 is not None and norm2 is None):
                differences.append('norm_presence')
            elif norm1 and norm2:
                if norm1.get('type') != norm2.get('type'):
                    differences.append('norm_type')
                if norm1.get('count', 1) != norm2.get('count', 1):
                    differences.append('norm_count')
                if set(norm1.get('parameters', [])) != set(norm2.get('parameters', [])):
                    differences.append('norm_parameters')

            if differences:
                version_differences.append({
                    'rule_id': rule_id,
                    'differences': differences,
                    'v1_precondition': v1['precondition'],
                    'v2_precondition': v2['precondition'],
                    'v1_norm': v1['norm'],
                    'v2_norm': v2['norm']
                })

    # Assemble stats
    stats['version_analysis']['both_versions_percentage'] = (stats['summary']['both_versions_count'] / len(rules)) * 100
    stats['norm_analysis']['total_norms'] = sum(norm_types.values())
    stats['norm_analysis']['type_distribution'] = dict(norm_types.most_common())
    stats['norm_analysis']['most_common_norm'] = norm_types.most_common(1)[0] if norm_types else None

    stats['precondition_analysis']['has_precondition_percentage'] = (sum(precondition_counts.values()) / (
                len(rules) * 2)) * 100
    stats['precondition_analysis']['operator_distribution'] = dict(operators.most_common())
    stats['precondition_analysis']['action_distribution'] = dict(actions.most_common())
    stats['precondition_analysis']['precondition_parameters'] = dict(precondition_parameters.most_common())

    stats['parameter_analysis']['total_unique_parameters'] = len(parameters)
    stats['parameter_analysis']['parameter_frequency'] = dict(parameters.most_common())
    stats['parameter_analysis']['most_common_parameter'] = parameters.most_common(1)[0] if parameters else None

    stats['count_distribution']['precondition_counts'] = dict(precondition_counts)
    stats['count_distribution']['norm_counts'] = dict(norm_counts)

    stats['version_differences'] = version_differences
    stats['summary']['rules_with_version_differences'] = len(version_differences)

    param_combinations = Counter()
    for rule in rules:
        if rule.get('both_versions', False) and rule['norm']:
            params = tuple(sorted(rule['norm'].get('parameters', [])))
            param_combinations[params] += 1
        elif not rule.get('both_versions', False):
            for version in ['version_1', 'version_2']:
                norm = rule['versions'][version]['norm']
                if norm:
                    params = tuple(sorted(norm.get('parameters', [])))
                    param_combinations[params] += 1

    stats['parameter_analysis']['parameter_combinations'] = dict(param_combinations.most_common(10))

    return stats


def print_statistics(stats):
    print("=" * 60)
    print("RULE ANALYSIS STATISTICS")
    print("=" * 60)

    print(f"\n📊 SUMMARY")
    print(f"Total rules: {stats['summary']['total_rules']}")
    print(f"Rules with both versions: {stats['summary']['both_versions_count']}")
    print(f"Rules with separate versions: {stats['summary']['separate_versions_count']}")
    print(f"Rules with version differences: {stats['summary']['rules_with_version_differences']}")

    print(f"\n🎯 NORM TYPE DISTRIBUTION")
    for norm_type, count in stats['norm_analysis']['type_distribution'].items():
        percentage = (count / stats['norm_analysis']['total_norms']) * 100
        print(f"  {norm_type}: {count} ({percentage:.1f}%)")

    print(f"\n🔧 PRECONDITION ANALYSIS")
    print(f"Rules with preconditions: {stats['precondition_analysis']['has_precondition_percentage']:.1f}%")
    print("Operators used:")
    for op, count in stats['precondition_analysis']['operator_distribution'].items():
        print(f"  {op}: {count}")
    print("Actions used:")
    for action, count in stats['precondition_analysis']['action_distribution'].items():
        print(f"  {action}: {count}")
    print("Precondition Parameters:")
    for param, count in stats['precondition_analysis']['precondition_parameters'].items():
        print(f"  {param}: {count}")

    print(f"\n📈 PARAMETER ANALYSIS")
    print(f"Unique parameters: {stats['parameter_analysis']['total_unique_parameters']}")
    print("Most frequent parameters:")
    for param, count in list(stats['parameter_analysis']['parameter_frequency'].items())[:10]:
        print(f"  {param}: {count}")

    print(f"\n🔢 COUNT DISTRIBUTION")
    print("Precondition counts (x1, x2, etc.):")
    for count, freq in sorted(stats['count_distribution']['precondition_counts'].items()):
        print(f"  x{count}: {freq}")

    print("\nNorm counts:")
    for count, freq in sorted(stats['count_distribution']['norm_counts'].items()):
        print(f"  x{count}: {freq}")

    print(f"\n🔄 VERSION DIFFERENCES")
    for diff in stats['version_differences']:
        print(f"\nRule {diff['rule_id']}: {', '.join(diff['differences'])}")

    print(f"\n🤝 COMMON PARAMETER COMBINATIONS")
    for combo, count in stats['parameter_analysis']['parameter_combinations'].items():
        if combo:
            print(f"  {combo}: {count}")


def generate_dataframe(rules):
    rows = []
    for rule in rules:
        rule_id = rule['id']
        both_versions = rule.get('both_versions', False)

        if both_versions:
            rows.append({
                'id': rule_id,
                'version': 'both',
                'precondition_action': rule['precondition'].get('action') if rule['precondition'] else None,
                'precondition_operator': rule['precondition'].get('operator') if rule['precondition'] else None,
                'precondition_count': rule['precondition'].get('count') if rule['precondition'] else None,
                'norm_type': rule['norm'].get('type') if rule['norm'] else None,
                'norm_count': rule['norm'].get('count') if rule['norm'] else None,
                'parameters': ', '.join(rule['norm'].get('parameters', [])) if rule['norm'] else None
            })
        else:
            for version in ['version_1', 'version_2']:
                v_data = rule['versions'][version]
                rows.append({
                    'id': rule_id,
                    'version': version,
                    'precondition_action': v_data['precondition'].get('action') if v_data['precondition'] else None,
                    'precondition_operator': v_data['precondition'].get('operator') if v_data['precondition'] else None,
                    'precondition_count': v_data['precondition'].get('count') if v_data['precondition'] else None,
                    'norm_type': v_data['norm'].get('type') if v_data['norm'] else None,
                    'norm_count': v_data['norm'].get('count') if v_data['norm'] else None,
                    'parameters': ', '.join(v_data['norm'].get('parameters', [])) if v_data['norm'] else None
                })

    return pd.DataFrame(rows)


# Main execution
if __name__ == "__main__":
    print("Analyzing rules data...\n")

    stats = get_statistics(data)
    print_statistics(stats)

    df = generate_dataframe(data)

    print("\n" + "=" * 60)
    print("DATAFRAME PREVIEW")
    print("=" * 60)
    print(df.head(10))

    print("\n" + "=" * 60)
    print("ADDITIONAL ANALYSIS")
    print("=" * 60)

    print("\n📊 Norm Type by Version:")
    crosstab = pd.crosstab(df['norm_type'], df['version'])
    print(crosstab)

    print("\n📊 Precondition Presence:")
    df['has_precondition'] = df['precondition_action'].notna()
    precondition_summary = df.groupby('version')['has_precondition'].value_counts(normalize=True)
    print(precondition_summary)

    df.to_csv('rules_analysis.csv', index=False)
    print("\n✅ Data saved to 'rules_analysis.csv'")

    with open('rules_statistics.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, default=str)
    print("✅ Statistics saved to 'rules_statistics.json'")
