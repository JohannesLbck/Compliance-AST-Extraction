import argparse
import json
from pathlib import Path


def main():
    # -----------------------
    # Argument parsing
    # -----------------------

    parser = argparse.ArgumentParser(
        description="Evaluate extracted requirement AST outputs"
    )

    parser.add_argument(
        "dataset",
        type=str,
        help="Dataset name (e.g. winter, bpmq, pcl)"
    )

    args = parser.parse_args()
    dataset = args.dataset

    # -----------------------
    # Load model output file
    # -----------------------

    output_file = Path(f"outputs/{dataset}_output.json")

    if not output_file.exists():
        raise FileNotFoundError(
            f"Output file not found: {output_file.resolve()}"
        )

    with output_file.open(encoding="utf-8") as f:
        output_data = json.load(f)

    if "results" not in output_data or not isinstance(output_data["results"], list):
        raise ValueError("Invalid output format: 'results' list not found")

    results = output_data["results"]

    # -----------------------
    # Load ground truth file
    # -----------------------

    gt_file = Path("gt") / f"{dataset}.json"

    if not gt_file.exists():
        raise FileNotFoundError(
            f"Ground truth file not found: {gt_file.resolve()}"
        )

    with gt_file.open(encoding="utf-8") as f:
        ground_truth = json.load(f)

    # -----------------------
    # Debug output (temporary)
    # -----------------------

    print(f"Dataset: {dataset}")
    print(f"Loaded model outputs: {len(results)} runs")

    if isinstance(ground_truth, dict):
        print(f"Ground truth keys: {list(ground_truth.keys())}")
    elif isinstance(ground_truth, list):
        print(f"Ground truth entries: {len(ground_truth)}")
    else:
        print("Ground truth loaded")

    if results:
        print("\nFirst output entry keys:")
        print(results[0].keys())


if __name__ == "__main__":
    main()

