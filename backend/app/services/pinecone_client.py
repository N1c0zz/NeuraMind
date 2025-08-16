import logging
from typing import List, Dict, Any
from pinecone import Pinecone, ServerlessSpec
from app.core.config import settings

logger = logging.getLogger(__name__)

class PineconeService:
    def __init__(self):
        if not settings.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY non configurata")
        
        self.pc = Pinecone(api_key=settings.pinecone_api_key)
        self.index_name = settings.pinecone_index_name
        
        # Assicurati che l'indice esista
        self._ensure_index_exists()
        
        # Connettiti all'indice
        self.index = self.pc.Index(self.index_name)

    def _ensure_index_exists(self):
        """Crea l'indice se non esiste"""
        try:
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creazione indice Pinecone: {self.index_name}")
                
                self.pc.create_index(
                    name=self.index_name,
                    dimension=1536,  # OpenAI embeddings dimension
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud=settings.pinecone_cloud,
                        region=settings.pinecone_region
                    )
                )
                logger.info(f"Indice {self.index_name} creato con successo")
            else:
                logger.info(f"Indice {self.index_name} già esistente")
                
        except Exception as e:
            logger.error(f"Errore configurazione Pinecone: {e}")
            raise

    async def upsert_vectors(self, vectors: List[Dict[str, Any]]) -> bool:
        """Inserisce/aggiorna vettori in Pinecone"""
        try:
            response = self.index.upsert(vectors=vectors)
            logger.info(f"Upsert completato: {response}")
            return True
        except Exception as e:
            logger.error(f"Errore upsert: {e}")
            raise

    async def query_vectors(self, query_vector: List[float], top_k: int = 5, 
                          filter_dict: Dict = None) -> List[Dict]:
        """Cerca vettori simili"""
        try:
            response = self.index.query(
                vector=query_vector,
                top_k=top_k,
                filter=filter_dict,
                include_metadata=True,
                include_values=False
            )
            
            matches = []
            for match in response.matches:
                matches.append({
                    "id": match.id,
                    "score": float(match.score),
                    "metadata": match.metadata
                })
            
            return matches
        except Exception as e:
            logger.error(f"Errore query: {e}")
            raise