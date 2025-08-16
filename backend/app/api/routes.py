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