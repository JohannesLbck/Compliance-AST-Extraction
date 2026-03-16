import json
import os
from pathlib import Path
import argparse
from typing import Dict, List
from pydantic import BaseModel, Field
import datetime
from openai import OpenAI

# The client gets the API key from the environment variable `OPENAI_API_KEY`.
client = OpenAI(
    api_key = os.environ.get("OPENAI_API_KEY"),
)

class RequirementsModel(BaseModel):
    requirements: List[str] = Field(..., description="List of requirement ASTs")


def main():
    # -----------------------
    # Argument parsing
    # -----------------------
    doc = Path("../methods_doc_concise.md").read_text(encoding="utf-8")
    for temperature in {0.1, 0.3, 0.5, 0.7}:
        for key in TEXT_MAPPING.keys():
            prompt = (
                    "TASK: Extract compliance requirements from text and convert to AST expressions.\n"
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
                    f"{TEXT_MAPPING[key]}"
                )
            print(f"Running with temperature={temperature} and text_selector={key}")
            for i in range(5):
                print(f"Run {i+1}/5 for temperature={temperature} and text_selector={key}")
                response = client.responses.parse(
                    model="gpt-5.0",
                    input=[
                        {
                            "role": "system",
                            "content": "You are an expert in business process compliance modeling. Extract requirements and express them as AST expressions following the provided schema exactly."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    text_format=RequirementsModel,
                    temperature=temperature
                )

                output_file = Path(f"{key}_{temperature}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

                output_file.write_text(
                    json.dumps(response.output_parsed.requirements, indent=2, ensure_ascii=False),
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
    "haar": (
        "A case cannot be closed before all segments are translated.\n"
        "The TM cannot be updated automatically if the alignment is unverified.\n"
        "Segment can only be created until the translation is started.\n"
        "If a case gets accepted, the TM must eventually be updated."
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
