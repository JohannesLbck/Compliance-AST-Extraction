import json
import torch
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

DATASETS={"bpmq", "crl", "haar", "pcl", "ppsl", "status", "sun", "zasada"}
TEMPERATURES = {"0.1", "0.3", "0.5", "0.7"}
## Contains the pure patterns normalized from the user study identified validated encodings
GT = {
    "bpmq": {},
    "crl": {},
    "haar": {},
    "pcl": {},
    "ppsl": {},
    "status": {},
    "sun": {},
    "zasada": {}
}

# Use the same multilingual MiniLM model as in the original eval.py
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

# Files to iterate over
FILES = [
    'Gemini/merged_results.json',
    'Sonnet/merged_results.json',
    'GPT/merged_results.json'
]

# Default cosine similarity threshold
THRESHOLD = 0.9


def read_combined_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


def smart_split(rule):
    depth = 0
    parts = []
    current = ""
    i = 0
    while i < len(rule):
        if rule[i] == '(':
            depth += 1
            current += rule[i]
        elif rule[i] == ')':
            depth -= 1
            current += rule[i]
        elif rule[i:i+5] == " and " and depth == 0:
            parts.append(current)
            current = ""
            i += 4
        else:
            current += rule[i]
        i += 1
    if current:
        parts.append(current)
    return parts


def normalize_rules(rule):
    rule = rule.lower()
    rule = rule.replace("-", "")
    rule = rule.replace("_", "")
    rule = rule.replace("/", "")
    rule = rule.replace("\\{", "")
    rule = rule.replace("\\}", "")
    rule = rule.replace('"', "'")
    rule = rule.split(":")[-1].strip()
    rules = smart_split(rule)
    rules = [r.replace(" ", "") for r in rules]
    return rules


def build_embedding_map(strings):
    """Given an iterable of unique strings, return a dict mapping string->tensor embedding."""
    unique_list = list(strings)
    if not unique_list:
        return {}
    embeddings = model.encode(unique_list, convert_to_tensor=True)
    return {s: embeddings[i] for i, s in enumerate(unique_list)}


def is_similar_to_any(rule, target_list, embed_map, threshold):
    """Return True if rule embedding has cosine similarity > threshold with any entry in target_list."""
    if rule not in embed_map:
        return False
    if not target_list:
        return False
    a = embed_map[rule]
    # build tensor for targets
    target_tensors = torch.stack([embed_map[t] for t in target_list])
    sims = cos_sim(a, target_tensors)  # shape [1, n]
    return torch.any(sims > threshold).item()


def compare_sets_embeddings(comparison_set, embed_map, threshold=0.9):
    """Compare multiple sets of rules using precomputed embeddings.
    comparison_set: list of lists (each inner list are normalized rule strings)
    Returns a single similarity score representing fraction of dataset-pairs
    where >80% of rules in one set have a match in the other set.
    """
    n = len(comparison_set)
    comparisons = sum(range(n))
    succesful_comparisons_total = 0

    for i in range(n):
        for j in range(i+1, n):
            A = comparison_set[i]
            B = comparison_set[j]
            if not A or not B:
                continue
            # stack tensors for A and B
            A_tensors = torch.stack([embed_map[a] for a in A])
            B_tensors = torch.stack([embed_map[b] for b in B])
            # compute similarity matrix [len(A), len(B)]
            sim_matrix = cos_sim(A_tensors, B_tensors)
            # for each row (rule in A) check if any value > threshold
            row_matches = torch.any(sim_matrix > threshold, dim=1)
            successful = int(torch.sum(row_matches).item())
            if successful > len(A) * 0.8:
                succesful_comparisons_total += 1

    score = succesful_comparisons_total / comparisons if comparisons > 0 else 0.0
    return score


def evaluate_file(path, threshold=THRESHOLD):
    data = read_combined_json(path)

    for dataset in sorted(DATASETS):
        # collect all comparison sets across temperatures so we can embed rules once per dataset
        comparisons_all = []
        comparisons_by_temp = {t: [] for t in sorted(TEMPERATURES)}
        unique_rules = set()
        gt_rules = set(GT[dataset].keys()) if GT.get(dataset) else set()

        for temp in sorted(TEMPERATURES):
            for iteration, result in enumerate(data[dataset][temp]):
                drules = []
                for rule in result["data"]:
                    rules = normalize_rules(rule)
                    for r in rules:
                        drules.append(r)
                comparisons_all.append(drules)
                comparisons_by_temp[temp].append(drules)
                unique_rules.update(drules)

        # include GT rules into the embedding set
        unique_rules.update(gt_rules)

        # build embeddings once for this dataset
        embed_map = build_embedding_map(unique_rules)

        print(f"\nEvaluating file: {path} - Dataset: {dataset}")

        # Evaluate per-iteration F1 using embedding-based GT matching
        for temp in sorted(TEMPERATURES):
            for iteration, result in enumerate(data[dataset][temp]):
                FN_counter = 0
                TP_counter = 0
                FP_counter = 0
                predicted_rules = []
                for rule in result["data"]:
                    rules = normalize_rules(rule)
                    for r in rules:
                        predicted_rules.append(r)
                        if is_similar_to_any(r, list(gt_rules), embed_map, threshold):
                            TP_counter += 1
                        else:
                            FP_counter += 1
                for gt_r in gt_rules:
                    # count false negatives: no predicted rule matches this GT rule
                    matched = False
                    if gt_r in embed_map:
                        gt_tensor = embed_map[gt_r]
                        if predicted_rules:
                            preds_t = torch.stack([embed_map[p] for p in predicted_rules])
                            sims = cos_sim(gt_tensor, preds_t)
                            if torch.any(sims > threshold):
                                matched = True
                    if not matched:
                        FN_counter += 1
                F1 = 2 * TP_counter / (2 * TP_counter + FP_counter + FN_counter) if (2 * TP_counter + FP_counter + FN_counter) > 0 else 0
                print(f"Dataset: {dataset}, Temperature: {temp}, Iteration: {iteration+1}, TP: {TP_counter}, FP: {FP_counter}, FN: {FN_counter}, F1: {F1:.2f}")

            # per-temperature comparison score using embeddings
            SC_temperature = compare_sets_embeddings(comparisons_by_temp[temp], embed_map, threshold)
            print(f"Similarity Score for {dataset} at temperature {temp}: {SC_temperature:.2f}")

        # overall score across all temperatures/iterations
        SC_overall = compare_sets_embeddings(comparisons_all, embed_map, threshold)
        print(f"\nSimilarity Score for {dataset}: {SC_overall:.2f}\n")


if __name__ == "__main__":
    for f in FILES:
        evaluate_file(f, threshold=THRESHOLD)
