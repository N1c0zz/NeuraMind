# NeuraMind Backend

Backend API for NeuraMind - Personal AI Assistant

## Features
- 🧠 **RAG (Retrieval-Augmented Generation)** - Semantic search over personal documents
- 🔍 **Vector Search** - Powered by Pinecone for fast similarity search  
- 🤖 **OpenAI Integration** - GPT-4o-mini for intelligent responses
- 📚 **Document Processing** - Automatic text chunking and embedding

## Quick Start

### 1. Setup Environment
```bash
# Create virtual environment
python -m venv .venv
source .venv/Scripts/activate  # Windows
# source .venv/bin/activate    # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Copy `.env.example` to `.env` and fill your API keys:
```bash
cp .env.example .env
```

Required variables:
- `OPENAI_API_KEY` - Your OpenAI API key
- `PINECONE_API_KEY` - Your Pinecone API key

### 3. Run Server
```bash
python run_server.py
```

Server will be available at: http://127.0.0.1:8000

## API Documentation
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## API Endpoints

### Core Endpoints
- `GET /v1/health` - Health check
- `POST /v1/embed-upsert` - Store documents in vector DB
- `POST /v1/query` - Semantic search
- `POST /v1/answer` - Generate AI responses

### Typical Workflow
1. **Upsert** → Store your documents/notes
2. **Query** → Find relevant information  
3. **Answer** → Get AI-generated responses

## Testing
```bash
# Simple connectivity test
python scripts/simple_test.py

# Full API test
python scripts/test_api.py
```

## Project Structure
```
backend/
├── app/                    # Main application
│   ├── api/               # API routes
│   ├── core/              # Configuration
│   ├── services/          # Business logic
│   └── main.py           # FastAPI app
├── scripts/               # Test & utility scripts
├── run_server.py         # Server launcher
└── requirements.txt      # Dependencies
```
