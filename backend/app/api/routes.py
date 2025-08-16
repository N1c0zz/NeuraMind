from fastapi import APIRouter, Depends
from app.api.deps import check_api_key
from app.schemas import UpsertIn, UpsertOut, QueryIn, QueryOut, AnswerIn, AnswerOut
from app.services.chunking import chunk_text
from app.services.rag import upsert_chunks, semantic_search, answer_from_context

router = APIRouter()

@router.get("/health")
def health():
    return {"ok": True}

@router.post("/embed-upsert", response_model=UpsertOut, dependencies=[Depends(check_api_key)])
def embed_upsert(body: UpsertIn):
    chunks = chunk_text(body.text)
    ids = upsert_chunks(body.user_id, body.item_id, body.title, chunks)
    return {"ok": True, "ids": ids}

@router.post("/query", response_model=QueryOut, dependencies=[Depends(check_api_key)])
def query(body: QueryIn):
    matches = semantic_search(body.user_id, body.query, body.top_k)
    return {"matches": matches}

@router.post("/answer", response_model=AnswerOut, dependencies=[Depends(check_api_key)])
def answer(body: AnswerIn):
    ans = answer_from_context(body.query, body.contexts)
    return {"answer": ans}
