"""
Exploratory analysis script for TestingTemplate.csv survey data
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Configuration
CSV_FILE = Path(__file__).parent / "TestingTemplate.csv"

# Columns to remove from analysis
COLUMNS_TO_REMOVE = {
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


    

def load_data():
    """Load CSV file with semicolon delimiter"""
    print(f"Loading data from: {CSV_FILE}")
    df = pd.read_csv(CSV_FILE, delimiter=";")
    return df

def print_basic_info(df):
    """Print basic information about the dataset"""
    print("\n" + "="*80)
    print("BASIC DATASET INFORMATION")
    print("="*80)
    print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"\nData types:\n{df.dtypes}")

def remove_unnecessary_columns(df):
    """Remove columns that are not needed for analysis using COLUMNS_TO_REMOVE config"""
    # Flatten all column names from the dictionary
    columns_to_remove = []
    for category, col_list in COLUMNS_TO_REMOVE.items():
        columns_to_remove.extend(col_list)
    
    # Also remove columns containing "Optional"
    columns_to_remove.extend([col for col in df.columns if "Optional" in col])
    
    # Remove duplicates and filter to only existing columns
    columns_to_remove = list(set(columns_to_remove))
    columns_to_remove = [col for col in columns_to_remove if col in df.columns]
    
    if columns_to_remove:
        df = df.drop(columns=columns_to_remove)
    
    return df


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
    try:
        df = load_data()
        df = remove_unnecessary_columns(df)
        print_basic_info(df)

        # calculate and display column averages
        averages = calculate_column_averages(df)
        total_average = averages.mean()
        print(f"\nOverall average score across all columns: {total_average:.2f}")
        if not averages.empty:
            print("\n" + "="*80)
            print("COLUMN AVERAGES")
            print("="*80)
            print(averages.to_string())
        
        return df
        
    except FileNotFoundError:
        print(f"Error: CSV file not found at {CSV_FILE}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    df = main()
