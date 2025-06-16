from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Anytime Fitness AI Chatbot API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# System prompt constant
SYSTEM_PROMPT = """You are an expert AI assistant and virtual receptionist for Anytime Fitness India. Your entire persona is that of a knowledgeable and friendly human employee.

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

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]]

class ChatResponse(BaseModel):
    reply: str

class SpeakRequest(BaseModel):
    text: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Get vector store ID from environment
        vector_store_id = os.getenv("VECTOR_STORE_ID")
        if not vector_store_id:
            raise HTTPException(status_code=500, detail="Vector store ID not configured")

        # Construct conversation messages list
        conversation_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        conversation_messages.extend(request.history)
        conversation_messages.append({"role": "user", "content": request.message})

        # Make API call to OpenAI
        response = client.responses.create(
            model="gpt-4o-mini",
            input=conversation_messages,
            tools=[{
                    "type": "file_search",
                    "vector_store_ids": [vector_store_id]
                }]
        )

        # Extract the assistant's reply from response.output
        response_text = None
        for item in response.output:
            if hasattr(item, 'role') and item.role == 'assistant':
                response_text = item.content[0].text
                break

        if not response_text:
            raise HTTPException(status_code=500, detail="Failed to get response from AI model")

        return ChatResponse(reply=response_text)

    except Exception as e:
        # Log the error for debugging
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again later."
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/speak")
async def text_to_speech(request: SpeakRequest):
    try:
        response = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=request.text
        )
        
        return StreamingResponse(
            content=response.iter_bytes(),
            media_type="audio/mpeg"
        )
        
    except Exception as e:
        print(f"Error in text-to-speech endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while generating speech. Please try again later."
        )
