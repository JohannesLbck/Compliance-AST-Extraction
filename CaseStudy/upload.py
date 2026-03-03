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

    with open(args.file_path, "rb") as filehandler:

        file_search_store = client.file_search_stores.create(
            config = {
                "display_name": "BPM26 Case Study",
            })


        operation = client.file_search_stores.upload_to_file_search_store(
            file = filehandler,
            file_search_store_name=file_search_store.name,
            config = {
                "display_name": args.filename
            }
        )

        while not operation.done:
            print("Waiting for file upload to complete...")
            time.sleep(5)
            operation = client.operations.get(operation)

        print("File upload completed.")