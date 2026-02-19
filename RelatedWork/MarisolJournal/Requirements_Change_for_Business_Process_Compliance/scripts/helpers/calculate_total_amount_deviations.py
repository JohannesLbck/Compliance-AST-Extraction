import os
import json
from collections import Counter

# path to your folder with JSON files
folder_path = "Add here folder where JSON files are"

# counter for deviation types
deviation_counts = Counter()

# iterate over all json files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        print(filename)
        filepath = os.path.join(folder_path, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            # each file contains a list of requirements
            for requirement in data:
                for deviation in requirement.get("deviations", []):
                    deviation_type = deviation.get("deviation_type")
                    if deviation_type:
                        deviation_counts[deviation_type] += 1

# print results
print("Deviation type counts:")
for dtype in ["non-compliance", "over-compliance", "no impact"]:
    print(f"{dtype}: {deviation_counts[dtype]}")
