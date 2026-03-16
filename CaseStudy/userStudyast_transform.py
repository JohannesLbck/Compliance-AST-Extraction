import ast
from TransASTParser import transform
from fuzzywuzzy import fuzz
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


#model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')




def simil_comparison(str1, str2):
    ratio = fuzz.ratio(str1, str2)
    return ratio > 80

def semantic_string_comparison(str1, str2):
    embedding1 = model.encode(str1)
    print("reached embedding1")
    embedding2 = model.encode(str2)
    print("reached embedding2")
    simil = model.similarity(embedding1, embedding2)
    print(simil)
    return simil

AST_FUNCTIONS = {
    "exists",
    "absence",
    "leads_to",
    "precedence",
    "leads_to_absence",
    "precedence_absence",
    "parallel",
    "executed_by",
    "executed_by_identify",
    "executed_by_return",
    "directly_follows",
    "send_exist",
    "receive_exist",
    "activity_sends",
    "activity_receives",
    "min_time_between",
    "by_due_date",
    "recurring",
    "max_time_between",
    "data_value_alternative_directly_follows",
    "data_value_alternative_eventually_follows",
    "condition_directly_follows",
    "condition_eventually_follows",
    "data_leads_to_absence",
    "loop",
    "timed_alternative",
    "failure_directly_follows",
    "failure_eventually_follows",
}


class TreeArgInjector(ast.NodeTransformer):
    def visit_Call(self, node):
        node = self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id in AST_FUNCTIONS:
            has_tree = (
                len(node.args) > 0
                and isinstance(node.args[0], ast.Name)
                and node.args[0].id == "tree"
            )
            if not has_tree:
                node.args.insert(0, ast.Name(id="tree", ctx=ast.Load()))
        return node


def parse_req(string):
    expr = ast.parse(string, mode="eval")
    transformed = TreeArgInjector().visit(expr)
    ast.fix_missing_locations(transformed)
    return ast.unparse(transformed)

def main() -> None:
    ## Fill these with the ones from the user study that are above the higher threshhold
    ASTS = {
        "condition_eventually_follows(tree, 'respondentBankEvaluation == \"fail\"', 'Add to black list')": "If the respondent bank evaluation fails, it must be added to a black list.",
        "condition_eventually_follows('not respondentBankEvaluation', 'Add to black list')": "If the respondent bank evaluation fails, it must be added to a black list.",
        "condition_eventually_follows(tree, \"respondentBankEvaluation == 'fail'\", 'add respondent bank to black list')": "If the respondent bank evaluation fails, it must be added to a black list.",
        "condition_eventually_follows('risk == \"low\"', 'Open account')": "Opening an account must be of low risk.",
        "condition_eventually_follows( 'isFirstTime', 'Conduct advanced due diligence study')": "If it is the first time to deal with the respondent bank, an advanced due diligence study must be conducted.",
        "condition_eventually_follows( \"firstTime\", 'Conduct advanced due diligence study')": "If it is the first time to deal with the respondent bank, an advanced due diligence study must be conducted.",
        "condition_eventually_follows( \"firstTimeDeal\", 'Conduct Advanced Due Diligence Study')": "If it is the first time to deal with the respondent bank, an advanced due diligence study must be conducted.",
        "data_leads_to_absence(tree, \"respondentBankCertificate == 'invalid'\", 'Open Account')": "Before opening an account, the respondent bank certificate must be valid.",
        "(executed_by( 'check customer bank privilege', 'credit broker') or executed_by('check customer bank privilege', 'supervisor')) and executed_by( 'check credit worthiness', 'post-processing clerk') and not(executed_by_return('check customer bank privilege') == executed_by_return( 'check credit worthiness'))": "The activity 'customer bank privilege check' (to be performed by credit broker or supervisor) should be segregated from 'credit worthiness check' (to be performed by post-processing clerk).",
        "condition_eventually_follows( 'credit > 1000000', 'check credit worthiness') and executed_by( 'check credit worthiness', 'clerk supervisor') and failure_directly_follows( 'check credit worthiness', 'create suspense file') and failure_eventually_follows( 'create suspense file', 'notify manager')": "If the loan request's credit exceeds 1 million Euro (1M e) the clerk supervisor checks the credit worthiness of the customer. The lack of the supervisor check immediately creates a suspense file. In case of failure of the creation of a suspense file, the manager is notified by the system.",
        "leads_to(\"production action\",\"quality check\") and precedence(\"delivery\",\"quality check\")": "After each production action a quality check has to be performed prior to delivery.",
        "leads_to( 'Perform Production Action', 'Perform Quality Check') and precedence( 'Deliver', 'Perform Quality Check')": "After each production action a quality check has to be performed prior to delivery.",
        "(precedence( 'Close Order', 'Record Payment') or precedence( 'Close Order', 'Record Rejection')) and leads_to( receive_exist( 'payment'), 'Report Payment')": "Before an order is being closed, either records of payments made or records of the fact that the order was rejected have to be taken. Each payment received shall be reported.",
        "precedence(tree, 'close order', 'record payment') or precedence(tree, 'close order', 'record rejection') and leads_to(tree, receive_exist(tree, 'paymentData'), 'report payment')": "Before an order is being closed, either records of payments made or records of the fact that the order was rejected have to be taken. Each payment received shall be reported.",
        "leads_to('Fill Order', 'Ship') and leads_to('Fill Order', 'Send Invoice')": "When an order is filled, a product has to be shipped and an invoice has to be sent.",
        "leads_to( 'perform_identity_check', 'retain_identity_check_history')": "Retain history of identity checks performed.",
        "leads_to( 'scan_customer', 'retain_history') and send_exist( 'identityCheckHistory')": "Retain history of identity checks performed.",
        "recurring('check DMS', '10518984 ') and activity_receives('check DMS', 'completedandsignedChecklist')": "Every four months, it is necessary to check whether a new document has been uploaded to the Document Management System (DMS) that contains the checklist completed and signed by the Tax Manager and the Financial Controller",
        "(condition_eventually_follows( 'resolutionProposal and reportCb and reportLd', 'Analyse Reports') and executed_by( 'Analyse Reports', executed_by_return( 'Create Resolution Proposal')))": "If the resolution proposal has been created and the respective reports from the CB and the LD are available, then such reports must be eventually analysed by the same person who created the resolution proposal",
        "condition_eventually_follows( 'resolutionProposal and cbReport and ldReport', 'Analyse reports') and executed_by( 'Analyse reports', executed_by_return( 'Create resolution proposal'))": "If the resolution proposal has been created and the respective reports from the CB and the LD are available, then such reports must be eventually analysed by the same person who created the resolution proposal",
        "condition_eventually_follows( 'resolutionProposal and reportCb and reportLd', 'analyse reports') and executed_by( 'analyse reports', executed_by_return( 'create resolution proposal'))": "If the resolution proposal has been created and the respective reports from the CB and the LD are available, then such reports must be eventually analysed by the same person who created the resolution proposal"
    }

    translated_asts = []
    nl_requirements = []
    for ast_rule, nl_text in ASTS.items():
        print(f"Translating AST: {ast_rule}")
        ast_rule = parse_req(ast_rule)
        print(f"Parsed AST: {ast_rule}")
        result = transform(ast_rule)
        translated_asts.append(result)
        nl_requirements.append(nl_text)
        print(f"Result: {result}\n")

    print(translated_asts)
    astembeddings = model.encode(translated_asts)
    nlembeddings = model.encode(nl_requirements)
    avg = cos_sim(astembeddings, nlembeddings).diagonal().mean().item()
    total = 0
    for i in range(len(translated_asts)):
        print(f"Comparing AST requirement {translated_asts[i]} with NL requirement {nl_requirements[i]}:")
        simil = cos_sim(astembeddings[i], nlembeddings[i])
        total += simil
        if simil > 0.7:
            print(f"AST and NL requirement {i} are similar based on semantic string comparison.")
        else:
            print(f"AST and NL requirement {i} are NOT similar based on semantic string comparison.")
    print(cos_sim(astembeddings[0], nlembeddings[0]))
    print(f"Average similarity (diagonal): {avg:.4f}")
    print(f"Average similarity: {total.item() / len(translated_asts):.4f}")
 
		


if __name__ == "__main__":
    main()
