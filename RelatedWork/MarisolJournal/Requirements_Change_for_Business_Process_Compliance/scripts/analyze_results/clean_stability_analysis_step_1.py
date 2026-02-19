import os
import pandas as pd

def parse_comparison_table_from_file(file_path):
    """
    Parses a single comparison text file and returns a matrix of difference counts.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    diff_counts = {}
    versions = set()

    for line in lines:
        if line.startswith("|") and "vs" in line:
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            if len(parts) < 2:
                continue
            pair = parts[0]
            identical = parts[1].lower()
            v1, v2 = map(str.strip, pair.split("vs"))
            key = tuple(sorted((v1, v2)))

            versions.update([v1, v2])

            if identical == "yes":
                diff_counts[key] = 0
            else:
                diff_counts[key] = diff_counts.get(key, 0) + 1

    versions = sorted(versions)
    matrix = pd.DataFrame(index=versions, columns=versions, dtype="Int64")

    for v1 in versions:
        for v2 in versions:
            if v1 == v2:
                matrix.loc[v1, v2] = None
            else:
                matrix.loc[v1, v2] = diff_counts.get(tuple(sorted((v1, v2))), 0)

    return matrix

def export_matrices_to_excel(folder_path, output_path):
    """
    Creates an Excel file with one sheet per file, each sheet containing a similarity matrix.
    """
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith(".txt"):
                file_path = os.path.join(folder_path, filename)
                sheet_name = os.path.splitext(filename)[0][:31]  # Excel max sheet name length
                matrix = parse_comparison_table_from_file(file_path)
                matrix.to_excel(writer, sheet_name=sheet_name)

    print(f"✅ Excel file created: {output_path}")

# === USAGE ===
if __name__ == "__main__":
    folder_path = ""  # 🔁 Replace with your actual folder
    output_excel = "multi_matrix_summary.xlsx"

    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
    else:
        export_matrices_to_excel(folder_path, output_excel)
