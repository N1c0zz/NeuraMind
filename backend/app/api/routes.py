from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import check_api_key
from app.schemas import UpsertIn, UpsertOut, QueryIn, QueryOut, AnswerIn, AnswerOut
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
def health():
    return {"ok": True}

@router.post("/embed-upsert", response_model=UpsertOut, dependencies=[Depends(check_api_key)])
def embed_upsert(body: UpsertIn):
    try:
        # Implementazione temporanea semplice
        # Dividi il testo in chunks semplici
        text = body.text
        chunk_size = 1000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        # Per ora restituiamo solo gli ID dei chunks
        chunk_ids = [f"{body.item_id}_{i:04d}" for i in range(len(chunks))]
        
        return UpsertOut(ok=True, ids=chunk_ids)
        
    except Exception as e:
        logger.error(f"Errore embed_upsert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=QueryOut, dependencies=[Depends(check_api_key)])
def query(body: QueryIn):
    try:
        # Implementazione temporanea - restituisce match fittizi
        matches = [
            {
                "id": "doc_001_0000",
                "score": 0.95,
                "metadata": {
                    "user_id": body.user_id,
                    "item_id": "doc_001",
                    "title": "Test Document",
                    "preview": "Questo è un documento di test..."
                }
            }
        ]
        
        return QueryOut(matches=matches)
        
    except Exception as e:
        logger.error(f"Errore query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/answer", response_model=AnswerOut, dependencies=[Depends(check_api_key)])
def answer(body: AnswerIn):
    try:
        # Implementazione temporanea - risposta fissa
        answer_text = f"Basandomi sui documenti forniti, ecco la risposta alla tua domanda: '{body.query}'. Al momento sto usando una risposta di test."
        
        return AnswerOut(answer=answer_text)
        
    except Exception as e:
        logger.error(f"Errore answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))