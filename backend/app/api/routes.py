from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import check_api_key
from app.schemas import UpsertIn, UpsertOut, QueryIn, QueryOut, AnswerIn, AnswerOut
from app.services.chunking import chunk_text
from app.services.rag import upsert_chunks, semantic_search, answer_from_context
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
def health():
    return {"ok": True}

@router.get("/debug", dependencies=[Depends(check_api_key)])
def debug_info():
    """Endpoint di debug per vedere configurazione Railway"""
    try:
        from app.core.config import settings
        
        debug_data = {
            "pinecone_api_key_set": bool(settings.pinecone_api_key),
            "openai_api_key_set": bool(settings.openai_api_key),
            "pinecone_index_name": settings.pinecone_index_name,
            "pinecone_region": settings.pinecone_region,
            "pinecone_cloud": settings.pinecone_cloud,
        }
        
        # Prova a connettersi a Pinecone e lista indici
        try:
            from app.services.pinecone_client import PineconeService
            pinecone_service = PineconeService()
            debug_data["pinecone_connection"] = "OK"
            
            # Lista indici disponibili
            if hasattr(pinecone_service, 'pc'):
                if pinecone_service.use_new_api:
                    available_indexes = [idx.name for idx in pinecone_service.pc.list_indexes()]
                else:
                    available_indexes = pinecone_service.pc.list_indexes()
                debug_data["available_indexes"] = available_indexes
            else:
                debug_data["available_indexes"] = "Unable to list"
                
        except Exception as e:
            debug_data["pinecone_connection"] = f"FAILED: {str(e)}"
            debug_data["available_indexes"] = []
        
        # Test OpenAI
        try:
            from app.services.openai_client import OpenAIService
            openai_service = OpenAIService()
            test_embedding = openai_service.create_embedding("test")
            debug_data["openai_connection"] = "OK"
            debug_data["embedding_size"] = len(test_embedding)
        except Exception as e:
            debug_data["openai_connection"] = f"FAILED: {str(e)}"
        
        return debug_data
        
    except Exception as e:
        logger.error(f"Errore debug: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/embed-upsert", response_model=UpsertOut, dependencies=[Depends(check_api_key)])
def embed_upsert(body: UpsertIn):
    try:
        # Chunking del testo
        chunks = chunk_text(body.text, chunk_size=1000, overlap=150)
        logger.info(f"Creati {len(chunks)} chunks per {body.item_id}")
        
        # Upsert reale con OpenAI + Pinecone
        chunk_ids = upsert_chunks(
            user_id=body.user_id,
            item_id=body.item_id, 
            title=body.title,
            chunks=chunks
        )
        
        return UpsertOut(ok=True, ids=chunk_ids)
        
    except Exception as e:
        logger.error(f"Errore embed_upsert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=QueryOut, dependencies=[Depends(check_api_key)])
def query(body: QueryIn):
    try:
        # Ricerca semantica reale
        matches = semantic_search(
            user_id=body.user_id,
            query=body.query,
            top_k=body.top_k
        )
        
        return QueryOut(matches=matches)
        
    except Exception as e:
        logger.error(f"Errore query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/answer", response_model=AnswerOut, dependencies=[Depends(check_api_key)])
def answer(body: AnswerIn):
    try:
        # Generazione risposta reale con GPT
        answer_text = answer_from_context(
            query=body.query,
            contexts=body.contexts
        )
        
        return AnswerOut(answer=answer_text)
        
    except Exception as e:
        logger.error(f"Errore answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))