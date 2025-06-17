import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATA_DIR = "scraped_data"
OUTPUT_FILE = "file_ids.json"

def main():
    file_paths = []
    
    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith('.md'):
                file_paths.append(os.path.join(root, file))
    
    file_ids = []
    
    for path in tqdm(file_paths, desc="Uploading Files"):
        try:
            with open(path, "rb") as file:
                file_object = client.files.create(file=file, purpose="assistants")
                file_ids.append(file_object.id)
        except Exception as e:
            print(f"Error uploading {path}: {e}")
            continue
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(file_ids, f)
    
    print(f"Successfully uploaded {len(file_ids)} files. File IDs saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()