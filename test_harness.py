# test_harness.py (Corrected Version 2)
# An automated test suite for our voice agent.

import os
import asyncio
import io 
import numpy as np
import soundfile as sf
from openai import OpenAI

# --- 1. SETUP AND CONFIGURATION ---
try:
    from voice_agent import triage_agent
except ImportError:
    print("🔴 Error: Could not import 'triage_agent' from voice_agent.py.")
    print("Ensure the file exists and is in the same directory.")
    exit()

from agents.voice import AudioInput, SingleAgentVoiceWorkflow, VoicePipeline
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
TTS_SAMPLE_RATE = 24000
OUTPUT_DIR = "test_audio_responses"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# --- 2. DEFINE THE TEST SUITE ---
test_suite = [
    {
        "name": "General Equipment Query",
        "query_text": "What kind of workout equipment do you have?",
        "expected_keywords": ["treadmills", "cycles", "weights", "equipment"]
    },
    {
        "name": "Specific Policy Query",
        "query_text": "Tell me about your health and safety policy.",
        "expected_keywords": ["health", "safety", "policy", "cleanliness"]
    },
    {
        "name": "Out-of-Scope Nonsense Query",
        "query_text": "Can you tell me the current price of gold?",
        "expected_keywords": ["sorry", "cannot", "don't have information"]
    },
    {
        "name": "Membership Details Query",
        "query_text": "What are the terms and conditions for a membership?",
        "expected_keywords": ["terms", "conditions", "membership"]
    },
]


# --- 3. THE TEST HARNESS MAIN FUNCTION ---
async def run_test_harness():
    print("🚀 Starting Automated Test Harness for Voice Agent...")
    workflow = SingleAgentVoiceWorkflow(agent=triage_agent)
    pipeline = VoicePipeline(workflow=workflow)
    passed_count = 0
    failed_count = 0
    
    for i, case in enumerate(test_suite):
        test_name = case["name"]
        query_text = case["query_text"]
        expected_keywords = case["expected_keywords"]
        
        print(f"\n--- Running Test {i+1}/{len(test_suite)}: {test_name} ---")

        try:
            print("1. Generating voice query from text...")
            response = client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice="alloy",
                input=query_text
            )
            query_audio_bytes = response.content

            print("2. Decoding MP3 bytes to raw audio waveform (NumPy array)...")
            # Treat the bytes object as an in-memory file
            mp3_file_like_object = io.BytesIO(query_audio_bytes)
            # Use soundfile to read the in-memory file and get a NumPy array
            query_audio_np, read_samplerate = sf.read(mp3_file_like_object, dtype= 'float32')

            print("3. Feeding decoded voice to the agent...")
            audio_input = AudioInput(buffer=query_audio_np, frame_rate=read_samplerate)
            
            result = await pipeline.run(audio_input)

            print("4. Capturing agent's audio response...")
            response_chunks = []
            async for event in result.stream():
                if event.type == "voice_stream_event_audio":
                    response_chunks.append(event.data)

            if not response_chunks:
                print("⚠️  Agent produced no audio response.")
                failed_count += 1
                continue

            response_audio_np = np.concatenate(response_chunks, axis=0)

            print("5. Saving response and converting it back to text for validation...")
            temp_audio_path = os.path.join(OUTPUT_DIR, f"response_{test_name.replace(' ', '_')}.wav")
            # Use the sample rate from the agent's response stream for saving
            response_samplerate = TTS_SAMPLE_RATE
            sf.write(temp_audio_path, response_audio_np, response_samplerate)

            with open(temp_audio_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="gpt-4o-mini-tts", 
                    file=audio_file
                )
            response_text = transcription.text.lower()

            print("6. Validating response text...")
            is_pass = all(keyword in response_text for keyword in expected_keywords)

            if is_pass:
                print(f"✅ PASS: Response contained expected keywords.")
                passed_count += 1
            else:
                print(f"❌ FAIL: Response did not meet expectations.")
                print(f"   - Expected to find: {expected_keywords}")
                print(f"   - Actual response: '{response_text}'")
                failed_count += 1
                
        except Exception as e:
            print(f"🚨 An error occurred during test '{test_name}': {e}")
            failed_count += 1

    print("\n\n--- Test Harness Complete ---")
    print(f"✅ Passed: {passed_count}")
    print(f"❌ Failed: {failed_count}")
    print("---------------------------")
    if failed_count == 0:
        print("🎉 All tests passed successfully!")


# --- SCRIPT ENTRY POINT ---
if __name__ == "__main__":
    asyncio.run(run_test_harness())