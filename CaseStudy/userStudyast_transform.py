import json
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


def main() -> None:
    ## Fill these with the ones from the user study that are above the higher threshhold
    ASTS = [
        "AST",
        "AST",
    ]
    NL = [
        "NL requirement",
        "NL requirement",
    ]

    translated_asts = []
    for ast in ASTS:
        print(f"Translating AST: {ast}")
        result = transform(ast)
        translated_asts.append(result)
        print(f"Result: {result}\n")

    print(translated_asts)
    astembeddings = model.encode(translated_asts)
    nlembeddings = model.encode(NL)
    average_similarity = model.similarity(astembeddings, nlembeddings).mean()  
    print(f"Average similarity between AST and NL requirements: {average_similarity:.4f}")
    for i in range(len(translated_asts)):
        print(f"Comparing AST requirement {translated_asts[i]} with NL requirement {NL[i]}:")
        simil = cos_sim(astembeddings[i], nlembeddings[i])
        print(simil)
        if simil > 0.7:
            print(f"AST and NL requirement {i} are similar based on semantic string comparison.")
        else:
            print(f"AST and NL requirement {i} are NOT similar based on semantic string comparison.")
    print(cos_sim(astembeddings[0], nlembeddings[0]))
 
		


if __name__ == "__main__":
    main()
