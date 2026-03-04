from google import genai
from google.genai import types
import time
import argparse
from pydantic import BaseModel, Field
from typing import List

from prompt_toolkit import prompt

class RequirementsModel(BaseModel):
    requirements: List[str] = Field(..., description="List of requirement ASTs")

client = genai.Client()


def main():
    argparser = argparse.ArgumentParser(description="Extract content using Google GenAI")
    argparser.add_argument("inputtext", type=str, help="Input text for content generation")
    argparser.add_argument("temperature", type=float, help="Temperature value for content generation (0.0 to 1.0)")
    args = argparser.parse_args()
    
    prompt = "Enter the prompt for content generation: "
    
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents = prompt,
        config=types.GenerateContentConfig(
            temperature=args.temperature,
            tools=[types.Tool(
                tool_name=types.FileSearch(
                    file_search_store_names=['fileSearchStores/bpm26casestudy-i0tme4qdt7rx'],
                )],
            response_mime_type="application/json",
            response_schema=RequirementsModel.model_json_schema()
        )
    )

if __name__ == "__main__":
    main()