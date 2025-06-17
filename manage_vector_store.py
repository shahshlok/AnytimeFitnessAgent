import os
import openai
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def list_vector_stores():
    print("--- Available Vector Stores ---")
    stores = client.vector_stores.list(limit=100)
    
    if stores.data:
        for store in stores.data:
            print(f"Name: {store.name}")
            print(f"ID: {store.id}")
            print("-" * 40)
    else:
        print("No Vector Stores found.")

def create_new_vector_store():
    store_name = input("Enter name for the new Vector Store: ")
    vector_store = client.vector_stores.create(name=store_name)
    
    print(f"✓ Vector Store created successfully!")
    print(f"Vector Store ID: {vector_store.id}")
    print(f"Copy this ID: {vector_store.id}")

def delete_vector_store():
    store_id = input("Enter Vector Store ID to delete: ")
    confirmation = input(f"Are you sure you want to PERMANENTLY delete Vector Store {store_id}? [y/n]: ")
    
    if confirmation == "y":
        client.vector_stores.delete(vector_store_id=store_id)
        print(f"✓ Vector Store {store_id} deleted successfully!")
    else:
        print("Deletion cancelled.")

def check_store_existence():
    store_id = input("Enter Vector Store ID to check: ")
    
    try:
        store = client.vector_stores.retrieve(vector_store_id=store_id)
        print(f"✓ Vector Store EXISTS: {store.name} (ID: {store.id})")
    except openai.NotFoundError:
        print(f"✓ Vector Store {store_id} DOES NOT EXIST")
    except Exception as e:
        print(f"Error checking store existence: {e}")

if __name__ == "__main__":
    while True:
        print("\n=== Vector Store Management Tool ===")
        print("1. List Stores")
        print("2. Create New Store")
        print("3. Delete Store")
        print("4. Verify Store Existence")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            list_vector_stores()
        elif choice == "2":
            create_new_vector_store()
        elif choice == "3":
            delete_vector_store()
        elif choice == "4":
            check_store_existence()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-5.")