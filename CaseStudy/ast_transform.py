import argparse
import json
from pathlib import Path
from TransASTParser import transform
from fuzzywuzzy import fuzz
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


#model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')


def read_json(path: Path) -> dict:
	with path.open("r", encoding="utf-8") as file:
		return json.load(file)


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Read JSON files in CaseStudy/Outputs-style format."
	)
	parser.add_argument(
		"input_path",
		type=Path,
		help="Path to a single JSON file.",
	)
	return parser.parse_args()

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


def main() -> None:
	args = parse_args()
	input_path = args.input_path

	if not input_path.is_file() or input_path.suffix.lower() != ".json":
		raise FileNotFoundError(f"Expected a JSON file path, got: {input_path}")

	data = read_json(input_path)
	translated_asts = []
	for ast in data["AST_requirements"]:
		print(f"Translating AST: {ast}")
		result = transform(ast)
		translated_asts.append(result)
		print(f"Result: {result}\n")	
	
	print(translated_asts)
	astembeddings = model.encode(translated_asts)
	nlembeddings = model.encode(data["NL_requirements"])
	for i in range(len(translated_asts)):
		print(f"Comparing AST requirement {translated_asts[i]} with NL requirement {data['NL_requirements'][i]}:")
		simil = cos_sim(astembeddings[i], nlembeddings[i])
		print(simil)
		if simil > 0.6898: ## Threshold calculated using userStudyast_transform.py
			print(f"AST and NL requirement {i} are similar based on semantic string comparison.")
		else:
			print(f"AST and NL requirement {i} are NOT similar based on semantic string comparison.")
	print(cos_sim(astembeddings[0], nlembeddings[0]))
 
		


if __name__ == "__main__":
	main()
