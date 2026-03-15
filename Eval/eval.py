import json
import argparse
from operator import gt
import textdistance as td
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

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
argparse = argparse.ArgumentParser(description='Evaluate combined JSON data.')
argparse.add_argument('--file', type=str, default='Gemini/merged_results.json', help='Path to the combined JSON file')
args = argparse.parse_args()

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
    rule = rule.replace("\"", "\'")
    rule = rule.split(":")[-1].strip()
    rules = smart_split(rule)
    #rules = rule.split(" and ")
    rules = [r.replace(" ", "") for r in rules]
    return rules

def similcheck_with_metric(rule1, rule2, metric_name='damerau_levenshtein', threshold=0.8):
    """Check similarity using specified metric from textdistance library"""
    # Edit distance metrics (return distance, not similarity)
    distance_metrics = {'levenshtein', 'damerau_levenshtein', 'hamming', 'jaro', 'jaro_winkler'}
    
    metric_func = getattr(td, metric_name, None)
    if metric_func is None:
        raise ValueError(f"Unknown metric: {metric_name}")
    
    # For edit distance metrics, use normalized_similarity
    if metric_name in distance_metrics:
        if hasattr(metric_func, 'normalized_similarity'):
            similarity = metric_func.normalized_similarity(rule1, rule2)
        else:
            # Fallback: manually normalize (distance / max_length)
            dist = metric_func(rule1, rule2)
            max_len = max(len(rule1), len(rule2))
            similarity = 1 - (dist / max_len) if max_len > 0 else 1.0
    else:
        similarity = metric_func(rule1, rule2)
    
    return similarity > threshold

def alt_simil_check(rule1, rule2, threshold=0.8):
    """Check similarity using sentence transformers"""
    embeddings1 = model.encode(rule1, convert_to_tensor=True)
    embeddings2 = model.encode(rule2, convert_to_tensor=True)
    similarity = cos_sim(embeddings1, embeddings2)
    return similarity.item() > threshold

def comparison_with_metric(comparison_set, metric_name='damerau_levenshtein', threshold=0.5):
    """Compare datasets using a specific similarity metric from textdistance library"""
    comparisons = sum(range(len(comparison_set)))
    succesful_comparisons_total_strict = 0
    succesful_comparisons_total_simil = 0
    for i in range(len(comparison_set)):
        for j in range(i+1, len(comparison_set)):
            dataset = comparison_set[i]
            other_dataset = comparison_set[j]
            succesful_comparisons_strict = 0
            succesful_comparisons_simil = 0
            for rule in dataset:
                succesful_comparison_strict = False
                succesful_comparison_simil = False
                for other_rule in other_dataset:
                    if rule in other_rule:
                        succesful_comparison_strict = True
                        break  # No need to check further once strict match found
                    elif similcheck_with_metric(rule, other_rule, metric_name, threshold):
                        succesful_comparison_simil = True
                if succesful_comparison_strict:
                    succesful_comparisons_strict += 1
                    succesful_comparisons_simil += 1
                elif succesful_comparison_simil:
                    succesful_comparisons_simil += 1
            if succesful_comparisons_strict > len(dataset)*0.8: #> len(dataset) / 2:
                succesful_comparisons_total_strict += 1
            if succesful_comparisons_simil > len(dataset)*0.8: #> len(dataset) / 2:
                succesful_comparisons_total_simil += 1
    strict_score = succesful_comparisons_total_strict / comparisons if comparisons > 0 else 0
    simil_score = succesful_comparisons_total_simil / comparisons if comparisons > 0 else 0
    return strict_score, simil_score

def main():
    """Main method with support for multiple similarity metrics"""
    data = read_combined_json(args.file)
    # Different similarity metrics to test
    metrics = ['jaccard', 'sorensen_dice', 'cosine', 'levenshtein','damerau_levenshtein', 'jaro_winkler']
    
    for dataset in sorted(DATASETS):
        comparisons_set = []
        for temp in sorted(TEMPERATURES):
            comparisons_set_temperature = []
            for iteration,result in enumerate(data[dataset][temp]):
                FN_counter = 0
                TP_counter = 0
                FP_counter = 0
                drules = []
                ## This is the "in" checking version, if the results are bad, lets copy paste it and make a similarity comparing where everything is the same
                ## but "in" is replaced with the similcheck() function that checks if the rule is similar enough to the GT rule
                for rule in result["data"]:
                    rules = normalize_rules(rule)
                    for r in rules:
                        drules.append(r)
                        if r in GT[dataset]:
                            TP_counter += 1 ## True positive
                        else:
                            FP_counter += 1 ## False positive
                    for gt_r in GT[dataset]:
                        if gt_r not in rules:
                            FN_counter += 1 ## False negative
                comparisons_set.append(drules)
                comparisons_set_temperature.append(drules)
                F1 = 2 * TP_counter / (2 * TP_counter + FP_counter + FN_counter) if (2 * TP_counter + FP_counter + FN_counter) > 0 else 0
                print(f"Dataset: {dataset}, Temperature: {temp}, Iteration: {iteration+1}, TP: {TP_counter}, FP: {FP_counter}, FN: {FN_counter}, F1: {F1:.2f}")
            SC_temperature_strict, SC_temperature_simil = comparison_with_metric(comparisons_set_temperature, metric_name='damerau_levenshtein', threshold=0.75)
            print(f"Strict Similarity Score for {dataset} at temperature {temp}: {SC_temperature_strict:.2f}")
            print(f"Similarity Score for {dataset} at temperature {temp}: {SC_temperature_simil:.2f}")
        SC_strict, SC_simil = comparison_with_metric(comparisons_set, metric_name='damerau_levenshtein', threshold=0.75)
        print(f"\nStrict Similarity Score for {dataset}: {SC_strict:.2f}")
        print(f"Similarity Score for {dataset}: {SC_simil:.2f}")
        
        # Test different similarity metrics
        #print(f"\n=== Similarity Metrics Comparison for {dataset} ===")
        #for metric in metrics:
        #    try:
        #        SC_strict_metric, SC_simil_metric = comparison_with_metric(comparisons_set, metric_name=metric, threshold=0.75)
        #        print(f"{metric.capitalize():20s} - Strict: {SC_strict_metric:.2f}, Similar: {SC_simil_metric:.2f}")
        #    except Exception as e:
        #        print(f"{metric.capitalize():20s} - Error: {e}")
        #print()

if __name__ == "__main__":
    main()
    

