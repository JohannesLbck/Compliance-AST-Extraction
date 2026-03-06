import json
import argparse
from operator import gt
import textdistance as td

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


argparse = argparse.ArgumentParser(description='Evaluate combined JSON data.')
argparse.add_argument('--file', type=str, default='combined.json', help='Path to the combined JSON file')
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

def similcheck(rule1, rule2):
    ## This is a simple similarity check that checks if the two rules are similar enough, we can adjust the threshold as needed
    similarity = td.jaccard(rule1, rule2)
    return similarity > 0.5 ## If the similarity is greater than 0.5, we consider it a match

def comparison(comparison_set):
    comparisons = sum(range(len(comparison_set))) ## This is the number of comparisons we will make, we will compare each dataset with each other dataset, but not with itself
    succesful_comparisons_total_strict = 0
    succesful_comparisons_total_simil = 0
    for i in range(len(comparison_set)):
        for j in range(i+1, len(comparison_set)):
            dataset = comparison_set[i]
            other_dataset = comparison_set[j]
            succesful_comparisons_strict = 0
            succesful_comparisons_simil = 0
            for rule in dataset:
                for other_rule in other_dataset:
                    succesful_comparison_strict = False
                    succesful_comparison_simil = False
                    #print(f"Comparing rule: {rule} with other rule: {other_rule}")
                    if rule in other_rule: # or similcheck(rule, other_rule):
                        #print(f"Rule: {rule} is similar to Other Rule: {other_rule}")
                        succesful_comparison_strict = True
                        break
                    elif similcheck(rule, other_rule):
                        succesful_comparison_simil = True
                if succesful_comparison_strict:
                    succesful_comparisons_strict += 1
                    succesful_comparisons_simil += 1 ## If it's a strict match, it's also a similar match
                elif succesful_comparison_simil:
                    succesful_comparisons_simil += 1
            if succesful_comparisons_strict > len(dataset) / 2: ## If more than 50% of the rules are the same, we consider it a succesful comparison
                succesful_comparisons_total_strict += 1
            if succesful_comparisons_simil > len(dataset) / 2: ## If more than 50% of the rules are similar, we consider it a succesful comparison
                succesful_comparisons_total_simil += 1
    strict_score = succesful_comparisons_total_strict / comparisons if comparisons > 0 else 0
    simil_score = succesful_comparisons_total_simil / comparisons if comparisons > 0 else 0
    return strict_score, simil_score

def main():
    data = read_combined_json(args.file)
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
            SC_temperature_strict, SC_temperature_simil = comparison(comparisons_set_temperature)
            print(f"Strict Similarity Score for {dataset} at temperature {temp}: {SC_temperature_strict:.2f}")
            print(f"Similarity Score for {dataset} at temperature {temp}: {SC_temperature_simil:.2f}")
        SC_strict, SC_simil = comparison(comparisons_set)
        print(f"\nStrict Similarity Score for {dataset}: {SC_strict:.2f}")
        print(f"Similarity Score for {dataset}: {SC_simil:.2f}")            

if __name__ == "__main__":
    main()
    

