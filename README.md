# Anytime Fitness AI Agent

An intelligent conversational AI chatbot designed specifically for Anytime Fitness India. This full-stack application provides a seamless chat interface with voice capabilities, powered by OpenAI's GPT-4 and vector search technology for gym-specific knowledge retrieval.

## 🎯 Overview

The Anytime Fitness AI Agent serves as a virtual receptionist that can answer questions about gym services, membership plans, facilities, and general fitness-related inquiries. It leverages OpenAI's vector search capabilities to provide accurate, contextual responses based on Anytime Fitness's internal knowledge base.

### Key Features

- **Intelligent Chat Interface**: Natural language conversations with context awareness
- **Voice Integration**: Speech-to-text input and text-to-speech output capabilities
- **Knowledge Base Integration**: Vector search through Anytime Fitness-specific content
- **Session Management**: Persistent conversations with unique session tracking
- **User Feedback System**: Thumbs up/down rating system for response quality
- **Real-time Analytics**: Response time tracking and conversation logging
- **Production Ready**: Docker containerization with PostgreSQL database

## 🏗️ Project Structure

```
AnytimeFitnessAgent/
├── ai_agent/                          # Main application directory
│   ├── backend/                       # FastAPI backend service
│   │   ├── __pycache__/              # Python cache files
│   │   ├── Dockerfile                # Backend container configuration
│   │   ├── database.py               # Database connection and session management
│   │   ├── main.py                   # FastAPI application with API endpoints
│   │   ├── models.py                 # SQLAlchemy ORM models
│   │   └── requirements.txt          # Python dependencies
│   └── frontend/                     # React frontend application
│       ├── Dockerfile                # Frontend container configuration
│       ├── README.md                 # React/Vite template documentation
│       ├── eslint.config.js          # ESLint configuration
│       ├── index.html                # HTML entry point
│       ├── nginx.conf                # Nginx configuration for production
│       ├── node_modules/             # Node.js dependencies
│       ├── package-lock.json         # Dependency lock file
│       ├── package.json              # Node.js dependencies and scripts
│       ├── postcss.config.js         # PostCSS configuration
│       ├── public/                   # Static assets
│       │   └── vite.svg              # Vite logo
│       ├── src/                      # React source code
│       │   ├── App.jsx               # Main React component
│       │   ├── assets/               # Application assets
│       │   ├── index.css             # Global styles
│       │   └── main.jsx              # React entry point
│       ├── tailwind.config.js        # Tailwind CSS configuration
│       └── vite.config.js            # Vite build configuration
├── deploy.md                         # Comprehensive deployment guide
├── docker-compose.yml                # Multi-container orchestration
├── schema.sql                        # PostgreSQL database schema
└── venv/                            # Python virtual environment
```

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL with SQLAlchemy ORM (async)
- **AI/ML**: OpenAI GPT-4.1-mini with vector search
- **Authentication**: Session-based with UUID tracking
- **Audio Processing**: OpenAI Whisper (transcription) and TTS models
- **Deployment**: Docker with uvicorn ASGI server

### Frontend  
- **Framework**: React 19 with Vite
- **Styling**: Tailwind CSS with Typography plugin
- **UI Components**: Lucide React icons
- **Markdown**: ReactMarkdown with GitHub Flavored Markdown support
- **Audio**: Web Audio API for recording and playback
- **Build Tool**: Vite with hot module replacement
- **Deployment**: Nginx in Docker container

### Infrastructure
- **Containerization**: Docker and Docker Compose
- **Database**: PostgreSQL 16 with Alpine Linux
- **Reverse Proxy**: Nginx for frontend serving
- **Environment Management**: dotenv for configuration

## 📊 Database Schema

The application uses a PostgreSQL database with the following structure:

### Tables

#### `conversations`
- Tracks unique chat sessions
- **Columns**: `id`, `session_id` (UUID), `user_agent`, `created_at`

#### `chat_messages`  
- Stores all user queries and AI responses
- **Columns**: `id`, `conversation_id`, `role`, `content`, `response_time_ms`, `is_unanswered`, `api_metadata`, `created_at`
- **Constraints**: Role must be 'user' or 'assistant'

#### `user_feedback`
- Captures user satisfaction ratings
- **Columns**: `id`, `message_id`, `rating`, `comment`, `created_at`  
- **Constraints**: Rating must be -1 (negative) or 1 (positive)

### Relationships
- One-to-many: `conversations` → `chat_messages`
- One-to-one: `chat_messages` → `user_feedback`
- Cascade deletes ensure data integrity

## 🚀 API Endpoints

### Core Chat API
- `POST /chat` - Process user messages and return AI responses
- `POST /feedback` - Submit user feedback for message quality
- `GET /health` - Health check endpoint

### Audio Features
- `POST /transcribe` - Convert audio to text using Whisper
- `POST /speak` - Convert text to speech using OpenAI TTS

### Request/Response Models
All endpoints use Pydantic models for validation:
- `ChatRequest` - User message with conversation history
- `ChatResponse` - AI response with message ID
- `FeedbackRequest` - User rating submission
- `SpeakRequest` - Text-to-speech conversion

## 🎨 Frontend Architecture

### Component Structure
- **App.jsx**: Main application component handling all chat functionality
- **State Management**: React hooks for local state (messages, session, UI states)
- **Audio Integration**: MediaRecorder API for voice input, Audio API for playback
- **Real-time Updates**: Automatic scrolling and loading states

### Key Features Implementation
- **Session Persistence**: UUID-based sessions stored in sessionStorage
- **Voice Recording**: Real-time audio capture with visual feedback
- **Markdown Rendering**: Full markdown support for AI responses
- **Error Handling**: Comprehensive error boundaries with user-friendly messages
- **Responsive Design**: Mobile-first approach with Tailwind CSS

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here
VECTOR_STORE_ID=your_vector_store_id_here
DATABASE_URL=postgresql+asyncpg://af_user:password@localhost:5432/anytime_fitness_chatbot

# Optional
PORT=8000
HOST=0.0.0.0
ALLOWED_ORIGINS=*
LOG_LEVEL=INFO
ENVIRONMENT=production
```

#### Frontend (.env.production)
```bash
VITE_API_BASE_URL=http://localhost:8000
```

### Docker Configuration
The application is fully containerized with:
- **Multi-stage frontend build** for optimized production bundles
- **Development mode backend** with hot reload capabilities
- **PostgreSQL service** with health checks and data persistence
- **Network isolation** between services

## 🚦 Getting Started

### Prerequisites
- Docker and Docker Compose
- OpenAI API key with GPT-4 access
- Vector Store ID (OpenAI Assistants API)

### Quick Start
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AnytimeFitnessAgent
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI credentials
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - Health check: http://localhost:8000/health

### Development Setup
For local development without Docker:

1. **Backend setup**
   ```bash
   cd ai_agent/backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Frontend setup**
   ```bash
   cd ai_agent/frontend
   npm install
   npm run dev
   ```

## 📈 Monitoring and Analytics

### Logging
- **Backend logs**: `/tmp/af_backend.log` and console output
- **Structured logging**: JSON format with timestamps and request IDs
- **Error tracking**: Full stack traces for debugging

### Performance Metrics
- **Response times**: Tracked per API call in milliseconds
- **Token usage**: OpenAI API consumption monitoring
- **User engagement**: Session duration and message counts
- **Quality metrics**: User feedback aggregation

### Health Checks
- Database connectivity validation
- OpenAI API availability checks
- Container health monitoring

## 🛡️ Security Features

- **CORS Configuration**: Configurable allowed origins
- **Input Validation**: Pydantic models for all API inputs
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **Environment Isolation**: Secrets managed through environment variables
- **Session Security**: UUID-based session identifiers

## 🚀 Deployment

The project includes comprehensive deployment documentation in `deploy.md` covering:
- Production environment setup
- VM deployment procedures
- Port configuration and firewall settings
- Monitoring and troubleshooting guides
- Performance optimization tips

### Production Considerations
- Use specific CORS origins instead of wildcards
- Implement HTTPS with SSL certificates
- Set up database backups and monitoring
- Configure log rotation and retention policies
- Monitor API rate limits and costs

## 🤝 Contributing

This project follows standard Git workflow practices:
- **Current branch**: `dashboard` (development)
- **Main branch**: `main` (production)
- Recent improvements include Docker optimization and deployment enhancements

## 📄 License

This project is proprietary software developed for Anytime Fitness India.

---

**Note**: This AI agent is specifically designed for Anytime Fitness operations and includes gym-specific knowledge and branding. The vector search capabilities are tailored to Anytime Fitness's internal documentation and FAQ content.