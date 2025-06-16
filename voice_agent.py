# voice_agent.py
# A standalone Python script for a Voice-In, Voice-Out AI assistant using the OpenAI Agents SDK, based on voice.ipynb

import os
import asyncio
import numpy as np
import sounddevice as sd
from dotenv import load_dotenv

# Import necessary classes from the Agents SDK
from agents import Agent, FileSearchTool, trace
from agents.voice import AudioInput, SingleAgentVoiceWorkflow, VoicePipeline
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions

# --- 1. SETUP AND CONFIGURATION ---
print("Initializing agent...")
load_dotenv()

# Load the Vector Store ID from the environment file
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")
if not VECTOR_STORE_ID:
    print("🔴 Error: VECTOR_STORE_ID not found in .env file. Please check your configuration.")
    exit()

# --- 2. AGENT DEFINITIONS ---

# Specialist Agent: Knows how to search the knowledge base
knowledge_agent = Agent(
    name="AnytimeFitnessKnowledgeAgent",
    instructions=(
        "You are a friendly and knowledgeable representative for Anytime Fitness. "
        "Your sole purpose is to answer user questions by using the FileSearchTool. "
        "Provide clear, helpful, and concise answers (not more than 50-60 tokens) based strictly on the information found."
        "Remember, the user cannot see your response, he/she can only hear them so make sure they are short and to the point"
        "Do not make up information."
    ),
    tools=[
        FileSearchTool(vector_store_ids=[VECTOR_STORE_ID])
    ],
)

# Triage Agent: The user's first point of contact, which routes to specialists
triage_agent = Agent(
    name="Assistant",
    instructions=prompt_with_handoff_instructions(
        """You are the virtual assistant for Anytime Fitness. 
        Welcome the user warmly and determine their needs.
        Based on their query, route to the correct specialist:

        - AnytimeFitnessKnowledgeAgent for any questions about Anytime Fitness memberships, equipment, policies, or general information."""
    ),
    handoffs=[knowledge_agent],
)

print("✅ Agents defined.")


# --- 3. MAIN VOICE APPLICATION LOGIC ---

async def main():
    """
    The main asynchronous function that runs the voice agent loop.
    """
    # Initialize the workflow and pipeline
    workflow = SingleAgentVoiceWorkflow(agent=triage_agent)
    pipeline = VoicePipeline(workflow=workflow)
    
    # Get the default microphone's sample rate for recording
    try:
        samplerate = int(sd.query_devices(kind='input')['default_samplerate'])
    except Exception as e:
        print(f"🔴 Error: Could not get microphone sample rate. Is a microphone connected? Error: {e}")
        return

    print("🎤 Agent is ready. Press Enter to speak, or type 'exit' and press Enter to quit.")
    print("-" * 70)

    # The main Voice-In, Voice-Out loop
    while True:
        cmd = input("Press Enter to speak...")
        if cmd.lower() == 'exit':
            print("👋 Goodbye!")
            break

        print("🔴 Listening... Press Enter again when you are finished speaking.")
        
        recorded_chunks = []
        def callback(indata, frames, time, status):
            if status:
                print(f"🔴 Recording error: {status}", flush=True)
            recorded_chunks.append(indata.copy())
            
        with sd.InputStream(callback=callback, samplerate=samplerate, channels=1, dtype='int16'):
            input() # This second input() waits for the user to press Enter to stop recording
            
        print("Processing your request...")
        if not recorded_chunks:
            print("No audio recorded. Please try again.")
            continue
            
        recording = np.concatenate(recorded_chunks, axis=0)
        
        # Package the audio data for the pipeline.
        # Note: Corrected `frame_rate` to `sample_rate` to match the SDK.
        audio_input = AudioInput(buffer=recording, sample_rate=samplerate)
        
        # Use trace to visualize the run in platform.openai.com
        with trace("Anytime Fitness Voice Agent Run"):
            result = await pipeline.run(audio_input)
        
        # Stream the audio response back
        response_chunks = []
        async for event in result.stream():
            if event.type == "voice_stream_event_audio":
                response_chunks.append(event.data)
                
        if response_chunks:
            print("🤖 Assistant is responding...")
            response_audio = np.concatenate(response_chunks, axis=0)
            
            sd.play(response_audio, samplerate=samplerate)
            sd.wait() # Wait for the audio to finish playing
        else:
            print("🤔 I don't have a response for that.")

        print("-" * 70)


# --- 4. SCRIPT ENTRY POINT ---

if __name__ == "__main__":
    try:
        # This is the standard way to run an async main function from a script
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting program.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")