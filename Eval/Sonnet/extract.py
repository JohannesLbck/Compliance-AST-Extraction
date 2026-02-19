import json
from pathlib import Path
import argparse
from typing import Dict, List
from pydantic import BaseModel, Field
import anthropic

# The client gets the API key from the environment variable `ANTHROPIC_API_KEY`.
client = anthropic.Anthropic()


class RequirementsModel(BaseModel):
    requirements: Dict[str, str] = Field(..., description="Requirement ASTs")


def main():
    # -----------------------
    # Argument parsing
    # -----------------------
    parser = argparse.ArgumentParser(
        description="Extract requirement ASTs from predefined text datasets using Claude Sonnet"
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
    doc = Path("../methods_doc.md").read_text(encoding="utf-8")

    # -----------------------
    # Prepare prompt with improved structure
    # -----------------------
    prompt = (
        "=" * 80 + "\n"
        "TASK: COMPLIANCE REQUIREMENT EXTRACTION\n"
        "=" * 80 + "\n"
        "Extract business process requirements from natural language text and convert them\n"
        "into formal compliance pattern AST (Abstract Syntax Tree) expressions.\n\n"

        "=" * 80 + "\n"
        "OUTPUT FORMAT\n"
        "=" * 80 + "\n"
        "Each requirement must be formatted as: R{NUMBER}: <AST expression>\n"
        "Example: R1: leads_to(tree, 'submit application', 'review application')\n"
        "Example: R2: executed_by(tree, 'approve request', 'manager')\n\n"

        "=" * 80 + "\n"
        "CORE PRINCIPLES (READ CAREFULLY)\n"
        "=" * 80 + "\n"
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

        "=" * 80 + "\n"
        "TIME HANDLING\n"
        "=" * 80 + "\n"
        "- Encode as integer seconds whenever possible.\n"
        "  Example: 7 working days = 604800 seconds\n"
        "- For non-specific or complex times, use descriptive strings.\n"
        "  Example: 'predefined period', 'business hours'\n"
        "- Special keywords:\n"
        "  * 'Start Activity' = process start event\n"
        "  * 'End Activity' = process end event\n"
        "  * 'terminate' = immediately stop/end process\n\n"

        "=" * 80 + "\n"
        "DATA PATTERNS (CRITICAL)\n"
        "=" * 80 + "\n"
        "Use send_exist() and receive_exist() instead of embedding data in activity labels.\n\n"

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

        "=" * 80 + "\n"
        "FAILURE PATTERNS (USE WITH CARE)\n"
        "=" * 80 + "\n"
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

        "=" * 80 + "\n"
        "COMMON TRANSFORMATIONS (REFERENCE)\n"
        "=" * 80 + "\n"
        "Pattern translations from natural language:\n\n"

        "1. ORDERING/PRECEDENCE:\n"
        "   'A must happen before B' OR 'B only after A'\n"
        "   → leads_to(tree, 'a', 'b')\n\n"

        "2. NEGATION/PREVENTION:\n"
        "   'A cannot happen after B' OR 'After A, B is impossible'\n"
        "   → leads_to_absence(tree, 'a', 'b')\n\n"

        "3. CONDITIONS:\n"
        "   'If X is true, then eventually A happens'\n"
        "   → condition_eventually_follows(tree, 'X==true', 'a')\n\n"

        "4. RESOURCE ASSIGNMENT:\n"
        "   'A must be performed by role R'\n"
        "   → executed_by(tree, 'a', 'R')\n\n"

        "5. DATA FLOW:\n"
        "   'X must be received before Y can occur'\n"
        "   → leads_to(tree, receive_exist(tree, 'X'), 'y')\n\n"

        "6. TIMING:\n"
        "   'A must complete within N seconds before B happens'\n"
        "   → timed_alternative(tree, 'a', 'b', N)\n\n"

        "7. PARALLEL:\n"
        "   'A and B must occur simultaneously'\n"
        "   → parallel(tree, 'a', 'b')\n\n"

        "=" * 80 + "\n"
        "MULTI-REQUIREMENT HANDLING\n"
        "=" * 80 + "\n"
        "If one NL sentence describes multiple independent constraints, create separate R{N} entries.\n"
        "If constraints are interdependent, combine them using 'and' operator within a single entry.\n\n"

        "Example:\n"
        "  NL: 'Check credit report and verify identity before opening account'\n"
        "  R1: leads_to(tree, 'check credit report', 'open account')\n"
        "  R2: leads_to(tree, 'verify identity', 'open account')\n\n"

        "=" * 80 + "\n"
        "VALIDATION CHECKLIST (Before submitting)\n"
        "=" * 80 + "\n"
        "□ All activity labels are in active voice (verb-object)\n"
        "□ No resource names appear in activity labels\n"
        "□ All data objects use camelCase\n"
        "□ Failure patterns are only used for actual activity failures\n"
        "□ Time values are integers (seconds) when specific, strings when not\n"
        "□ System perspective applied consistently (not actor perspective)\n"
        "□ Data presence uses send_exist/receive_exist, not activity labels\n\n"

        "=" * 80 + "\n"
        "COMPLIANCE PATTERN REFERENCE\n"
        "=" * 80 + "\n"
        f"{doc}\n\n"

        "=" * 80 + "\n"
        "TEXT TO EXTRACT FROM\n"
        "=" * 80 + "\n"
        f"{text}\n\n"

        "=" * 80 + "\n"
        "RESPONSE INSTRUCTIONS\n"
        "=" * 80 + "\n"
        "Return your response as valid JSON in this exact format:\n"
        "{\n"
        '  "requirements": {\n'
        '    "R1": "leads_to(tree, \'activity1\', \'activity2\')",\n'
        '    "R2": "executed_by(tree, \'activity\', \'resource\')"\n'
        "  }\n"
        "}"
    )

    # -----------------------
    # Collect all responses
    # -----------------------
    results: List[Dict] = []

    for i in range(repeat):
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Extract the text content
        response_text = response.content[0].text

        # Parse response JSON and append to results
        try:
            # Try to find JSON in the response (it might be wrapped in markdown code blocks)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                json_str = response_text

            result = json.loads(json_str)
            results.append(result)
        except json.JSONDecodeError as e:
            print(f"Error parsing response {i+1}: {e}")
            print(f"Response content: {response_text}")
            continue

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
        "Accounts must maintain a positive balance, unless approved by a bank manager, or for VIP customers.\n"
        "Accounts of type VIP are allowed to have a non positive balance and no approval is required for this type of accounts."
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
