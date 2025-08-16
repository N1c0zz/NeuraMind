import os
from pinecone import Pinecone, ServerlessSpec
from app.core.config import get_settings

settings = get_settings()

# Inizializza client
pc = Pinecone(api_key=settings.PINECONE_API_KEY)

def ensure_index():
    idx_name = settings.PINECONE_INDEX
    # Crea l'index se non esiste (dimensione 1536 = OpenAI embeddings small)
    if not pc.has_index(idx_name):
        pc.create_index(
            name=idx_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud=settings.PINECONE_CLOUD, region=settings.PINECONE_REGION),
            deletion_protection="disabled",
            tags={"env": "dev"}
        )
    return pc.Index(idx_name)

index = ensure_index()
