import logging
from typing import List, Dict, Any
from app.core.config import settings
from app.services.openai_service import OpenAIService
from app.services.pinecone_client import PineconeService

logger = logging.getLogger(__name__)

def upsert_chunks(user_id: str, item_id: str, title: str, chunks: List[str]) -> List[str]:
    """
    Crea embeddings per i chunks e li salva in Pinecone
    """
    try:
        openai_service = OpenAIService()
        pinecone_service = PineconeService()
        
        vectors = []
        chunk_ids = []
        
        for i, chunk in enumerate(chunks):
            # Crea ID univoco per il chunk
            chunk_id = f"{item_id}_{i:04d}"
            chunk_ids.append(chunk_id)
            
            # Crea embedding
            embedding = openai_service.create_embedding(chunk)
            
            # Prepara vettore per Pinecone
            vector = {
                "id": chunk_id,
                "values": embedding,
                "metadata": {
                    "user_id": user_id,
                    "item_id": item_id,
                    "title": title,
                    "chunk_index": i,
                    "text": chunk,
                    "preview": chunk[:200] + "..." if len(chunk) > 200 else chunk
                }
            }
            vectors.append(vector)
        
        # Upsert in Pinecone
        success = pinecone_service.upsert_vectors(vectors)
        
        if success:
            logger.info(f"Upsert completato per {len(chunks)} chunks")
            return chunk_ids
        else:
            raise Exception("Errore durante upsert in Pinecone")
            
    except Exception as e:
        logger.error(f"Errore upsert_chunks: {e}")
        raise

def semantic_search(user_id: str, query: str, top_k: int = 5) -> List[Dict]:
    """
    Cerca chunks simili alla query
    """
    try:
        openai_service = OpenAIService()
        pinecone_service = PineconeService()
        
        # Crea embedding della query
        query_embedding = openai_service.create_embedding(query)
        
        # Cerca in Pinecone
        filter_dict = {"user_id": user_id}
        matches = pinecone_service.query_vectors(
            query_vector=query_embedding,
            top_k=top_k,
            filter_dict=filter_dict
        )
        
        logger.info(f"Trovati {len(matches)} matches per la query")
        return matches
        
    except Exception as e:
        logger.error(f"Errore semantic_search: {e}")
        raise

def answer_from_context(query: str, contexts: List[Dict]) -> str:
    """
    Genera una risposta basata sui contesti trovati
    """
    try:
        openai_service = OpenAIService()
        
        # Prepara il contesto
        context_text = "\n\n".join([
            f"Documento: {ctx.get('metadata', {}).get('title', 'Senza titolo')}\n{ctx.get('metadata', {}).get('text', '')}"
            for ctx in contexts
        ])
        
        # Genera risposta
        answer = openai_service.generate_answer(query, context_text)
        
        logger.info("Risposta generata con successo")
        return answer
        
    except Exception as e:
        logger.error(f"Errore answer_from_context: {e}")
        raise