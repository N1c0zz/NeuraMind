import logging
from typing import List, Dict, Any
import pinecone
from app.core.config import settings

logger = logging.getLogger(__name__)

class PineconeService:
    def __init__(self):
        if not settings.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY non configurata")
        
        # Inizializza Pinecone (versione 2.2.4) con gestione errori
        try:
            # Prova environment diversi per Pinecone
            environments_to_try = [
                "us-east-1-aws",
                "us-east4-gcp", 
                "europe-west1-gcp",
                "asia-northeast1-gcp"
            ]
            
            pinecone_env = settings.pinecone_region
            if pinecone_env == "us-east-1":
                pinecone_env = "us-east-1-aws"
            
            logger.info(f"Tentativo connessione Pinecone environment: {pinecone_env}")
            
            pinecone.init(
                api_key=settings.pinecone_api_key,
                environment=pinecone_env
            )
            
        except Exception as e:
            logger.error(f"Errore connessione Pinecone con {pinecone_env}: {e}")
            # Prova environment di default
            try:
                logger.info("Tentativo con environment di default us-east-1-aws")
                pinecone.init(
                    api_key=settings.pinecone_api_key,
                    environment="us-east-1-aws" 
                )
            except Exception as e2:
                logger.error(f"Errore anche con environment di default: {e2}")
                raise ValueError(f"Impossibile connettersi a Pinecone. Verifica API key e environment.")
        
        self.index_name = settings.pinecone_index_name
        
        # Assicurati che l'indice esista
        self._ensure_index_exists()
        
        # Connettiti all'indice
        self.index = pinecone.Index(self.index_name)

    def _ensure_index_exists(self):
        """Crea l'indice se non esiste"""
        try:
            existing_indexes = pinecone.list_indexes()
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creazione indice Pinecone: {self.index_name}")
                
                pinecone.create_index(
                    name=self.index_name,
                    dimension=1536,  # OpenAI embeddings dimension
                    metric='cosine'
                )
                logger.info(f"Indice {self.index_name} creato con successo")
            else:
                logger.info(f"Indice {self.index_name} già esistente")
                
        except Exception as e:
            logger.error(f"Errore configurazione Pinecone: {e}")
            raise

    def upsert_vectors(self, vectors: List[Dict[str, Any]]) -> bool:
        """Inserisce/aggiorna vettori in Pinecone"""
        try:
            response = self.index.upsert(vectors=vectors)
            logger.info(f"Upsert completato: {response}")
            return True
        except Exception as e:
            logger.error(f"Errore upsert: {e}")
            raise

    def query_vectors(self, query_vector: List[float], top_k: int = 5, 
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