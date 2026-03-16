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
        gt_rules_normalized = []
        for gt_rule in GT[dataset]:
            gt_rules_normalized.extend(normalize_rules(gt_rule))

        for temp in sorted(TEMPERATURES):
            comparisons_set_temperature = []
            for iteration,result in enumerate(data[dataset][temp]):
                FN_counter = 0
                TP_counter = 0
                FP_counter = 0
                drules = []
                ## This is the "in" checking version, if the results are bad, lets copy paste it and make a similarity comparing where everything is the same
                ## but "in" is replaced with the similcheck() function that checks if the rule is similar enough to the GT rule
                rules_full = []
                for rule in result["data"]:
                    rules = normalize_rules(rule)
                    for r in rules:
                        rules_full.append(r)
                        drules.append(r)
                        matched_gt = any(
                            similcheck_with_metric(
                                r,
                                gt_r,
                                metric_name='damerau_levenshtein',
                                threshold=0.75,
                            )
                            for gt_r in gt_rules_normalized
                        )
                        if matched_gt:
                            TP_counter += 1 ## True positive
                        else:
                            FP_counter += 1 ## False positive
                for gt_r in gt_rules_normalized:
                    matched_pred = any(
                        similcheck_with_metric(
                            gt_r,
                            pred_r,
                            metric_name='damerau_levenshtein',
                            threshold=0.75,
                        )
                        for pred_r in rules_full
                    )
                    if not matched_pred:
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
    

