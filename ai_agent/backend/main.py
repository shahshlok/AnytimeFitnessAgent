from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict
import os
import logging
import sys
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/af_backend.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Anytime Fitness AI Chatbot API")

# Log startup
logger.info("Starting Anytime Fitness AI Chatbot API")

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
logger.info(f"CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("OPENAI_API_KEY not found in environment variables")
    raise ValueError("OPENAI_API_KEY must be set")

client = OpenAI(api_key=api_key)
logger.info("OpenAI client initialized successfully")

# System prompt constant
SYSTEM_PROMPT = """You are an expert AI assistant and virtual receptionist for Anytime Fitness India. Your entire persona is that of a knowledgeable and friendly human employee.

Your responses MUST be cheerful, professional, and helpful, always keeping Anytime Fitness in a positive light.

**Your Core Directives:**
1.  **Act Human:** You are a person, not an AI. Do not mention AI, language models, OpenAI, or being a bot.
2.  **Internal Knowledge Only:** You will be provided with internal information to answer questions. You must act as if this is your own knowledge. Never mention files, documents, your knowledge base, or that you are "looking something up."
3.  **No Guessing:** If the information is not in your knowledge base, gracefully state you cannot help with that specific query. Do not make up answers.
4.  **Stay on Brand:** Do not say anything negative about Anytime Fitness.
5.  **Be Concise:** Keep answers short and to the point. The response should be under 100 tokens.
6.  **Glanceable Format:** Always format responses using bullet points, numbered lists, or short paragraphs. Avoid long blocks of text to ensure information is easily scannable.
7.  **No Information about the Vector Store:** Do not provide any information about the vector store or the files that are used to answer the question.
8.  **No Information about the Files:** Do not provide any information about the files that are used to answer the question.
9.  **No Emojis:** Do not use emojis in your responses.
10. **Do not end the response with a question that you cannot answer**

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

async def get_ai_response(message: str, history: List[Dict[str, str]]) -> str:
    try:
        # Get vector store ID from environment
        vector_store_id = os.getenv("VECTOR_STORE_ID")
        if not vector_store_id:
            raise HTTPException(status_code=500, detail="Vector store ID not configured")

        # Construct conversation messages list
        conversation_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        conversation_messages.extend(history)
        conversation_messages.append({"role": "user", "content": message})

        # Make API call to OpenAI
        logger.info(f"Making OpenAI API call for message: {message[:100]}...")
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=conversation_messages,
            tools=[{
                    "type": "file_search",
                    "vector_store_ids": [vector_store_id]
                }],
            # max_output_tokens=100
        )

        # Extract the assistant's reply from response.output
        response_text = None
        for item in response.output:
            if hasattr(item, 'role') and item.role == 'assistant':
                response_text = item.content[0].text
                break

        if not response_text:
            raise HTTPException(status_code=500, detail="Failed to get response from AI model")
        
        logger.info(f"AI response generated: {response_text[:100]}...")

        return response_text

    except Exception as e:
        logger.error(f"Error in get_ai_response: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again later."
        )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    logger.info(f"Chat request received: {request.message[:100]}...")
    try:
        reply = await get_ai_response(request.message, request.history)
        logger.info(f"Chat response sent: {reply[:100]}...")
        return ChatResponse(reply=reply)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again later."
        )

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    logger.info(f"Transcription request received for file: {file.filename}")
    try:
        # Transcribe the audio file using GPT-4o-mini-transcribe
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=(file.filename, file.file)
        )
        
        logger.info(f"Transcription completed: {transcript.text[:50]}...")
        return {"transcribed_text": transcript.text}
        
    except Exception as e:
        logger.error(f"Error in transcribe endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while transcribing your audio. Please try again later."
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/speak")
async def text_to_speech(request: SpeakRequest):
    logger.info(f"TTS request received: {request.text[:50]}...")
    try:
        response = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=request.text
        )
        
        logger.info("TTS response generated successfully")
        return StreamingResponse(
            content=response.iter_bytes(),
            media_type="audio/mpeg"
        )
        
    except Exception as e:
        logger.error(f"Error in text-to-speech endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while generating speech. Please try again later."
        )
