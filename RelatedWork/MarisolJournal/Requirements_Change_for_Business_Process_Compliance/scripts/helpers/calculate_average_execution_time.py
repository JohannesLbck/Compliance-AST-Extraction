import os
import json


def average_execution_time(folder_path):
    times = []

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".json"):
            file_path = os.path.join(folder_path, file_name)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "execution_time_seconds" in data:
                        times.append(float(data["execution_time_seconds"]))
            except Exception as e:
                print(f"Skipping {file_name}: {e}")

    if times:
        avg_time = sum(times) / len(times)
        return avg_time
    else:
        return None


# Example usage:
folder = "Add here folder where execution files are"
avg = average_execution_time(folder)
if avg is not None:
    print(f"Average execution_time_seconds: {avg:.4f}")
else:
    print("No valid execution_time_seconds found.")
