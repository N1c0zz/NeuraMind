import logging
from typing import List, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class PineconeService:
    def __init__(self):
        if not settings.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY non configurata")
        
        # Prova prima l'API nuova, poi fallback alla vecchia
        try:
            # API Nuova (3.x+)
            from pinecone import Pinecone
            
            logger.info("🆕 Usando Pinecone API nuova (3.x+)")
            self.pc = Pinecone(api_key=settings.pinecone_api_key)
            self.use_new_api = True
            
        except ImportError:
            # API Vecchia (2.x)
            import pinecone
            
            logger.info("🔄 Usando Pinecone API vecchia (2.x)")
            
            # Gestione errori per environment
            environments_to_try = [
                settings.pinecone_region,
                "us-east-1-aws",
                "us-east4-gcp", 
                "europe-west1-gcp",
                "asia-northeast1-gcp"
            ]
            
            for env in environments_to_try:
                try:
                    logger.info(f"Tentativo connessione environment: {env}")
                    pinecone.init(
                        api_key=settings.pinecone_api_key,
                        environment=env
                    )
                    self.pinecone_env = env
                    break
                except Exception as e:
                    logger.warning(f"Fallito environment {env}: {e}")
                    continue
            else:
                raise ValueError("Impossibile connettersi a nessun environment Pinecone")
            
            self.pc = pinecone
            self.use_new_api = False
        
        self.index_name = settings.pinecone_index_name
        
        # Verifica che l'indice esista
        self._ensure_index_exists()
        
        # Connettiti all'indice
        if self.use_new_api:
            self.index = self.pc.Index(self.index_name)
        else:
            self.index = self.pc.Index(self.index_name)

    def _ensure_index_exists(self):
        """Verifica che l'indice esista"""
        try:
            if self.use_new_api:
                # API Nuova
                existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            else:
                # API Vecchia
                existing_indexes = self.pc.list_indexes()
            
            logger.info(f"🔍 Indici disponibili: {existing_indexes}")
            logger.info(f"🎯 Cercando indice: {self.index_name}")
            
            if self.index_name not in existing_indexes:
                logger.error(f"❌ Indice {self.index_name} non trovato!")
                
                # Se ci sono altri indici, suggerisci di usare quelli
                if existing_indexes:
                    logger.info(f"� Indici disponibili che potresti usare:")
                    for idx in existing_indexes:
                        logger.info(f"   - {idx}")
                    logger.info(f"💡 Aggiorna PINECONE_INDEX su Railway con uno di questi nomi")
                else:
                    logger.info(f"💡 Nessun indice disponibile. Devi:")
                    logger.info(f"   1. Creare un indice su console.pinecone.io")
                    logger.info(f"   2. Verificare che l'API key sia corretta")
                
                raise ValueError(f"Indice {self.index_name} non trovato. Indici disponibili: {existing_indexes}")
            else:
                logger.info(f"✅ Indice {self.index_name} trovato!")
                
        except Exception as e:
            logger.error(f"Errore verifica indice: {e}")
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
            # Uguale per entrambe le API
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