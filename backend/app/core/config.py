import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # API Keys
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    pinecone_api_key: Optional[str] = Field(default=None, alias="PINECONE_API_KEY")
    dev_api_key: str = Field(default="super-secret-for-local", alias="DEV_API_KEY")
    
    # Pinecone Config
    pinecone_index_name: str = Field(default="neuramind-index", alias="PINECONE_INDEX")
    pinecone_cloud: str = Field(default="aws", alias="PINECONE_CLOUD")
    pinecone_region: str = Field(default="us-east-1-aws", alias="PINECONE_REGION")
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        populate_by_name = True  # Permette uso di alias
        extra = "ignore"  # Ignora campi extra
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Fix per environment Pinecone
        if self.pinecone_region == "us-east-1":
            self.pinecone_region = "us-east-1-aws"

# Istanza globale
settings = Settings()

# Funzione per compatibilità con eventuali import
def get_settings() -> Settings:
    """Restituisce l'istanza delle impostazioni"""
    return settings