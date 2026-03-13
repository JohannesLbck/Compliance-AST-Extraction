from google import genai
from google.genai import types
import time

client = genai.Client()

file_search_store = client.file_search_stores.create(config={'display_name': 'bpm26ExamRegulations'})

print(f"Created File Search Store: {file_search_store.name}")