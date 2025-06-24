from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc, Float
import os
import logging
import sys
import uuid
import time
from datetime import datetime, timedelta
from openai import OpenAI
from dotenv import load_dotenv

# Import database modules
import database
import models
import crud

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

# Create database tables on startup
models.Base.metadata.create_all(bind=database.engine)
logger.info("Database tables created/verified")

# Log startup
logger.info("Starting Anytime Fitness AI Chatbot API")

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
logger.info(f"CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    # allow_origins=allowed_origins,
    # allow_credentials=True,
    allow_origins= ["*"],
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
    session_id: uuid.UUID | None = None
    input_type: str = "text"

class ChatResponse(BaseModel):
    reply: str


class SpeakRequest(BaseModel):
    text: str

async def get_ai_response(message: str, history: List[Dict[str, str]]) -> Tuple[str, Dict[str, Any]]:
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
        start_time = time.time()
        model_name = "gpt-4.1-mini"
        response = client.responses.create(
            model=model_name,
            input=conversation_messages,
            tools=[{
                    "type": "file_search",
                    "vector_store_ids": [vector_store_id]
                }],
            # max_output_tokens=100
        )
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        # Extract the assistant's reply from response.output
        response_text = None
        for item in response.output:
            if hasattr(item, 'role') and item.role == 'assistant':
                response_text = item.content[0].text
                break

        if not response_text:
            raise HTTPException(status_code=500, detail="Failed to get response from AI model")
        
        logger.info(f"AI response generated: {response_text[:100]}...")
        
        # Prepare metadata
        metadata = {
            "model": model_name,
            "latency_ms": latency_ms
        }

        return response_text, metadata

    except Exception as e:
        logger.error(f"Error in get_ai_response: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again later."
        )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(database.get_db)):
    logger.info(f"Chat request received: {request.message[:100]}...")
    try:
        # Generate session_id if not provided
        session_id = request.session_id or uuid.uuid4()
        
        # Get or create conversation
        conversation = crud.get_or_create_conversation(db, session_id)
        
        # Log user message
        user_metadata = {"input_type": request.input_type}
        crud.create_message(
            db=db,
            conversation_id=conversation.id,
            role="user",
            content=request.message,
            extra_data_payload=user_metadata
        )
        
        # Get AI response with metadata
        reply, ai_metadata = await get_ai_response(request.message, request.history)
        
        # Log assistant message
        crud.create_message(
            db=db,
            conversation_id=conversation.id,
            role="assistant",
            content=reply,
            extra_data_payload=ai_metadata
        )
        
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
        # Transcribe the audio file using GPT-4o-transcribe
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
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

# Analytics endpoints
@app.get("/analytics/overview")
async def get_analytics_overview(db: Session = Depends(database.get_db)):
    """Get overview KPI metrics"""
    try:
        # Get current date and 30 days ago for comparison
        now = datetime.now()
        thirty_days_ago = now - timedelta(days=30)
        sixty_days_ago = now - timedelta(days=60)
        
        # Total conversations
        total_conversations = db.query(func.count(models.Conversation.id)).scalar()
        
        # Total messages
        total_messages = db.query(func.count(models.Message.id)).scalar()
        
        # Average response time (from assistant messages)
        avg_response_time = db.query(
            func.avg(func.cast(models.Message.extra_data['latency_ms'].astext, models.Float))
        ).filter(models.Message.role == 'assistant').scalar()
        
        # Conversations in last 30 days vs previous 30 days
        current_period_conversations = db.query(func.count(models.Conversation.id)).filter(
            models.Conversation.started_at >= thirty_days_ago
        ).scalar()
        
        previous_period_conversations = db.query(func.count(models.Conversation.id)).filter(
            models.Conversation.started_at >= sixty_days_ago,
            models.Conversation.started_at < thirty_days_ago
        ).scalar()
        
        # Calculate percentage change
        conv_change = 0
        if previous_period_conversations > 0:
            conv_change = ((current_period_conversations - previous_period_conversations) / previous_period_conversations) * 100
        
        # Messages in last 30 days vs previous 30 days
        current_period_messages = db.query(func.count(models.Message.id)).filter(
            models.Message.created_at >= thirty_days_ago
        ).scalar()
        
        previous_period_messages = db.query(func.count(models.Message.id)).filter(
            models.Message.created_at >= sixty_days_ago,
            models.Message.created_at < thirty_days_ago
        ).scalar()
        
        # Calculate percentage change
        msg_change = 0
        if previous_period_messages > 0:
            msg_change = ((current_period_messages - previous_period_messages) / previous_period_messages) * 100
        
        return {
            "total_conversations": total_conversations or 0,
            "total_messages": total_messages or 0,
            "avg_response_time": round(avg_response_time / 1000, 2) if avg_response_time else 0,  # Convert to seconds
            "conversations_change": round(conv_change, 1),
            "messages_change": round(msg_change, 1),
            "error_rate": 0.5  # Placeholder for now
        }
        
    except Exception as e:
        logger.error(f"Error in analytics overview: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching analytics overview")

@app.get("/analytics/conversations/daily")
async def get_daily_conversations(db: Session = Depends(database.get_db)):
    """Get daily conversation trends for the last 30 days"""
    try:
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        results = db.query(
            func.date(models.Conversation.started_at).label('date'),
            func.count(models.Conversation.id).label('conversations')
        ).filter(
            models.Conversation.started_at >= thirty_days_ago
        ).group_by(
            func.date(models.Conversation.started_at)
        ).order_by(
            func.date(models.Conversation.started_at)
        ).all()
        
        return [
            {
                "date": result.date.isoformat(),
                "conversations": result.conversations
            }
            for result in results
        ]
        
    except Exception as e:
        logger.error(f"Error in daily conversations: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching daily conversations")

@app.get("/analytics/messages/volume")
async def get_message_volume(db: Session = Depends(database.get_db)):
    """Get message volume by day (user vs assistant)"""
    try:
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        results = db.query(
            func.date(models.Message.created_at).label('date'),
            models.Message.role,
            func.count(models.Message.id).label('count')
        ).filter(
            models.Message.created_at >= seven_days_ago
        ).group_by(
            func.date(models.Message.created_at),
            models.Message.role
        ).order_by(
            func.date(models.Message.created_at)
        ).all()
        
        # Process results into the format expected by the dashboard
        data_dict = {}
        for result in results:
            date_str = result.date.strftime("%b %d")
            if date_str not in data_dict:
                data_dict[date_str] = {"date": date_str, "userMessages": 0, "assistantMessages": 0}
            
            if result.role == "user":
                data_dict[date_str]["userMessages"] = result.count
            elif result.role == "assistant":
                data_dict[date_str]["assistantMessages"] = result.count
        
        return list(data_dict.values())
        
    except Exception as e:
        logger.error(f"Error in message volume: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching message volume")

@app.get("/analytics/input-methods")
async def get_input_methods(db: Session = Depends(database.get_db)):
    """Get input method distribution (text vs voice)"""
    try:
        results = db.query(
            func.coalesce(models.Message.extra_data['input_type'].astext, 'text').label('input_type'),
            func.count(models.Message.id).label('count')
        ).filter(
            models.Message.role == 'user'
        ).group_by(
            models.Message.extra_data['input_type'].astext
        ).all()
        
        total_messages = sum(result.count for result in results)
        
        return [
            {
                "name": "Text Input" if result.input_type == "text" else "Voice Input",
                "value": round((result.count / total_messages) * 100, 1) if total_messages > 0 else 0,
                "color": "#8b5cf6" if result.input_type == "text" else "#06b6d4"
            }
            for result in results
        ]
        
    except Exception as e:
        logger.error(f"Error in input methods: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching input methods")

@app.get("/analytics/questions/top")
async def get_top_questions(db: Session = Depends(database.get_db)):
    """Get top 10 most frequent user questions"""
    try:
        results = db.query(
            models.Message.content,
            func.count(models.Message.id).label('count')
        ).filter(
            models.Message.role == 'user'
        ).group_by(
            models.Message.content
        ).order_by(
            desc(func.count(models.Message.id))
        ).limit(10).all()
        
        return [
            {
                "question": result.content,
                "count": result.count
            }
            for result in results
        ]
        
    except Exception as e:
        logger.error(f"Error in top questions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching top questions")

@app.get("/analytics/performance/response-times")
async def get_response_times(db: Session = Depends(database.get_db)):
    """Get response time trends by week"""
    try:
        four_weeks_ago = datetime.now() - timedelta(weeks=4)
        
        results = db.query(
            extract('week', models.Message.created_at).label('week'),
            extract('year', models.Message.created_at).label('year'),
            func.avg(func.cast(models.Message.extra_data['latency_ms'].astext, models.Float)).label('avg_time')
        ).filter(
            models.Message.role == 'assistant',
            models.Message.created_at >= four_weeks_ago,
            models.Message.extra_data['latency_ms'].astext != None
        ).group_by(
            extract('week', models.Message.created_at),
            extract('year', models.Message.created_at)
        ).order_by(
            extract('year', models.Message.created_at),
            extract('week', models.Message.created_at)
        ).all()
        
        return [
            {
                "date": f"Week {int(result.week)}",
                "responseTime": round(result.avg_time / 1000, 2) if result.avg_time else 0  # Convert to seconds
            }
            for result in results
        ]
        
    except Exception as e:
        logger.error(f"Error in response times: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching response times")
