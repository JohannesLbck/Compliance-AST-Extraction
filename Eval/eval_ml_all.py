import json
import torch
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import argparse

DATASETS={"bpmq", "crl", "haar", "pcl", "ppsl", "status", "sun", "zasada"}
TEMPERATURES = {"0.1", "0.3", "0.5", "0.7"}
## Contains the pure patterns normalized from the user study identified validated encodings
GT = {
    "bpmq": [
        "leads_to(tree, receive_exist(tree, 'respondentBankReport'), 'Analyze respondent bank report')",
        "condition_eventually_follows('not data.evaluation', 'add respondent bank to blacklist')",
        "condition_eventually_follows(tree, 'respondentBankEvaluation == \"fail\"', 'Add to black list')",
        "condition_eventually_follows(tree, 'respondentBankEvaluation == \"fail\"', 'Add to black list')",
        "condition_eventually_follows('not respondentBankEvaluation', 'Add to black list')",
        "condition_eventually_follows(tree, \"respondentBankEvaluation == 'fail'\", 'add respondent bank to black list')",
        "condition_eventually_follows('not risk ', 'Open account')",
        "condition_eventually_follows('risk == \"low\"', 'Open account')",
        "condition_eventually_follows( 'isFirstTime', 'Conduct advanced due diligence study')",
        "condition_eventually_follows( \"firstTime\", 'Conduct advanced due diligence study')",
        "condition_eventually_follows(tree, \"isFirstTimeDealing\", 'conduct advanced due diligence study')",
        "condition_eventually_follows( \"firstTimeDeal\", 'Conduct Advanced Due Diligence Study')",
        "data_leads_to_absence(tree, 'respondentBankRating == \"rejected\"', 'Open account')",
        "data_leads_to_absence( 'respondentBankRating == \"rejected\"', 'Open account')",
        "data_leads_to_absence(tree, 'status == \"rejected\"', 'Open account')",
        "data_leads_to_absence(tree, \"respondentBankCertificate == 'invalid'\", 'Open Account')",
        "not condition_eventually_follows(tree, \"respondentBankCertificate == 'invalid'\", 'Open Account')",
        "condition_eventually_follows(tree, \"respondentBankCertificate == 'valid'\", 'Open Account')",
    ],
    "crl": [
        "parallel('send automated email', 'collect data') and executed_by('collect data', 'credit bureau service')",
        "executed_by( 'collect personal data', 'credit bureau service') and activity_sends('collect personal data', 'automatedEmailNotification')",
        "executed_by( 'collect personal data', 'credit bureau service') and leads_to( 'collect personal data', receive_exist(tree, 'automatedEmailNotification'))",
        "activity_receives( 'collect personal data', 'personalData') and executed_by('collect personal data', 'credit bureau service') and leads_to( 'collect personal data', 'receive automated email notification')",
        "directly_follows( 'check customer bank privilege', 'check credit worthiness') and leads_to( 'check credit worthiness', 'determine risk level')",
        "precedence('evaluate loan risk', 'customer bank privilege check') and precedence('evaluate loan risk', 'check credit worthiness') and leads_to('customer bank privilege check', 'check credit worthiness')",
        "directly_follows(tree, 'check_customer_bank_privilege', 'check_credit_worthiness') and precedence(tree, 'determine_loan_risk_level', 'check_credit_worthiness')",
        "(executed_by( 'check customer bank privilege', 'credit broker') or executed_by('check customer bank privilege', 'supervisor')) and executed_by( 'check credit worthiness', 'post-processing clerk') and not(executed_by_return('check customer bank privilege') == executed_by_return( 'check credit worthiness'))",
        "(executed_by( 'customer bank privilege check', 'credit broker') or executed_by( 'customer bank privilege check', 'supervisor')) and executed_by( 'credit worthiness check', 'post-processing clerk')",
        "(executed_by(tree, 'check bank privilege', 'credit broker') or executed_by(tree, 'check bank privilege', 'supervisor')) and executed_by(tree, 'check credit worthiness', 'post-processing clerk')",
        "executed_by( 'check risk', 'branch office manager') and (leads_to( 'check risk', 'approve request') or leads_to( 'check risk', 'reject request'))",
        "executed_by( 'check risk', 'branch office manager') and (leads_to( 'check risk', 'approve request') or leads_to( 'check risk', 'reject request'))",
        "executed_by( 'checkRisks', 'branch office manager') and condition_eventually_follows('risksAcceptable', 'approveRequest') and condition_eventually_follows('not risksAcceptable', 'rejectRequest')",
        "condition_eventually_follows( 'credit > 1000000', 'check credit worthiness') and executed_by( 'check credit worthiness', 'clerk supervisor') and failure_eventually_follows(tree, 'create suspense file', 'notify manager')",
        "condition_eventually_follows(\"credit > 1000000\", \"check credit worthiness\") and executed_by(\"check credit worthiness\", \"clerk supervisor\") and failure_eventually_follows(\"create suspense file\", send_exist(\"managerNotification\"))",
        "condition_eventually_follows( 'credit > 1000000', 'check credit worthiness') and executed_by( 'check credit worthiness', 'clerk supervisor') and failure_directly_follows( 'check credit worthiness', 'create suspense file') and failure_eventually_follows( 'create suspense file', 'notify manager')",
        "data_leads_to_absence(tree, \"customerGold and credit < 1000000\", \"evaluate loan risk\")",
        "condition_eventually_follows(tree, 'customerStatus != \"gold\"', 'check_banking_privileges') and data_leads_to_absence(tree, 'customerStatus == \"gold\" and loanCredit < 1000000', 'evaluate_loan_risk')",
        "data_leads_to_absence(tree, \"customerStatus == 'gold' and creditAmount < 1000000\", 'evaluate loan risk')",
        "data_leads_to_absence(tree, 'trustedGold and creditAmount < 1000000', 'evaluate loan risk')",
        "not condition_eventually_follows('data.customer_status == gold && data.loan_amount < 1000000','evaluate loan risk','global')",
    ],
    "haar": [
        "precedence( \"close_order\", send_exist( \"receivedOrderRecord\"))",
        "precedence( 'Close Order', 'Record Order')",
        "precedence( 'close order', send_exist( 'receivedOrderRecord'))",
        "precedence(\"close order\",\"record received order\")",
        "leads_to( \"Perform Production Action\", \"Perform Quality Check\") and precedence( \"Deliver\", \"Perform Quality Check\")",
        "leads_to(\"production action\",\"quality check\") and precedence(\"delivery\",\"quality check\")",
        "leads_to( \"production_action\", \"perform_quality_check\") and precedence( \"deliver\", \"perform_quality_check\")",
        "leads_to( 'Perform Production Action', 'Perform Quality Check') and precedence( 'Deliver', 'Perform Quality Check')",
        "(precedence( 'Close Order', 'Record Payment') or precedence( 'Close Order', 'Record Rejection')) and leads_to( receive_exist( 'payment'), 'Report Payment')",
        "precedence(tree, 'close order', 'record payment') or precedence(tree, 'close order', 'record rejection') and leads_to(tree, receive_exist(tree, 'paymentData'), 'report payment')",
        "leads_to('Fill Order', 'Ship') and leads_to('Fill Order', 'Send Invoice')",
        "leads_to( 'Fill Order', send_exist( 'product')) and leads_to( 'Fill Order', send_exist( 'invoice'))",
    ],
    "pcl": [
        "leads_to( 'perform_identity_check', 'retain_identity_check_history')",
        "leads_to( receive_exist( 'newCustomer'), 'perform_identity_check')",
        "condition_eventually_follows('data.state == \"new\"', 'identity check')",
        "leads_to( \"scan_new_customer\", \"retain_identity_check\") and activity_sends( \"retain_identity_check\", \"identityCheckHistory\")",
        "leads_to( 'scan_customer', 'retain_history') and send_exist( 'identityCheckHistory')",
        "condition_eventually_follows(tree, '(accountBalance > 0) or (isApprovedByManager == true) or (customerType == \"VIP\")', 'End Activity')",
    ],
    "ppsl": [],
    "status": [
        "max_time_between(tree, \"Check Document\", \"Check Document\", 4) and activity_receives(tree, \"Check Document\", \"signedChecklist\")",
        "recurring('check DMS', '10518984 ') and activity_receives('check DMS', 'completedandsignedChecklist')",
        "(condition_eventually_follows( 'resolutionProposal and reportCb and reportLd', 'Analyse Reports') and executed_by( 'Analyse Reports', executed_by_return( 'Create Resolution Proposal')))",
        "condition_eventually_follows( 'resolutionProposal and cbReport and ldReport', 'Analyse Report') and (executed_by_return( 'Create Resolution Proposal') == executed_by_return( 'Analyse Report'))",
        "condition_eventually_follows( 'resolutionProposal and cbReport and ldReport', 'Analyse reports') and executed_by( 'Analyse reports', executed_by_return( 'Create resolution proposal'))",
        "condition_eventually_follows( 'resolutionProposal and reportCb and reportLd', 'analyse reports') and executed_by( 'analyse reports', executed_by_return( 'create resolution proposal'))",
    ],
    "sun": [],
    "zasada": []
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
THRESHOLD = 0.75
parser = argparse.ArgumentParser(description="Evaluate ML-generated rules against GT with embedding-based similarity.")
parser.add_argument("--threshold", type=float, default=THRESHOLD, help="Cosine similarity threshold for considering a match between predicted and GT rules.")
args = parser.parse_args()
THRESHOLD = args.threshold


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
    if not target_list:
        return False
    a = embed_map[rule]
    # build tensor for targets
    target_tensors = torch.stack([embed_map[t] for t in target_list])
    sims = cos_sim(a, target_tensors)  # shape [1, n]
    return torch.any(sims > threshold)


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
        gt_entry = GT.get(dataset)
        gt_rules = set()
        if isinstance(gt_entry, dict):
            for rule in gt_entry.keys():
                gt_rules.update(normalize_rules(rule))
        elif isinstance(gt_entry, list):
            for rule in gt_entry:
                gt_rules.update(normalize_rules(rule))


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
                    # count false negatives: no extracted rule matches this GT rule
                    matched = False
                    #if gt_r in embed_map:
                    gt_tensor = embed_map[gt_r]
                    if predicted_rules:
                        preds_t = torch.stack([embed_map[p] for p in predicted_rules])
                        sims = cos_sim(gt_tensor, preds_t)
                        #sims = model.similarity(gt_tensor, preds_t)
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
