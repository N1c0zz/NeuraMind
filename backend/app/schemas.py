from pydantic import BaseModel, Field
from typing import Any, List, Dict

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
