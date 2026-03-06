import json
import os
from pathlib import Path
from collections import defaultdict

# Configuration
sonnet_folder = "raws"
output_file = "merged_results.json"

# Parse and organize files
results = defaultdict(lambda: defaultdict(list))

for filename in sorted(os.listdir(sonnet_folder)):
    if not filename.endswith(".json") or filename == "merged_results.json":
        continue
    
    # Parse: datasetname_temperature_creationdate_creationtime.json
    parts = filename[:-5].split("_")  # Remove .json
    if len(parts) < 4:
        continue
    
    dataset_name = parts[0]
    temperature = parts[1]
    timestamp = f"{parts[2]}_{parts[3]}"  # creationdate_creationtime
    
    # Load JSON
    filepath = os.path.join(sonnet_folder, filename)
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        results[dataset_name][temperature].append({
            "timestamp": timestamp,
            "data": data
        })
    except Exception as e:
        print(f"Error reading {filename}: {e}")

# Sort by timestamp within each temperature group
for dataset in results:
    for temperature in results[dataset]:
        results[dataset][temperature].sort(key=lambda x: x["timestamp"])

# Write merged file
with open(output_file, "w") as f:
    json.dump(dict(results), f, indent=2)

print(f"Merged {len([f for f in os.listdir(sonnet_folder) if f.endswith('.json') and f != 'merged_results.json'])} files into {output_file}")