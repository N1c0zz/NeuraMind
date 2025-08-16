from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_INDEX: str = "neuramind-dev"
    PINECONE_CLOUD: str = "aws"
    PINECONE_REGION: str = "us-east-1"
    DEV_API_KEY: str = "change-me"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
