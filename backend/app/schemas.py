from pydantic import BaseModel, Field
from typing import Any, List, Dict, Optional

class UpsertIn(BaseModel):
    user_id: str
    item_id: str
    title: str
    text: str

class UpsertOut(BaseModel):
    ok: bool
    ids: List[str]

class QueryIn(BaseModel):
    user_id: str
    query: str
    top_k: int = 8

class QueryOut(BaseModel):
    matches: List[Dict[str, Any]]

class AnswerIn(BaseModel):
    query: str
    contexts: List[Dict[str, Any]]

class AnswerOut(BaseModel):
    answer: str

# ========================
# NUOVI SCHEMAS per OCR
# ========================

class DocumentUploadOut(BaseModel):
    """Response per upload documento"""
    success: bool
    item_id: str
    title: str
    text_preview: str = Field(..., description="Prime 200 caratteri del testo estratto")
    chunks_created: int = Field(..., description="Numero di chunk creati")
    ocr_metadata: Dict[str, Any] = Field(..., description="Metadata OCR (confidenza, dimensioni, etc.)")
    processing_time: float = Field(..., description="Tempo di elaborazione in secondi")

class DocumentUploadError(BaseModel):
    """Response per errori upload"""
    success: bool = False
    error: str
    error_code: str
    details: Optional[Dict[str, Any]] = None

class DocumentListOut(BaseModel):
    """Lista documenti utente"""
    user_id: str
    documents: List[Dict[str, Any]]
    total_count: int

class DocumentInfo(BaseModel):
    """Info singolo documento"""
    item_id: str
    title: str
    created_at: str
    text_length: int
    chunks_count: int
    ocr_confidence: Optional[float] = None
