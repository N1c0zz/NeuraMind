import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(
    title="NeuraMind API",
    description="AI Assistant with RAG capabilities",
    version="1.0.0"
)

# CORS per frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/v1")

@app.get("/")
async def root():
    return {
        "message": "NeuraMind API is running", 
        "docs": "/docs",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "local")
    }

@app.get("/health")
async def health():
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
