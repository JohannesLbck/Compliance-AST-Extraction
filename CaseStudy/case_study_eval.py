import argparse
import json
from pathlib import Path

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

from TransASTParser import transform


MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DEFAULT_THRESHOLD = 0.6898


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate AST/NL similarity for all JSON files in CaseStudy/Outputs."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("Outputs"),
        help="Directory containing CaseStudy output JSON files.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help="Cosine similarity threshold to count AST/NL as similar.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print only failed AST/NL comparisons.",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_list(data: dict, keys: tuple[str, ...]) -> list[str]:
    for key in keys:
        if key in data and isinstance(data[key], list):
            return data[key]
    return []


def evaluate_file(path: Path, model: SentenceTransformer, threshold: float, verbose: bool = False) -> dict:
    data = read_json(path)

    ast_rules = get_list(data, ("AST_requirements", "ast_requirements"))
    nl_rules = get_list(data, ("NL_requirements", "nl_requirements"))

    pair_count = min(len(ast_rules), len(nl_rules))
    if pair_count == 0:
        return {
            "file": path.name,
            "pairs": 0,
            "similar": 0,
            "percentage": 0.0,
            "skipped": max(len(ast_rules), len(nl_rules)),
            "errors": 0,
        }

    translated_asts: list[str] = []
    transformed_nl: list[str] = []
    errors = 0

    for index in range(pair_count):
        ast_rule = ast_rules[index]
        nl_rule = nl_rules[index]
        try:
            translated = transform(ast_rule)
            translated_asts.append(translated)
            transformed_nl.append(nl_rule)
        except Exception:
            errors += 1

    if not translated_asts:
        return {
            "file": path.name,
            "pairs": pair_count,
            "similar": 0,
            "percentage": 0.0,
            "skipped": abs(len(ast_rules) - len(nl_rules)),
            "errors": errors,
        }

    ast_embeddings = model.encode(translated_asts, convert_to_tensor=True)
    nl_embeddings = model.encode(transformed_nl, convert_to_tensor=True)

    diagonal = cos_sim(ast_embeddings, nl_embeddings).diagonal()

    if verbose:
        printed_header = False
        for index, (ast_text, nl_text) in enumerate(zip(translated_asts, transformed_nl), start=1):
            score = float(diagonal[index - 1].item())
            is_similar = score > threshold
            if is_similar:
                continue
            if not printed_header:
                print(f"\nFailed comparisons for {path.name}:")
                printed_header = True
            print(f"  Comparison {index}:")
            print(f"    AST: {ast_text}")
            print(f"    NL : {nl_text}")
            print(f"    Similarity: {score:.4f} -> NOT SIMILAR")

    similar_count = int((diagonal > threshold).sum().item())
    percentage = (similar_count / len(translated_asts)) * 100

    return {
        "file": path.name,
        "pairs": pair_count,
        "similar": similar_count,
        "percentage": percentage,
        "skipped": abs(len(ast_rules) - len(nl_rules)),
        "errors": errors,
    }


def main() -> None:
    args = parse_args()
    input_dir: Path = args.input_dir
    threshold: float = args.threshold
    verbose: bool = args.verbose

    if not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    json_files = sorted(input_dir.glob("*.json"))
    if not json_files:
        print(f"No JSON files found in: {input_dir}")
        return

    model = SentenceTransformer(MODEL_NAME)

    total_pairs = 0
    total_similar = 0
    total_errors = 0

    print(f"Evaluating {len(json_files)} file(s) in {input_dir} (threshold={threshold})\n")

    for path in json_files:
        result = evaluate_file(path, model, threshold, verbose=verbose)
        total_pairs += result["pairs"]
        total_similar += result["similar"]
        total_errors += result["errors"]

        print(
            f"{result['file']}: "
            f"{result['similar']}/{result['pairs']} similar "
            f"({result['percentage']:.2f}%)"
            f" | transform_errors={result['errors']}"
            f" | pair_mismatch={result['skipped']}"
        )

    overall_percentage = (total_similar / total_pairs * 100) if total_pairs > 0 else 0.0
    print("\n---")
    print(
        f"Overall: {total_similar}/{total_pairs} similar "
        f"({overall_percentage:.2f}%)"
        f" | total_transform_errors={total_errors}"
    )


if __name__ == "__main__":
    main()
