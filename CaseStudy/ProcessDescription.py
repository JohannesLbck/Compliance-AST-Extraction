from pathlib import Path

from google import genai
from google.genai import types
import time
import argparse
from pydantic import BaseModel, Field
from typing import List
import json



class RequirementsModel(BaseModel):
    nlrequirements: List[str] = Field(..., description="List of requirements in Natural Language")
    astrequirements: List[str] = Field(..., description="List of requirement ASTs")

client = genai.Client()


def main():
    argparser = argparse.ArgumentParser(description="Extract content using Google GenAI")
    argparser.add_argument("inputtext", type=str, help="Input text for content generation")
    argparser.add_argument("temperature", type=float, help="Temperature value for content generation (0.0 to 1.0)",default=0.3)
    args = argparser.parse_args()
    
    doc = Path("methods_doc_concise.md").read_text(encoding="utf-8")

    # -----------------------
    # Prepare prompt with improved structure
    # -----------------------
    prompt = (
        "TASK: Your Task is to identify which requirements are relevant to a process from a short process description.\n"
        "Return the identified requirements both in natural language and as ASTs\n"
        "Use the documents from the file search store as grounding if fitting.\n\n"
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
        "9. Generate at most 10 requirements. Focus on most critical ones.\n\n"
        "COMPLIANCE PATTERN REFERENCE\n"
        f"{doc}\n\n"
        "PROCESS DESCRIPTION\n"
        f"{args.inputtext}"
    )
    
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents = prompt,
        config=types.GenerateContentConfig(
            temperature=args.temperature,
            tools=[types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=['fileSearchStores/bpm26casestudy-i0tme4qdt7rx'],
                )
            )],
            response_mime_type="application/json",
            response_schema=RequirementsModel.model_json_schema()
        )
    )
    # Build output containing original input text and the parsed requirements
    print(response)
    output = json.loads(response.text)
    if response.candidates[0].grounding_metadata:
        citations = []
        for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
            citation = {
                "source" :chunk.retrieved_context.title,
                "text": chunk.retrieved_context.text,
            }
            citations.append(citation)
    else:
        print("No grounding metadata was used in the Answer.")
        citations = "No grounding metadata was used in the Answer."

    output_obj = {
        "input_text": args.inputtext,
        "NL_requirements": output["nlrequirements"],
        "AST_requirements": output["astrequirements"],
        "citations": citations,
    }

    output_file = Path(f"Outputs/{args.temperature}_{time.strftime('%Y%m%d_%H%M%S')}.json")
    with output_file.open("w", encoding="utf-8") as f:
        f.write(json.dumps(output_obj, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()