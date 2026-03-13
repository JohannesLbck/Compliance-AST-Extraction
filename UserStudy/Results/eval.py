import pandas as pd
import numpy as np
from pathlib import Path
from study_analysis import run_study_execution_analysis

DATASETS= {
    "A": "ResultsA.csv",
    "B": "ResultsB.csv",
    "C": "ResultsC.csv",
}
TEST_DATASET = {
    "test": "TestingTemplate.csv"
}

# Configuration
GT_COLUMN = Path(__file__).parent / "GroupBGT.csv"

COLUMNS = {
    "metadata": [
        "Startzeit",
        "Fertigstellungszeit",
        "E-Mail",
        "Id"
    ],
    "text": [col for col in [] if "Optional" in col],
    "study_execution": [
        "I have X years of experience with Process Modeling",
        "I have X years of experience with (Process) Compliance Management",
        "I have X years of experience with coding/programming.",
        "Goals and terms of the study.The terms used throughout the study were familiar",
        "Goals and terms of the study.The goal of the study is clear",
        "Goals and terms of the study.I understood the natural language compliance requirements",
        "Goals and terms of the study.I understood the encoded compliance requirements",
        "If any terms were unfamiliar, which (Open ended, Answer not required)",
        "Can you describe the goal of the study?",
        "Can you order the datasets by which you found more/less challenging to understand/evaluate.",
        "Space for any additional feedback regarding the survey, the datasets, the encodings, etc. (Open ended, Answer not required)",
    ]
}


    

def load_data(name):
    """Load CSV file with semicolon delimiter"""
    CSV_FILE = Path(__file__).parent / f"{name}"
    print(f"Loading data from: {CSV_FILE}")
    df = pd.read_csv(CSV_FILE, delimiter=";")
    print(f"Loading GT data from: {GT_COLUMN}")
    gt_df = pd.read_csv(GT_COLUMN, delimiter=";")
    return df, gt_df

def print_basic_info(df):
    """Print basic information about the dataset"""
    print("\n" + "="*80)
    print("BASIC DATASET INFORMATION")
    print("="*80)
    print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"\nData types:\n{df.dtypes}")

def prepare_task_df(df):
    """Prepare task-related dataframe by removing non-task columns."""
    # Flatten all column names from the dictionary
    columns_to_remove = []
    for category, col_list in COLUMNS.items():
        columns_to_remove.extend(col_list)
    
    # Also remove columns containing "Optional"
    columns_to_remove.extend([col for col in df.columns if "Optional" in col])
    
    # Remove duplicates and filter to only existing columns
    columns_to_remove = list(set(columns_to_remove))
    columns_to_remove = [col for col in columns_to_remove if col in df.columns]
    
    if columns_to_remove:
        df = df.drop(columns=columns_to_remove)

    return df


def report_task_averages(task_df, gt_df):
    """Compute, print, and export task averages analysis."""
    # calculate and display column averages
    averages = calculate_column_averages(task_df)

    total_average = averages.mean()
    print(f"\nOverall average score across all columns: {total_average:.2f}")
    if averages.empty:
        return pd.DataFrame(), task_df

    # Export averages to CSV
    averages_df = averages.reset_index()
    averages_df.columns = ['Question', 'Average']

    # Add question ID (1-5 within each question group)
    averages_df['ID'] = (averages_df.index % 5) + 1

    # Add gt_df column by cycling through the types
    averages_df['gt_df'] = gt_df['Type'].iloc[averages_df.index % len(gt_df)].values

    print(averages_df.head(10))  # Optional: print first 10 rows to verify

    # Per-question analysis (every 5 rows is a new question)
    threshold = averages_df['Average'].mean()
    high_threshhold = averages_df['Average'].mean() + averages_df['Average'].std()
    print("\n" + "="*80)
    print("PER-QUESTION ANALYSIS")
    print("="*80)
    print(f"Threshold (average across all data): {threshold:.2f}")
    print(f"High Threshold (mean + std): {high_threshhold:.2f}")
    print("="*80)
    for i in range(0, len(averages_df), 5):
        chunk = averages_df.iloc[i:i+5]
        question_avg = chunk['Average'].mean()
        y_avg = chunk[chunk['gt_df'] == 'Y']['Average'].mean() if (chunk['gt_df'] == 'Y').any() else None
        y_max = chunk[chunk['gt_df'] == 'Y']['Average'].max() if (chunk['gt_df'] == 'Y').any() else None
        x_avg = chunk[chunk['gt_df'] == 'X']['Average'].mean() if (chunk['gt_df'] == 'X').any() else None
        y_str = f"{y_avg:.2f}" if y_avg is not None else 'N/A'
        x_str = f"{x_avg:.2f}" if x_avg is not None else 'N/A'

        # Get ID with highest average (among rows above threshold)
        above_threshold = chunk[chunk['Average'] > threshold]
        above_high_threshold = chunk[chunk['Average'] > high_threshhold]
        highest_id = chunk.loc[chunk['Average'].idxmax(), 'ID'] if not chunk.empty else 'N/A'
        ids_above_threshold = above_threshold['ID'].tolist() if not above_threshold.empty else []
        ids_above_high_threshold = above_high_threshold['ID'].tolist() if not above_high_threshold.empty else []

        print(f"Question {i//5 + 1} average: {question_avg:.2f}, Highest Y: {y_max}, Y avg: {y_str}, X avg: {x_str}")
        print(f'Highest ID: {highest_id}')
        print(f'IDs above threshold: {ids_above_threshold}')
        print(f'IDs above high threshold: {ids_above_high_threshold}')
        print("-"*80)

    return averages_df, task_df


def task_analysis(df, gt_df):
    """Run task-related averages analysis and per-question reporting."""
    task_df = prepare_task_df(df)
    averages_df, task_df = report_task_averages(task_df, gt_df)

    return averages_df, df


def calculate_column_averages(df):
    """Compute average numeric score per column.

    Values are either integers 2-4 or strings '1(very bad)'/'5(very good)'.
    Converts everything to numeric then returns a Series of means.
    """
    # helper mapping
    mapping = {
        "1(very bad)": 1,
        "5(very good)": 5
    }
    # attempt to convert each column
    means = {}
    for col in df.columns:
        # map and coerce
        series = df[col].map(mapping).fillna(df[col])
        # try numeric conversion
        numeric = pd.to_numeric(series, errors="coerce")
        if numeric.notna().any():
            means[col] = numeric.mean()
    return pd.Series(means)


def main():
    combined_dfs = []

    for dataset_key, dataset_file in TEST_DATASET.items():
        print(f"\nAnalysis for {dataset_key}: {dataset_file}")
        try:
            df, gt_df = load_data(dataset_file)
            averages_df, original_df = task_analysis(df, gt_df)

            print(gt_df.head())
            if not averages_df.empty:
                output_file = f"{dataset_file}_averages.csv"
                averages_df.to_csv(output_file, index=False)
                print(f"\nAverages exported to {output_file}")
            else:
                print("No task averages found; skipping averages export.")

            combined_dfs.append(original_df)
            print(f"\n{'='*80}\n")

        except FileNotFoundError:
            print(f"Error: CSV file not found at {dataset_file} or GT file at {GT_COLUMN}.")
            continue
        except Exception as e:
            print(f"Error while processing {dataset_file}: {e}")
            continue

    if not combined_dfs:
        print("No datasets were processed successfully.")
        return None

    combined_study_df = pd.concat(combined_dfs, ignore_index=True)
    print("Running combined study execution analysis across all processed datasets...")
    run_study_execution_analysis(combined_study_df, COLUMNS)

    return combined_study_df

if __name__ == "__main__":
    df = main()
