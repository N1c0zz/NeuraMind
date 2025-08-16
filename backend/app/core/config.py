import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Keys - Railway le prenderà dalle environment variables
    openai_api_key: Optional[str] = None
    pinecone_api_key: Optional[str] = None
    dev_api_key: str = "super-secret-for-local"
    
    # Pinecone Config
    pinecone_environment: str = "gcp-starter"
    pinecone_index_name: str = "neuramind"
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Prendi le variabili da Railway
        if not self.openai_api_key:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.pinecone_api_key:
            self.pinecone_api_key = os.getenv("PINECONE_API_KEY")

settings = Settings()
