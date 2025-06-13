# %%
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# %%
client= OpenAI(api_key= os.getenv("OPENAI_API_KEY"))

# %%
# --- File Upload  ---
file_directory = "Scraping Data/"
uploaded_file_ids = []

# Check if the directory exists
if not os.path.isdir(file_directory):
    print(f"Error: Directory '{file_directory}' not found. Please make sure your markdown files are inside it.")
else:
    # Get a list of all markdown files in the directory
    files_to_upload = [f for f in os.listdir(file_directory) if f.endswith('.md')]
    
    if not files_to_upload:
        print(f"No markdown (.md) files found in the '{file_directory}' directory.")
    else:
        print(f"Found {len(files_to_upload)} files to upload. Starting process...")
        
        # Loop through each file and upload it
        for filename in files_to_upload:
            file_path = os.path.join(file_directory, filename)
            try:
                print(f"  Uploading {filename}...")
                with open(file_path, "rb") as file_stream:
                    # Upload the file to OpenAI
                    file_object = client.files.create(
                        file=file_stream,
                        purpose="assistants"  # The purpose must be 'assistants' for use with Vector Stores
                    )
                
                # Append the returned file ID to our list
                uploaded_file_ids.append(file_object.id)
                print(f"  -> Success! File ID: {file_object.id}")
            except Exception as e:
                print(f"  -> FAILED to upload {filename}. Error: {e}")

# --- Final Output ---
print("\n" + "="*30)
print("File Upload Process Complete.")
print(f"Total files uploaded successfully: {len(uploaded_file_ids)}")
print("="*30)
print("\nList of File IDs:")
print(uploaded_file_ids)

# %%
print(vector_store.id)

# %%
try:
    system_prompt = """You are an expert AI assistant and virtual receptionist for Anytime Fitness India. Your entire persona is that of a knowledgeable and friendly human employee.

Your responses MUST be cheerful, professional, and helpful, always keeping Anytime Fitness in a positive light.

**Your Core Directives:**
1.  **Act Human:** You are a person, not an AI. Do not mention AI, language models, OpenAI, or being a bot.
2.  **Internal Knowledge Only:** You will be provided with internal information to answer questions. You must act as if this is your own knowledge. Never mention files, documents, your knowledge base, or that you are "looking something up."
3.  **No Guessing:** If the information is not in your knowledge base, gracefully state you cannot help with that specific query. Do not make up answers.
4.  **Stay on Brand:** Do not say anything negative about Anytime Fitness.
5.  **Be Concise:** Keep answers short and to the point (under 60 tokens).

**Crucially, you must NEVER use phrases like:**
- "According to the document..."
- "Based on the files provided..."
- "The information I have says..."
- "I found in our knowledge base..."

You must ALWAYS speak from a first-person perspective as a helpful receptionist. Never break character.
"""
    conversation_history = [{"role": "system", "content": system_prompt}]
    vector_store_id = vector_store.id 

    print("--- Anytime Fitness AI Agent ---")
    print("Agent is now ready. Type 'exit' or 'quit' to end the session.")

    
    while True:
        # Get user input
        query = input("👤 You: ")
        
        # Check for exit condition
        if query.lower() in ["exit", "quit"]:
            print("\n🤖 Assistant: It was a pleasure to help. Have a wonderful day!")
            break
        print("\n👤 You: "+ query)
        try:
            conversation_history.append({"role": "user", "content": str(query)})
            
            # Make the API call
            response = client.responses.create(
                model="gpt-4o-mini",
                input=conversation_history,
                tools=[{
                    "type": "file_search",
                    "vector_store_ids": [vector_store_id]
                }]
            )

            
            response_text= None
            for item in response.output:
                if(hasattr(item, 'role') and item.role== 'assistant'):
                    response_text= item
                    break

            if response_text:
                text_content_block = response_text.content[0]
                response_text = text_content_block.text
                
                display_text = response_text

                print(f"🤖 Assistant: {display_text}")
                
                conversation_history.append({"role": "assistant", "content": response_text})
            else:
                print("🤖 Assistant: I seem to be having trouble finding an answer right now. Could you please try asking in a different way?")
                conversation_history.pop()

        except Exception as e:
            print(f"\nAn error occurred during the API call: {e}")
            conversation_history.pop()

except NameError:
    print("\n[ERROR] The 'vector_store' object was not found.")
except Exception as e:
    print(f"\nAn unexpected error occurred during setup: {e}")
