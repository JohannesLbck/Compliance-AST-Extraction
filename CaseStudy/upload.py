from google import genai
from google.genai import types
import time
import argparse

client = genai.Client()


def main():
    parser = argparse.ArgumentParser(description="Upload a file to Google GenAI File Search Store")
    parser.add_argument("file_path", type=str, help="Path to the file to be uploaded")
    parser.add_argument("filename", type=str, help="Filename to be used in the File Search Store")
    args = parser.parse_args()

    operation = client.file_search_stores.upload_to_file_search_store(
        file = args.file_path,
        file_search_store_name="fileSearchStores/bpm26casestudy-i0tme4qdt7rx",
        config = {
            "display_name": args.filename
        }
    )

    while not operation.done:
        print("Waiting for file upload to complete...")
        time.sleep(5)
        operation = client.operations.get(operation)

    print("File upload completed.")
        
if __name__ == "__main__":
    main()