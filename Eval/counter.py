import json
import os

def count_rules(file_path):
    """Count rules in a merged_results.json file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        total = 0
        
        # Handle nested structure with process names and thresholds
        if isinstance(data, dict):
            for process_name, thresholds in data.items():
                if isinstance(thresholds, dict):
                    for threshold, entries in thresholds.items():
                        if isinstance(entries, list):
                            for entry in entries:
                                if isinstance(entry, dict):
                                    # Check for 'data' key
                                    if 'data' in entry and isinstance(entry['data'], dict):
                                        # Gemini format: data is a dict with 'requirements' key
                                        if 'requirements' in entry['data'] and isinstance(entry['data']['requirements'], list):
                                            total += len(entry['data']['requirements'])
                                    elif 'data' in entry and isinstance(entry['data'], list):
                                        # GPT format: data is a list
                                        total += len(entry['data'])
        return total
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0

def main():
    # Find all merged_results.json files in current directory and subdirectories
  base_path = "/home/johannesl/Papers/BPM26Full/BPM26"
  total_rules = 0
  files_found = []

  for root, dirs, files in os.walk(base_path):
      for file in files:
          if file == "merged_results.json":
              file_path = os.path.join(root, file)
              rule_count = count_rules(file_path)
              files_found.append((file_path, rule_count))
              total_rules += rule_count
              print(f"{file_path}: {rule_count} rules")

  print(f"\n{'='*50}")
  print(f"Total files found: {len(files_found)}")
  print(f"Total rules across all files: {total_rules}")

if __name__ == "__main__":
  main()