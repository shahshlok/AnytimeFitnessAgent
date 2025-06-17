import os
import json
import requests
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Configuration
FIRECRAWL_API_KEY = os.getenv('PERSONAL_FIRECRAWL_API_KEY')
SITEMAP_PATH = "Scraping Data/claude_sitemap.json"
OUTPUT_DIR = 'scraped_data'

def url_to_filename(url: str) -> str:
    """
    Convert a URL into a safe filename.
    
    Args:
        url (str): The URL to convert
        
    Returns:
        str: A safe filename with .md extension
    """
    # Remove protocol and www
    filename = re.sub(r'^https?://(?:www\.)?', '', url)
    
    # If empty (homepage), return homepage.md
    if not filename:
        return "homepage.md"
    
    # Replace / with _
    filename = filename.replace('/', '_')
    
    # Remove any characters that are not alphanumeric, underscore, or hyphen
    filename = re.sub(r'[^a-zA-Z0-9_-]', '', filename)
    
    # Append .md extension
    return f"{filename}.md"

def main():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Read and parse sitemap
    try:
        with open(SITEMAP_PATH, 'r') as f:
            sitemap = json.load(f)
    except FileNotFoundError:
        print(f"Error: Sitemap file '{SITEMAP_PATH}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: '{SITEMAP_PATH}' is not a valid JSON file.")
        return
    
    # Loop through each URL in sitemap
    for url_obj in sitemap:
        url = url_obj.get('url')
        if not url:
            continue
            
        print(f"Scraping: {url}")
        
        try:
            # Make API request to Firecrawl
            response = requests.post(
                'https://api.firecrawl.dev/v0/scrape',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {FIRECRAWL_API_KEY}'
                },
                json={'url': url}
            )
            
            if response.status_code == 200:
                # Extract markdown content
                markdown_content = response.json()['data']['markdown']
                
                # Generate filename and save content
                filename = url_to_filename(url)
                output_path = os.path.join(OUTPUT_DIR, filename)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                    
                print(f"Successfully saved: {filename}")
            else:
                print(f"Error scraping {url}: {response.status_code} - {response.reason}")
                
        except requests.exceptions.RequestException as e:
            print(f"Connection error while scraping {url}: {str(e)}")
        except Exception as e:
            print(f"Unexpected error while scraping {url}: {str(e)}")

if __name__ == "__main__":
    main() 