import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Keys
    openai_api_key: Optional[str] = None
    pinecone_api_key: Optional[str] = None
    dev_api_key: str = "super-secret-for-local"
    
    # Pinecone Config
    pinecone_index_name: str = "neuramind-index"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1-aws"  # Formato corretto per Pinecone 2.x
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Prendi le variabili da Railway
        self.openai_api_key = os.getenv("OPENAI_API_KEY", self.openai_api_key)
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY", self.pinecone_api_key)
        self.pinecone_index_name = os.getenv("PINECONE_INDEX", self.pinecone_index_name)
        self.pinecone_cloud = os.getenv("PINECONE_CLOUD", self.pinecone_cloud)
        self.pinecone_region = os.getenv("PINECONE_REGION", self.pinecone_region)

# Istanza globale
settings = Settings()

# Funzione per compatibilità con eventuali import
def get_settings() -> Settings:
    """Restituisce l'istanza delle impostazioni"""
    return settings