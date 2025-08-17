from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.api.deps import check_api_key
from app.schemas import (
    UpsertIn, UpsertOut, QueryIn, QueryOut, AnswerIn, AnswerOut,
    DocumentUploadOut, DocumentUploadError, DocumentListOut, DocumentInfo
)
from app.services.chunking import chunk_text
from app.services.rag import upsert_chunks, semantic_search, answer_from_context
from app.services.ocr_service import ocr_service
from app.services.document_service import document_service
import logging
import time
import uuid
from datetime import datetime

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
            "pinecone_api_key_preview": settings.pinecone_api_key[:15] + "..." + settings.pinecone_api_key[-5:] if settings.pinecone_api_key else "None",
            "openai_api_key_set": bool(settings.openai_api_key),
            "openai_api_key_preview": settings.openai_api_key[:15] + "..." + settings.openai_api_key[-5:] if settings.openai_api_key else "None",
            "pinecone_index_name": settings.pinecone_index_name,
            "pinecone_region": settings.pinecone_region,
            "pinecone_cloud": settings.pinecone_cloud,
        }
        
        # Prova a connettersi a Pinecone e lista indici
        try:
            from app.services.pinecone_client import PineconeService
            pinecone_service = PineconeService()
            debug_data["pinecone_connection"] = "OK"
            
            # Lista indici con API 3.x
            available_indexes = [idx.name for idx in pinecone_service.pc.list_indexes()]
            debug_data["available_indexes"] = available_indexes
                
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


# ========================
# NUOVI ENDPOINT OCR
# ========================

@router.post("/upload-document", dependencies=[Depends(check_api_key)])
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(""),
    user_id: str = Form(...),
    language: str = Form("ita+eng")
):
    """
    Upload documento immagine → OCR → RAG
    Con limite di 10 documenti per utente
    """
    start_time = time.time()
    
    try:
        # 0. Controllo limite documenti
        if not document_service.can_upload_document(user_id):
            current_count = document_service.count_user_documents(user_id)
            
            if current_count >= document_service.max_documents:
                # Elimina il documento più vecchio
                if document_service.delete_oldest_document(user_id):
                    logger.info(f"Eliminato documento più vecchio per {user_id} (limite {document_service.max_documents})")
                else:
                    return DocumentUploadError(
                        error=f"Limite di {document_service.max_documents} documenti raggiunto e impossibile eliminare documenti vecchi",
                        error_code="LIMIT_EXCEEDED"
                    )
        
        # 1. Validazione file
        logger.info(f"File ricevuto: {file.filename}, tipo: {file.content_type}")
        
        # Accetta anche PDF (li tratteremo come immagini per ora)
        supported_types = {
            'image/jpeg', 'image/jpg', 'image/png', 
            'image/bmp', 'image/tiff', 'image/webp',
            'application/pdf'  # Accetta PDF
        }
        
        if not file.content_type or file.content_type not in supported_types:
            return DocumentUploadError(
                error=f"Formato file non supportato: {file.content_type}",
                error_code="UNSUPPORTED_FORMAT",
                details={"content_type": file.content_type, "supported": list(supported_types)}
            )
        
        # 2. Leggi contenuto file
        file_content = await file.read()
        if len(file_content) == 0:
            return DocumentUploadError(
                error="File vuoto",
                error_code="EMPTY_FILE"
            )
        
        # Limite dimensione (20MB)
        max_size = 20 * 1024 * 1024  # 20MB
        if len(file_content) > max_size:
            return DocumentUploadError(
                error=f"File troppo grande. Max: {max_size/1024/1024:.1f}MB",
                error_code="FILE_TOO_LARGE",
                details={"size_mb": len(file_content)/1024/1024}
            )
        
        logger.info(f"File ricevuto: {file.filename}, {len(file_content)} bytes, tipo: {file.content_type}")
        
        # 3. OCR o testo simulato per PDF
        if file.content_type == 'application/pdf':
            # Per ora simula estrazione testo PDF
            extracted_text = f"""AUTOCERTIFICAZIONE ESAMI UNIVERSITARI

Nome Studente: {user_id}
Corso di Laurea: Informatica

ESAMI SOSTENUTI:
- Algoritmi e Strutture Dati: 28/30 (15/06/2023)
- Programmazione Web: 30/30 (20/09/2023) 
- Database: 27/30 (10/01/2024)
- Intelligenza Artificiale: 30L/30 (15/03/2024)
- Sistemi Operativi: 26/30 (05/05/2024)
- Reti di Calcolatori: 29/30 (18/06/2024)

Media voti: 28.3/30
Crediti acquisiti: 180 CFU

Data certificazione: 17 Agosto 2025
Firma: [Firma digitale]"""
            
            ocr_metadata = {
                'method': 'pdf_mock',
                'original_size': (800, 600),
                'language': language,
                'text_length': len(extracted_text),
                'confidence': 0.95,
                'note': 'Testo simulato per PDF - Implementazione OCR PDF in sviluppo'
            }
            
            logger.info("PDF caricato: usando testo simulato per demo")
            
        else:
            # OCR per immagini
            try:
                extracted_text, ocr_metadata = ocr_service.extract_text_with_fallback(
                    file_content, language
                )
            except Exception as e:
                logger.error(f"Errore OCR: {e}")
                return DocumentUploadError(
                    error=f"Impossibile estrarre testo: {str(e)}",
                    error_code="OCR_FAILED",
                    details={"language": language}
                )
        
        # Verifica che sia stato estratto del testo
        if not extracted_text or len(extracted_text.strip()) < 5:
            return DocumentUploadError(
                error="Nessun testo significativo trovato nel file",
                error_code="NO_TEXT_FOUND",
                details={"extracted_length": len(extracted_text), "confidence": ocr_metadata.get("confidence", 0)}
            )
        
        logger.info(f"Testo estratto: {len(extracted_text)} caratteri, confidenza: {ocr_metadata.get('confidence', 0):.2f}")
        
        # 4. Salva nel RAG
        item_id = f"doc_{user_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        document_title = title or file.filename or f"Documento {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        try:
            # Chunking
            chunks = chunk_text(extracted_text, chunk_size=1000, overlap=150)
            logger.info(f"Creati {len(chunks)} chunks per {item_id}")
            
            # Upsert nel RAG
            chunk_ids = upsert_chunks(
                user_id=user_id,
                item_id=item_id,
                title=document_title,
                chunks=chunks
            )
            
            logger.info(f"Documento salvato con {len(chunk_ids)} chunks")
            
        except Exception as e:
            logger.error(f"Errore salvataggio RAG: {e}")
            return DocumentUploadError(
                error=f"Errore salvataggio documento: {str(e)}",
                error_code="RAG_SAVE_FAILED"
            )
        
        # 5. Risposta successo
        processing_time = time.time() - start_time
        
        return DocumentUploadOut(
            success=True,
            item_id=item_id,
            title=document_title,
            text_preview=extracted_text[:200] + ("..." if len(extracted_text) > 200 else ""),
            chunks_created=len(chunk_ids),
            ocr_metadata=ocr_metadata,
            processing_time=round(processing_time, 2)
        )
        
    except Exception as e:
        logger.error(f"Errore upload documento: {e}")
        return DocumentUploadError(
            error=f"Errore interno: {str(e)}",
            error_code="INTERNAL_ERROR"
        )


@router.get("/documents/{user_id}", response_model=DocumentListOut, dependencies=[Depends(check_api_key)])
def list_user_documents(user_id: str):
    """
    Lista documenti di un utente
    """
    try:
        logger.info(f"Richiesta lista documenti per {user_id}")
        
        # Recupera documenti dal servizio
        documents = document_service.get_user_documents(user_id)
        
        # Converti in oggetti DocumentInfo
        document_infos = []
        for doc in documents:
            doc_info = DocumentInfo(
                item_id=doc['item_id'],
                title=doc['title'],
                created_at=doc['created_at'],
                upload_date=doc['upload_date'],
                text_length=doc['text_length'],
                chunks_count=doc['chunks_count'],
                ocr_confidence=doc.get('ocr_confidence'),
                text_preview=doc['text_preview'],
                file_type=doc['file_type'],
                user_id=doc['user_id']
            )
            document_infos.append(doc_info)
        
        return DocumentListOut(
            user_id=user_id,
            documents=document_infos,
            total_count=len(document_infos),
            max_documents=document_service.max_documents
        )
        
    except Exception as e:
        logger.error(f"Errore lista documenti per {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{user_id}/{item_id}", dependencies=[Depends(check_api_key)])
def delete_user_document(user_id: str, item_id: str):
    """
    Elimina un documento specifico
    """
    try:
        logger.info(f"Richiesta eliminazione documento {item_id} per {user_id}")
        
        success = document_service.delete_document(user_id, item_id)
        
        if success:
            return {"success": True, "message": "Documento eliminato con successo"}
        else:
            raise HTTPException(status_code=404, detail="Documento non trovato")
        
    except Exception as e:
        logger.error(f"Errore eliminazione documento {item_id} per {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{item_id}", dependencies=[Depends(check_api_key)])
async def delete_document(item_id: str, user_id: str):
    """Elimina documento"""
    try:
        # TODO: Implementare eliminazione da Pinecone
        return {"success": True, "message": f"Documento {item_id} eliminato"}
        
    except Exception as e:
        logger.error(f"Errore eliminazione documento: {e}")
        raise HTTPException(status_code=500, detail=str(e))