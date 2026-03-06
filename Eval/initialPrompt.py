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
    doc = Path("../methods_doc.md").read_text(encoding="utf-8")

    # -----------------------
    # Prepare prompt
    # -----------------------
    prompt = (
        "Your Task is to extract business process requirements from Natural Language Requirements. "
        "Every requirement should be of format R{ID}: AST'"
        "All times should be encoded as seconds integers if possible. If a time is not exactly defined, you can write a string that describes the time."
        "If possible, instead of creating activity labels that indicate sending/receiving data in their labels, use the send_exists and receive_exists patterns"
        "Write dataobjects in camel_case"
        "Data conditions should be encoded as formulas created out of dataobjectname operator value or dataobjectname in case of booleans"
        "'Start Activity' refers to the start activity, 'End Activity' refers to the end activity, and 'terminate' immediattely terminates/ends a process"
        "You can use standard operators (not, or, ==, and, >, <, >=, <=) and parentheses to combine compliannce patterns and create complex data conditions"
        "If a requirement has to hold for the entire tree, you can leave out the tree argument"
        "Write activity labels in active voice without connectors such as 'a' and 'the'"
        "Avoid including resource assignment in the activity label. Instead use the executed_by pattern to specify which resource performs which activity)"
        "Furthermore, activities are from the perspective of the system, so for example 'customer receives email' should be written as 'send email' and not 'receive email'"
        "Same applies to sending and receving data using send_exist and receive_exist, for example 'customer receives email' should be written as send_exist(tree, 'email') and not receive_exist(tree, 'email')"
        "Every requirement should be transformed into a python AST which uses only"
        "Failure patterns should only be used if a activity fails. For example, if a customer fails an eligibility check, the activity did not fail, but the eligibility check did, so you should use a condition_eventually_follows(tree, 'eligibility check failed', 'some activity') pattern and not a failure_eventually_follows(tree, 'eligibility check', 'some activity') pattern"
        "A example for a failure pattern usage would be if a system fails to send an email, then you could use the pattern failure_eventually_follows(tree, 'send email', 'some activity')"
        "the Methods described in the following documentation written in markdown:\n\n"
        f"{doc}\n\n"
        "Extract from the following text:\n\n"
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
        "The customer should receive an automated email notification when his personal data is collected by the ‘credit bureau service’.\n"
        "The checking of the customer bank privilege that is followed by checking of her credit worthiness must take place before determining the risk level of the loan application.\n"
        "The activity ‘customer bank privilege check’ (to be performed by credit broker or supervisor) should be segregated from ‘credit worthiness check’ (to be performed by post-processing clerk).\n"
        "The branch office manager checks whether risks are acceptable and makes either the final approval or rejection of the request.\n"
        "The offer in the signed loan contract is valid for 7 working days and afterwards it is closed.\n"
        "If the loan request’s credit exceeds 1 million Euro (1M e) the clerk supervisor checks the credit worthiness of the customer. The lack of the supervisor check immediately creates a suspense file. In case of failure of the creation of a suspense file, the manager is notified by the system.\n"
        "Checking banking privileges is optional for trusted (gold) customers. If a trusted (gold) customer’s loan request is less than 1M Euros, the evaluation of the loan risk is not performed."
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

