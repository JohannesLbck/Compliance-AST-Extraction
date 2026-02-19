import json
from collections import Counter


def quick_json_analysis(filename):
    """Quick analysis of JSON data."""

    # Load the JSON file
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("QUICK ANALYSIS")
    print("=" * 40)

    # Collect data
    deviation_types = []
    bpmn_elements = []

    for record in data:
        for deviation in record.get('deviations', []):
            deviation_types.append(deviation.get('type', ''))
            bpmn_elements.append(deviation.get('bpmn_element', ''))

    # Basic stats
    total_records = len(data)
    total_deviations = len(deviation_types)

    print(f"Records: {total_records}")
    print(f"Total deviations: {total_deviations}")
    print(f"Avg per record: {total_deviations / total_records:.2f}")

    # Type distribution
    print("\nDeviation Types:")
    type_counts = Counter(deviation_types)
    for dev_type, count in type_counts.items():
        print(f"  {dev_type}: {count} ({(count / total_deviations) * 100:.1f}%)")

    # Element distribution
    print("\nBPMN Elements:")
    element_counts = Counter(bpmn_elements)
    for element, count in element_counts.items():
        print(f"  {element}: {count} ({(count / total_deviations) * 100:.1f}%)")

    # Most common
    most_type = type_counts.most_common(1)[0]
    most_element = element_counts.most_common(1)[0]
    print(f"\nMost common: {most_type[0]} deviations, {most_element[0]} elements")


# Usage
quick_json_analysis("")