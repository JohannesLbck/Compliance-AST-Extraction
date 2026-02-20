from google import genai
from pydantic import BaseModel, Field
from typing import Dict, List
from pathlib import Path
import argparse
import json

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()


class RequirementsModel(BaseModel):
    requirements: Dict[str, str] = Field(..., description="Requirement ASTs")


def main():
    # -----------------------
    # Argument parsing
    # -----------------------
    parser = argparse.ArgumentParser(
        description="Extract requirement ASTs from predefined text datasets"
    )

    parser.add_argument(
        "textselector",
        type=str,
        choices=TEXT_MAPPING.keys(),
        help="Text dataset selector (e.g., winter, bpmq, pcl, etc.)"
    )

    parser.add_argument(
        "--range",
        type=int,
        default=1,
        help="Number of times to generate content (default=1)"
    )

    args = parser.parse_args()

    text_selector = args.textselector
    repeat = args.range

    text = TEXT_MAPPING[text_selector]

    # -----------------------
    # Load method documentation
    # -----------------------
    doc = Path("../methods_doc_concise.md").read_text(encoding="utf-8") ## Shortened version of the documentation to fit within token limits
    #doc = Path("../methods_doc.md").read_text(encoding="utf-8") ## Full version of the documentation
    # -----------------------
    # Prepare prompt
    # -----------------------
    prompt = (
        "TASK: COMPLIANCE REQUIREMENT EXTRACTION\n"
        "Extract business process requirements from natural language text and convert them\n"
        "into formal compliance pattern AST (Abstract Syntax Tree) expressions.\n\n"

        "OUTPUT FORMAT\n"
        "Each requirement must be formatted as: R{NUMBER}: <AST expression>\n"
        "Example: R1: leads_to(tree, 'submit application', 'review application')\n"
        "Example: R2: executed_by(tree, 'approve request', 'manager')\n\n"
        
        "1. SYSTEM PERSPECTIVE: Model requirements from the system's viewpoint, NOT external actors.\n"
        "   - If a customer receives an email, the system sent it.\n"
        "   - Use send_exist() for outgoing data, receive_exist() for incoming data.\n\n"

        "2. ACTIVITY LABELS:\n"
        "   - Use active voice without articles (a, the).\n"
        "   - Examples: 'approve request', 'scan document', 'send email' (NOT 'the approval', 'a scan').\n"
        "   - NEVER include resource names in activity labels.\n\n"

        "3. RESOURCE SPECIFICATION:\n"
        "   - ALWAYS use executed_by(tree, 'activity', 'resource') pattern.\n"
        "   - Resources must be specified separately from activity names.\n"
        "   - ✗ WRONG:  executed_by(tree, 'manager approves request', 'manager')\n"
        "   - ✓ RIGHT:  executed_by(tree, 'approve request', 'manager')\n\n"

        "4. DATA OBJECT NAMING:\n"
        "   - Use camelCase for all data object names.\n"
        "   - Examples: 'customerData', 'loanApplication', 'emailNotification'.\n\n"

        "5. DESIGN TIME PERSPECTIVE:\n"
        "   - Rules are from the design time perspective. This means that a disjunction in the natural language can lead to a conjunction of patterns, if both patterns have to exist in the process\n"
        "   - Example: 'Before a process ends, the order has to either be delivered or rejected'.\n"
        "   - ✗ WRONG: precedence('End Activity', 'deliverOrder') or precedence('End Activity', 'rejectOrder')\n"
        "   - ✓ RIGHT: leads_to('deliverOrder', 'End Activity') and leads_to('rejectOrder', 'End Activity') and exists('deliverOrder') and exists('rejectOrder')\n\n"
        "   - This is not always the case as the natural language can also be describing different options of a compliant process in which case a disjunction of patterns would be correct.'.\n"

        "TIME HANDLING\n"
        "- Encode as integer seconds whenever possible.\n"
        "  Example: 7 working days = 604800 seconds\n"
        "- For non-specific or complex times, use descriptive strings.\n"
        "  Example: 'predefined period', 'business hours'\n"
        "- Special keywords:\n"
        "  * 'Start Activity' = process start event\n"
        "  * 'End Activity' = process end event\n"
        "  * 'terminate' = immediately stop/end process\n\n"

        "DATA PATTERNS (CRITICAL)\n"
        "Use send_exist() and receive_exist() instead of embedding data in activity labels.\n\n"
        "However, do not use data existence patterns for physical objects. A product being shipped should be modeled as activities, not data objects.\n\n"
        "Finnaly, if a dataobject should stay in a certain domain, then conditional checks should prevent it from leaving the domain.\n\n"
        "E.g., if a bank account should not have a negative balance, then the condition 'accountBalance >= withdrawalAmount' should be used to prevent unallowed withdrawals\n\n"

        "SYSTEM PERSPECTIVE EXAMPLES:\n"
        "  NL: 'Customer receives email notification'\n"
        "  ✗ WRONG: receive_exist(tree, 'emailNotification')\n"
        "  ✓ RIGHT: send_exist(tree, 'emailNotification')\n\n"

        "  NL: 'System receives payment confirmation'\n"
        "  ✗ WRONG: send_exist(tree, 'paymentConfirmation')\n"
        "  ✓ RIGHT: receive_exist(tree, 'paymentConfirmation')\n\n"

        "DATA CONDITIONS:\n"
        "- Use operators: not, or, ==, and, >, <, >=, <=\n"
        "- Format: dataObjectName operator value\n"
        "- Examples: 'loanAmount > 1000000', 'customerStatus == \"gold\"', 'riskScore < 50'\n"
        "- Combine with parentheses: '(loanAmount > 1000000) and (customerStatus == \"gold\")'\n\n"

        "FAILURE PATTERNS (USE WITH CARE)\n"
        "ONLY use failure_* patterns when an activity itself fails (system cannot execute it).\n"
        "Do NOT use for negative condition results.\n\n"

        "✗ WRONG USAGE:\n"
        "  NL: 'If eligibility check fails, deny application'\n"
        "  ✗ failure_eventually_follows(tree, 'eligibility check', 'deny application')\n"
        "  REASON: The check ran successfully; the result was just negative.\n"
        "  ✓ RIGHT: condition_eventually_follows(tree, 'checkFailed == true', 'deny application')\n\n"

        "✓ CORRECT USAGE:\n"
        "  NL: 'If system fails to send email, retry after 5 minutes'\n"
        "  ✓ failure_eventually_follows(tree, 'send email', 'retry sending')\n"
        "  REASON: The system cannot execute 'send email' (actual failure).\n\n"

        "COMPLIANCE PATTERN REFERENCE\n"
        f"{doc}\n\n"
        "TEXT TO EXTRACT FROM\n"
        f"{text}"
    )

    # -----------------------
    # Collect all responses
    # -----------------------
    results: List[Dict] = []

    for i in range(repeat):
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": RequirementsModel.model_json_schema()
            }
        )

        # Parse response JSON and append to results
        results.append(json.loads(response.text))

    # -----------------------
    # Write all responses to a single JSON file
    # -----------------------
    output_file = Path(f"{text_selector}_output.json")
    output_data = {"results": results}

    output_file.write_text(
        json.dumps(output_data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # Print the lines of the JSON file
    with output_file.open(encoding="utf-8") as f:
        for line in f:
            print(line.rstrip())

    print(f"\nAll {repeat} response(s) saved to: {output_file.resolve()}")


# -----------------------
# Text mapping dictionary
# -----------------------

TEXT_MAPPING = {
    "winter": (
        "In order that access to an IT system is reliably prevented during a short absence "
        "of the IT user, it should only be possible to disable a screen lock after successful "
        "user authentication. It should be possible for the user to activate the screen lock "
        "manually. In addition, the screen lock should be automatically initiated after a "
        "predefined period of inactivity."
    ),

    "bpmq": (
        "We have to obtain and analyze the respondent bank report.\n"
        "If the respondent bank evaluation fails, it must be added to a black list.\n"
        "Opening an account must be of low risk.\n"
        "If it is the first time to deal with the respondent bank, an advanced due diligence study must be conducted.\n"
        "If the respondent bank rating is rejected, an account must never be opened.\n"
        "Before opening an account, the respondent bank certificate must be valid."
    ),

    "crl": (
        "The customer should receive an automated email notification when his personal data is collected by the 'credit bureau service'.\n"
        "The checking of the customer bank privilege that is followed by checking of her credit worthiness must take place before determining the risk level of the loan application.\n"
        "The activity 'customer bank privilege check' (to be performed by credit broker or supervisor) should be segregated from 'credit worthiness check' (to be performed by post-processing clerk).\n"
        "The branch office manager checks whether risks are acceptable and makes either the final approval or rejection of the request.\n"
        "The offer in the signed loan contract is valid for 7 working days and afterwards it is closed.\n"
        "If the loan request's credit exceeds 1 million Euro (1M e) the clerk supervisor checks the credit worthiness of the customer. The lack of the supervisor check immediately creates a suspense file. In case of failure of the creation of a suspense file, the manager is notified by the system.\n"
        "Checking banking privileges is optional for trusted (gold) customers. If a trusted (gold) customer's loan request is less than 1M Euros, the evaluation of the loan risk is not performed."
    ),

    "dcr": (
        "The consult event should occur before checking the symptoms.\n"
        "Checking symptoms should occur before setting a diagnosis.\n"
        "The prescription of medicine occurs only after the diagnosis is set.\n"
        "Event feel sick occurs after the medicine is given.\n"
        "Event feel healthy occurs after the medicine is given.\n"
        "Events feel sick and feel healthy should not simultaneously occur."
    ),

    "haar": (
        "If a job gets rejected, no further actions are possible.\n"
        "A case cannot be closed before all segments are translated.\n"
        "The TM cannot be updated automatically if the alignment is unverified.\n"
        "Segment can only be created until the translation is started.\n"
        "If a case gets accepted, the TM must eventually be updated."
    ),

    "lyn": (
        "For each milestone, no upload must take place after the corresponding milestone deadline.\n"
        "For each exercise, no upload must take place after the corresponding exercise deadline.\n"
        "For each uploaded milestone, the instructor gives feedback."
    ),

    "pcl": (
        "All new customers must be scanned against provided databases for identity checks.\n"
        "Retain history of identity checks performed.\n"
        "Accounts must maintain a positive balance, unless approved by a bank manager, or they are a VIP customer.\n"
    ),

    "ppsl": (
        "Before an order is being closed, records of the received orders have to be made.\n"
        "After each production action a quality check has to be performed prior to delivery.\n"
        "Before an order is being closed, either records of payments made or records of the fact that the order was rejected have to be taken. Each payment received shall be reported.\n"
        "When an order is filled, a product has to be shipped and an invoice has to be sent."
    ),

    "status": (
        "Every four months, it is necessary to check whether a new document has been uploaded to the Document Management System (DMS) that contains the checklist completed and signed by the Tax Manager and the Financial Controller.\n"
        "If the resolution proposal has been created and the respective reports from the CB and the LD are available, then such reports must be eventually analysed by the same person who created the resolution proposal."
    ),

    "sun": (
        "If, for any reason, it exceeds 30 days, the process with the telephone company must be terminated.\n"
        "The telephone company must verify the accuracy of user personal information.\n"
        "When a customer receives a SIM card, the telephone company must activate the SIM card before the customer can use it.\n"
        "Before retrieving any type of personal data from data subjects, the data controller must obtain the consent of the data subject."
    ),

    "zasada": (
        "The customer data must be received before the individual risk assessment can take place.\n"
        "The customer advisor must provide the two obligatory brochures WpHG Customer Information and the Basic Information Securities and Capital Investment.\n"
        "After concluding the custody account contract, the customer legitimation and the account documents need to be sent to market support.\n"
        "The investment advice needs to be conducted by a customer advisor with a securities competence of level C or above.\n"
        "The customer identification and legitimation must be handled by the customer advisor, while suspected cases of money laundering must be checked by an anti-money-laundering officer.\n"
        "Before concluding a custody-account contract, the customer advisor needs to wait until the suspected case of anti-money laundering is resolved.\n"
        "The customer information must be updated with every future customer contact."
    )
}


if __name__ == "__main__":
    main()
