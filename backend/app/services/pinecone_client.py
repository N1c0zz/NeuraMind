import logging
from typing import List, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class PineconeService:
    def __init__(self):
        if not settings.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY non configurata")
        
        # Usa solo l'API nuova (3.x+)
        try:
            from pinecone import Pinecone
            
            logger.info("🆕 Inizializzazione Pinecone 3.x+")
            self.pc = Pinecone(api_key=settings.pinecone_api_key)
            logger.info("✅ Pinecone client inizializzato")
            
        except ImportError as e:
            logger.error(f"❌ Pinecone 3.x non disponibile: {e}")
            raise ValueError("Pinecone 3.x+ richiesto. Aggiorna requirements.txt")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione Pinecone: {e}")
            raise ValueError(f"Impossibile inizializzare Pinecone: {e}")
        
        self.index_name = settings.pinecone_index_name
        
        # Verifica che l'indice esista
        self._ensure_index_exists()
        
        # Connettiti all'indice
        self.index = self.pc.Index(self.index_name)

    def _ensure_index_exists(self):
        """Verifica che l'indice esista"""
        try:
            logger.info(f"🔍 Verifica indice {self.index_name}...")
            
            # Lista indici con API 3.x (nuova architettura)
            indexes_response = self.pc.list_indexes()
            existing_indexes = [idx.name for idx in indexes_response]
            
            logger.info(f"📊 Indici esistenti: {existing_indexes}")
            logger.info(f"🎯 Indice cercato: {self.index_name}")
            
            if self.index_name not in existing_indexes:
                logger.error(f"❌ Indice {self.index_name} non trovato!")
                logger.info(f"💡 Debug info:")
                logger.info(f"   - API Key: {settings.pinecone_api_key[:15]}...{settings.pinecone_api_key[-5:]}")
                logger.info(f"   - Indici disponibili: {existing_indexes}")
                
                if existing_indexes:
                    logger.info(f"💡 Indici che potresti usare:")
                    for idx in existing_indexes:
                        logger.info(f"   - {idx}")
                    logger.info(f"💡 Aggiorna PINECONE_INDEX su Railway")
                else:
                    logger.info(f"💡 Nessun indice trovato - verifica console.pinecone.io")
                
                raise ValueError(f"Indice {self.index_name} non trovato. Indici disponibili: {existing_indexes}")
            else:
                logger.info(f"✅ Indice {self.index_name} trovato!")
                
                # Per la nuova architettura, mostra anche l'host dell'indice
                try:
                    index_info = next(idx for idx in indexes_response if idx.name == self.index_name)
                    if hasattr(index_info, 'host'):
                        logger.info(f"🌐 Host indice: {index_info.host}")
                except Exception as host_e:
                    logger.debug(f"Info host non disponibile: {host_e}")
                
        except Exception as e:
            logger.error(f"❌ Errore verifica indice: {e}")
            logger.error(f"💡 Possibili cause:")
            logger.error(f"   - API key non valida")
            logger.error(f"   - Indice in region diversa")
            logger.error(f"   - Problemi di rete")
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
                     filter_dict: Dict = None, include_metadata: bool = True) -> List[Dict]:
        """Cerca vettori simili"""
        try:
            # API 3.x
            response = self.index.query(
                vector=query_vector,
                top_k=top_k,
                filter=filter_dict,
                include_metadata=include_metadata,
                include_values=False
            )
            
            matches = []
            for match in response.matches:
                match_data = {
                    "id": match.id,
                    "score": float(match.score)
                }
                if include_metadata and hasattr(match, 'metadata'):
                    match_data["metadata"] = match.metadata
                matches.append(match_data)
            
            return matches
        except Exception as e:
            logger.error(f"Errore query: {e}")
            raise

    def list_vectors_by_filter(self, filter_dict: Dict, limit: int = 1000) -> List[Dict]:
        """Lista vettori usando un filtro - metodo alternativo per recuperare documenti"""
        try:
            # Prova con stats per vedere cosa c'è nell'indice
            stats_response = self.index.describe_index_stats()
            logger.info(f"Stats indice: {stats_response}")
            
            # Metodo alternativo: usa query con un vettore di tutti zeri
            # ma con score molto basso per catturare tutti i match
            zero_vector = [0.0] * 1536
            
            response = self.index.query(
                vector=zero_vector,
                top_k=limit,
                filter=filter_dict,
                include_metadata=True,
                include_values=False
            )
            
            matches = []
            for match in response.matches:
                matches.append({
                    "id": match.id,
                    "score": float(match.score),
                    "metadata": match.metadata if hasattr(match, 'metadata') else {}
                })
            
            logger.info(f"list_vectors_by_filter trovati {len(matches)} vettori")
            return matches
            
        except Exception as e:
            logger.error(f"Errore list_vectors_by_filter: {e}")
            return []