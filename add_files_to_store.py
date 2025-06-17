import os
import json
import time
import openai
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INPUT_FILE = "file_ids.json"

def main():
    vector_store_id = os.getenv("UPDATED_VECTOR_STORE_ID")
    
    with open(INPUT_FILE, "r") as f:
        all_file_ids = json.load(f)
    
    for file_id in tqdm(all_file_ids, desc="Adding Files to Vector Store"):
        try:
            client.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=file_id
            )
            time.sleep(0.5)
        except Exception as e:
            print(f"Error adding file {file_id}: {e}")
            continue
    
    print("Successfully completed adding files to vector store.")
    
    vector_store_files = client.vector_stores.files.list(vector_store_id=vector_store_id)
    print(f"Verification: Found {len(vector_store_files.data)} files in the vector store.")

if __name__ == "__main__":
    main()