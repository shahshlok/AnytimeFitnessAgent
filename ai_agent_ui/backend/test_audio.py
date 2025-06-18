# test_audio.py
# A simple script to transcribe a local audio file to verify its content.

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API Key from .env file at the project root
load_dotenv()
client = OpenAI()

# --- IMPORTANT ---
# Set the path to your test audio file here.
# Since the script is at the root, the path is relative from there.
AUDIO_FILE_PATH = "ai_agent_ui/backend/test_query.mp3" 

def verify_audio_content():
    """Transcribes an audio file and prints the result."""
    print(f"Attempting to transcribe file: {AUDIO_FILE_PATH}")
    
    if not os.path.exists(AUDIO_FILE_PATH):
        print(f"🔴 ERROR: File not found at the specified path.")
        return

    try:
        with open(AUDIO_FILE_PATH, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio_file
            )
        print("\n--- Transcription Result ---")
        print(f"✅ Success! The audio file contains the following text:")
        print(f"   '{transcript.text}'")
        print("----------------------------")
        
    except Exception as e:
        print(f"🔴 ERROR: Failed to transcribe audio file. Reason: {e}")

if __name__ == "__main__":
    verify_audio_content()