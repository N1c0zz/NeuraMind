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
- `PINECONE_INDEX` - Index name (default: neuramind-index)

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
- `GET /v1/debug` - Debug info (with API key)
- `POST /v1/embed-upsert` - Store documents in vector DB
- `POST /v1/query` - Semantic search
- `POST /v1/answer` - Generate AI responses

### Typical Workflow
1. **Upsert** → Store your documents/notes
2. **Query** → Find relevant information  
3. **Answer** → Get AI-generated responses

## Testing
```bash
# Complete workflow test
python test_essential.py

# Quick health check
python test_essential.py quick

# Railway debug (for production)
python debug_railway.py
```

## Deployment (Railway)

### Environment Variables
Set these on Railway dashboard:
```
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX=neuramind-index
PINECONE_REGION=us-east-1-aws
PINECONE_CLOUD=aws
DEV_API_KEY=super-secret-for-local
```

### Troubleshooting Railway
1. **Pinecone not found**: Check if index exists in your Pinecone console
2. **OpenAI errors**: Ensure latest dependencies with `openai>=1.35.0`
3. **Debug info**: Use `/v1/debug` endpoint to check configuration

## Project Structure
```
backend/
├── app/                    # Main application
│   ├── api/               # API routes
│   ├── core/              # Configuration
│   ├── services/          # Business logic
│   └── main.py           # FastAPI app
├── scripts/               # Utility scripts
├── test_essential.py     # Main test file
├── debug_railway.py      # Production debug
└── requirements.txt      # Dependencies
```

## Recent Fixes
- ✅ **Pinecone Connection**: Fixed for new serverless architecture
- ✅ **OpenAI Client**: Simplified initialization without deprecated parameters
- ✅ **Code Cleanup**: Removed duplicate test files
- ✅ **Railway Compatibility**: Updated dependencies for production deployment
