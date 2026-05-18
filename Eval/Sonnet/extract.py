import json
from pathlib import Path
import argparse
from typing import List
from pydantic import BaseModel, Field, root_model
import datetime
import anthropic

# The client gets the API key from the environment variable `ANTHROPIC_API_KEY`.
client = anthropic.Anthropic()


class RequirementsModel(BaseModel):
    # Root model containing a simple list of requirement AST strings
    requirements: List[str] = Field(..., description="List of requirement ASTs")


def main():
    # -----------------------
    # Argument parsing
    # -----------------------
    parser = argparse.ArgumentParser(
        description="Extract requirement ASTs from predefined text datasets using Claude Sonnet"
    )

    # Removed schema print and stray pass since not needed with root model
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

    parser.add_argument(
        "--temperature",
        type=float,
        default=0.3,
        help="Temperature setting for response generation (default=0.3)"
    )

    args = parser.parse_args()

    text_selector = args.textselector
    repeat = args.range
    temperature = args.temperature

    text = TEXT_MAPPING[text_selector]

    # -----------------------
    # Load method documentation
    # -----------------------
    doc = Path("../methods_doc.md").read_text(encoding="utf-8")

    # -----------------------
    # Prepare prompt with improved structure
    # -----------------------
    prompt = (
        "TASK: Extract compliance requirements from text and convert to AST expressions (in Json format).\n"
        "Return output as a JSON array of requirement strings, without any enclosing object.\n"
        "Format: R{NUMBER}: <expression>\n\n"

        "CRITICAL RULES:\n"
        "1. SYSTEM PERSPECTIVE: Model from system viewpoint. 'Customer receives email' = system sent it.\n"
        "   Use send_exist() for outgoing, receive_exist() for incoming data.\n\n"

        "2. ACTIVITY LABELS: Active voice, no articles or resource names.\n"
        "   ✓ 'approve request'  ✗ 'manager approves request'\n\n"

        "3. RESOURCE SPECIFICATION:\n"
        "   - ALWAYS use executed_by(tree, 'activity', 'resource') pattern.\n"
        "   - Resources must be specified separately from activity names.\n"
        "   - ✗ WRONG:  executed_by(tree, 'manager approves request', 'manager')\n"
        "   - ✓ RIGHT:  executed_by(tree, 'approve request', 'manager')\n\n"

        "4. DATA OBJECTS: camelCase names, not physical objects.\n"
        "   ✓ 'accountBalance'  ✗ 'sim card', 'pizza'\n"
        "   Use conditions to enforce domain constraints:\n"
        "   data_leads_to_absence(tree, 'accountBalance < 0', 'End Activity')\n\n"
        
        "5. Data Domain: If a dataobject should stay in a certain domain, prevent it from reaching said domain.\n"
        "  Example: 'accountBalance must never be negative' → no condition_eventually_follows(tree, 'accountBalance < withdrawalAmount', 'withdrawal')\n\n"

        "5. DATA CONDITIONS: Format = 'dataName operator value'\n"
        "   Operators: not, or, ==, and, >, <, >=, <=\n"
        "   Example: '(loanAmount > 1000000) and (status == \"gold\")'\n\n"

        "6. DESIGN TIME: Disjunction in NL may need conjunction of patterns.\n"
        "   'Either delivered OR rejected' = both must exist in process\n\n"

        "7. TIME: Encode seconds if possible (7 days = 604800s). String descriptiors if constraint is vague.\n"
        "   Special Activities: 'Start Activity', 'End Activity', 'terminate'\n\n"

        "8. failure_* patterns: ONLY for system execution failures, not negative results.\n"
        "   ✗ 'check fails' (negative result) → ✓ condition_eventually_follows(tree, 'checkFailed == true', ...)\n"
        "   ✓ 'system fails to send' (cannot execute) → failure_eventually_follows(...)\n\n"

        "COMPLIANCE PATTERN REFERENCE\n"
        f"{doc}\n\n"
        "TEXT TO EXTRACT\n"
        f"{text}"
    )

    # -----------------------
    # Collect all responses
    # -----------------------

    for i in range(repeat):
        response = client.messages.parse(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            temperature=temperature,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            output_format=RequirementsModel,
        )
        # Extract the text content
        response_text = response.parsed_output
        # append parsed list to results
        print(response_text.model_dump_json(indent=2, ensure_ascii=False))

        output_file = Path(f"{text_selector}_{temperature}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

        output_file.write_text(
            json.dumps(response_text.requirements, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        # Print the lines of the JSON file
        with output_file.open(encoding="utf-8") as f:
            for line in f:
                print(line.rstrip())
        print(f"\nResponse(s) saved to: {output_file.resolve()}")


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
    ),
    "Voter": (
            "The antiseptic solution should be allowed to dry completely before venepuncture. \n"
            "The collected blood should be mixed with the anticoagulant every 10 seconds during the donation to prevent clot formation. \n"
            "The maximum collection time for acceptance of the donation should be specified and controlled. \n"
            "If manual mixing is used, the blood container should be inverted every 30 seconds. "
            )
}


if __name__ == "__main__":
    main()
