# 🏋️‍♂️ Anytime Fitness AI Agent

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.13-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)](https://www.postgresql.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4.1--mini-412991?logo=openai)](https://openai.com/)
[![HubSpot](https://img.shields.io/badge/HubSpot-CRM-FF5722?logo=hubspot)](https://www.hubspot.com/)

> **A next-generation AI-powered customer engagement platform** for Anytime Fitness India, featuring intelligent conversation management, real-time analytics, automated lead generation, and comprehensive testing infrastructure.

## 🖼️ Application Screenshots

### Chat Interface
![Chat Interface](screenshots/chat-interface.png)
*Modern React 19 chat interface with voice and text input capabilities*

### Analytics Dashboard
![Analytics Dashboard](screenshots/analytics-dashboard.png)
*Real-time analytics dashboard with comprehensive KPIs and data visualization*

### Voice Processing
![Voice Processing](screenshots/voice-processing.png)
*Real-time speech-to-text with intelligent silence detection*

### Lead Generation
![Lead Generation](screenshots/lead-generation.png)
*Automated HubSpot CRM integration with progressive qualification*

## ✨ Core Capabilities

- **🎯 Intelligent Conversational AI** - GPT-4.1-mini powered chatbot with context-aware responses
- **🎤 Voice-First Experience** - Real-time speech-to-text and text-to-speech with silence detection
- **📊 Real-Time Analytics** - Live KPI monitoring, usage trends, and performance metrics
- **🔄 Automated Lead Generation** - HubSpot CRM integration with progressive qualification
- **🧪 Advanced Testing Suite** - 24 AI-powered personas with authentic Indian life contexts
- **🌐 Multi-Platform Support** - Web, mobile-responsive, and API-first architecture

## 🏗️ Architecture Overview

### System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[React Frontend<br/>Port 5173]
        B[Analytics Dashboard<br/>Port 4173]
    end
    
    subgraph "Backend Layer"
        C[FastAPI Backend<br/>Port 7479]
        D[Test Suite<br/>AI Personas]
    end
    
    subgraph "Database Layer"
        E[PostgreSQL 15<br/>Port 5432]
    end
    
    subgraph "External Services"
        F[OpenAI API<br/>GPT-4.1-mini]
        G[HubSpot CRM<br/>Lead Generation]
        H[Vector Store<br/>Knowledge Base]
    end
    
    A --> C
    B --> C
    C --> E
    D --> E
    C --> F
    C --> G
    C --> H
    
    style A fill:#61DAFB,stroke:#333,stroke-width:1px
    style B fill:#4A86E8,stroke:#333,stroke-width:1px
    style C fill:#00C0A3,stroke:#333,stroke-width:1px
    style D fill:#FF9E4A,stroke:#333,stroke-width:1px
    style E fill:#E0F7FA,stroke:#336791,stroke-width:1px
    style F fill:#FFFFFF,stroke:#412991,stroke-width:1px
    style G fill:#FF6B35,stroke:#333,stroke-width:1px
    style H fill:#10B981,stroke:#333,stroke-width:1px
```

### Data Flow Architecture

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Database
    participant OpenAI
    participant HubSpot
    
    User->>Frontend: Send message (text/voice)
    Frontend->>Backend: POST /chat
    Backend->>OpenAI: Transcribe audio (if voice)
    OpenAI-->>Backend: Transcription text
    Backend->>OpenAI: Chat completion with context
    OpenAI-->>Backend: AI response
    Backend->>Database: Store conversation
    
    alt Lead detected
        Backend->>HubSpot: Create/update lead
        HubSpot-->>Backend: Lead confirmation
    end
    
    Backend-->>Frontend: Response + metadata
    Frontend->>OpenAI: TTS (if enabled)
    OpenAI-->>Frontend: Audio response
    Frontend-->>User: Display/play response
```

## 📊 Key Features & Differentiators

### 🎯 **Intelligent Customer Engagement**
- **Context-Aware Conversations** - Maintains conversation history and context
- **Multi-Modal Input** - Text, voice, and mixed interaction support
- **Personalized Responses** - Tailored to Anytime Fitness India's brand voice
- **Progressive Lead Qualification** - 5-phase automated lead nurturing

### 📈 **Advanced Analytics & Monitoring**
- **Real-Time KPIs** - Live monitoring of conversations, response times, and user engagement
- **Cost Optimization** - Token usage tracking and cost analysis by model
- **Performance Insights** - Response time trends, transcription analytics, and error rates
- **Content Intelligence** - Top user questions, knowledge coverage, and interaction patterns

### 🔄 **Automated Lead Generation**
- **HubSpot Integration** - Seamless CRM sync with automated contact creation
- **Progressive Qualification** - Multi-stage lead nurturing process
- **Conversation Analysis** - AI-powered lead scoring and qualification
- **Sales Pipeline Management** - Automated lead routing and follow-up

### 🧪 **Comprehensive Testing Infrastructure**
- **24 AI Personas** - Realistic user simulation with authentic Indian contexts
- **Automated Testing** - Continuous validation of conversation quality
- **Performance Benchmarking** - Response time, accuracy, and engagement metrics
- **Lead Generation Testing** - Automated validation of CRM integration

## 🛠️ Technology Stack

### **Frontend Technologies**
- **React 19** - Latest React with concurrent features
- **Vite 6.x** - Next-generation build tool
- **Tailwind CSS 4.x** - Utility-first CSS framework
- **TypeScript 5.8** - Type-safe JavaScript
- **shadcn/ui** - Modern React component library
- **Recharts 3.0** - Powerful data visualization

### **Backend Technologies**
- **FastAPI 0.115.13** - Modern Python web framework
- **PostgreSQL 15** - Advanced relational database
- **SQLAlchemy 2.0** - Python ORM with async support
- **OpenAI API 1.88.0** - State-of-the-art AI integration
- **uvicorn 0.34.3** - ASGI server for production
- **Docker** - Containerized development environment

### **AI & Integration**
- **OpenAI GPT-4.1-mini** - Primary conversation model
- **OpenAI Responses API** - Advanced conversation handling
- **Vector Search** - Knowledge base integration
- **HubSpot CRM API** - Lead generation and management
- **Web Audio API** - Real-time audio processing

## 🚀 Quick Start

### Prerequisites
- **Node.js 18+** and **npm**
- **Python 3.12+** and **pip**
- **PostgreSQL 15+**
- **Docker** (optional)

### 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/shahshlok/AnytimeFitnessAgent.git
   cd AnytimeFitnessAgent
   ```

2. **Backend Setup**
   ```bash
   cd ai_agent/backend
   pip install -r ../../requirements.txt
   
   # Create .env file with:
   # OPENAI_API_KEY=your_key_here
   # VECTOR_STORE_ID=your_vector_store_id
   # DATABASE_URL=postgresql://user:pass@localhost/dbname
   # HUBSPOT_PERSONAL_KEY=your_hubspot_key
   ```

3. **Frontend Setup**
   ```bash
   cd ai_agent/frontend
   npm install
   ```

4. **Dashboard Setup**
   ```bash
   cd ai_agent/dashboard
   npm install
   ```

5. **Database Setup**
   ```bash
   # Using Docker (recommended)
   docker-compose up -d
   
   # Or manual PostgreSQL setup
   # Create database and run migrations
   ```

### 🎯 Development Commands

```bash
# Start all services
docker-compose up -d                      # Database
cd ai_agent/backend && python main.py    # Backend (port 7479)
cd ai_agent/frontend && npm run dev      # Frontend (port 5173)
cd ai_agent/dashboard && npm run dev     # Dashboard (port 4173)
```

### 🧪 Testing Suite

```bash
cd ai_agent/backend

# Setup test database
python -m test_suite.main --setup-db

# Run all test personas
python -m test_suite.main --scenario all

# Run specific persona types
python -m test_suite.main --filter-by-type life_context_test
python -m test_suite.main --filter-by-type franchise_prospect
python -m test_suite.main --filter-by-type edge_case

# Generate AI conversation summaries
python -m test_suite.main --generate-summaries
```

## 📊 Performance & Metrics

### **Response Time Benchmarks**
- **Chat Response**: < 2 seconds average
- **Voice Transcription**: < 1 second average
- **Text-to-Speech**: < 1.5 seconds average
- **Database Queries**: < 100ms average

### **Scalability Features**
- **Async/Await Architecture** - High concurrency support
- **Database Connection Pooling** - Optimized PostgreSQL connections
- **Caching Layer** - Redis-ready architecture
- **Load Balancer Ready** - Stateless design for horizontal scaling

### **Security & Privacy**
- **Environment-based Configuration** - Secure API key management
- **CORS Protection** - Configurable cross-origin policies
- **Input Validation** - Pydantic models for data validation
- **Session Management** - Privacy-focused UUID sessions

## 🎯 Advanced Features

### **AI-Powered Personas Testing**

```mermaid
graph LR
    subgraph "Test Suite Architecture"
        A[Test Runner] --> B[Persona Manager]
        B --> C[24 AI Personas]
        C --> D[Conversation Runner]
        D --> E[Backend API]
        E --> F[Test Database]
        D --> G[Conversation Analyzer]
        G --> H[AI Summaries]
    end
    
    style A fill:#FF9E4A,stroke:#333,stroke-width:1px
    style B fill:#C8E6C9,stroke:#333,stroke-width:1px
    style C fill:#BBDEFB,stroke:#333,stroke-width:1px
    style D fill:#D1C4E9,stroke:#333,stroke-width:1px
    style E fill:#00C0A3,stroke:#333,stroke-width:1px
    style F fill:#E3F2FD,stroke:#336791,stroke-width:1px
    style G fill:#FFCCBC,stroke:#333,stroke-width:1px
    style H fill:#F5F5F5,stroke:#333,stroke-width:1px
```

24 diverse personas including:
- **Life Context Personas** - Authentic Indian life situations
- **Franchise Business Personas** - Investment and operational scenarios
- **Edge Case Personas** - Security, privacy, and technical testing

### **Real-Time Analytics Dashboard**
- **Executive KPIs** - High-level metrics for business decisions
- **Usage Trends** - Daily/weekly conversation patterns
- **Cost Analysis** - Token usage and API cost tracking
- **Performance Monitoring** - Response time and error rate tracking

### **Automated Lead Generation**

```mermaid
flowchart TD
    A[User Interaction] --> B{Interest Detected?}
    B -->|Yes| C[Phase 1: Basic Info]
    B -->|No| D[Continue Chat]
    C --> E[Phase 2: Needs Assessment]
    E --> F[Phase 3: Budget Qualification]
    F --> G[Phase 4: Timeline & Urgency]
    G --> H[Phase 5: Contact Collection]
    H --> I[Create HubSpot Lead]
    I --> J[Lead Routing & Follow-up]
    
    style A fill:#61DAFB,stroke:#333,stroke-width:1px
    style B fill:#FF9E4A,stroke:#333,stroke-width:1px
    style C fill:#34D399,stroke:#333,stroke-width:1px
    style E fill:#34D399,stroke:#333,stroke-width:1px
    style F fill:#34D399,stroke:#333,stroke-width:1px
    style G fill:#34D399,stroke:#333,stroke-width:1px
    style H fill:#34D399,stroke:#333,stroke-width:1px
    style I fill:#FF6B35,stroke:#333,stroke-width:1px
    style J fill:#EDE7F6,stroke:#8B5CF6,stroke-width:1px
```

- **Progressive Qualification** - 5-phase lead nurturing
- **HubSpot Integration** - Automated CRM sync
- **Conversation Analysis** - AI-powered lead scoring
- **Sales Pipeline** - Automated lead routing

## 🔧 API Documentation

### **Core Endpoints**

#### Chat API
```http
POST /chat
Content-Type: application/json

{
  "message": "I'm interested in joining a gym",
  "session_id": "uuid-here",
  "input_type": "text"
}
```

#### Analytics API
```http
GET /analytics/overview
GET /analytics/conversations/daily
GET /analytics/messages/volume
GET /analytics/performance/response-times
```

#### Voice Processing
```http
POST /transcribe
Content-Type: multipart/form-data

# Audio file upload for speech-to-text

POST /speak
Content-Type: application/json

{
  "text": "Welcome to Anytime Fitness!",
  "voice": "alloy"
}
```

## 📁 Project Structure

```
AnytimeFitnessAgent/
├── ai_agent/
│   ├── backend/                    # FastAPI Python backend
│   │   ├── main.py                # Main application entry point
│   │   ├── models.py              # SQLAlchemy database models
│   │   ├── database.py            # Database configuration
│   │   ├── crud.py                # Database operations
│   │   ├── hubspot_integration.py # HubSpot CRM integration
│   │   └── test_suite/            # Automated testing suite
│   │       ├── main.py            # Test runner CLI
│   │       ├── persona.json       # 24 AI personas
│   │       ├── persona_manager.py # Persona management
│   │       └── conversation_runner.py # Test execution
│   ├── frontend/                   # React 19 chat interface
│   │   ├── src/
│   │   │   ├── App.jsx            # Main chat component
│   │   │   └── index.css          # Tailwind CSS styles
│   │   └── package.json           # Frontend dependencies
│   └── dashboard/                  # React 19 + TypeScript dashboard
│       ├── src/
│       │   ├── dashboard.tsx      # Analytics dashboard
│       │   ├── components/ui/     # shadcn/ui components
│       │   └── main.tsx           # Dashboard entry point
│       └── package.json           # Dashboard dependencies
├── requirements.txt                # Python dependencies
├── docker-compose.yml             # Development environment
└── README.md                      # This file
```

## 👥 Contributing

We welcome contributions! Please follow these guidelines:

### **Development Setup**
1. Fork the repository
2. Create a feature branch
3. Follow the coding standards
4. Add comprehensive tests
5. Submit a pull request

### **Code Standards**
- **Python**: Follow PEP 8 with Black formatting
- **JavaScript/TypeScript**: ESLint with Prettier
- **Git**: Conventional commits for clear history
- **Testing**: Comprehensive test coverage required

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


**Built with ❤️ by Shlok Shah** | **Powered by AI** | **Designed for Scale**

*This project showcases modern full-stack development, AI integration, and enterprise-grade software engineering practices.*
