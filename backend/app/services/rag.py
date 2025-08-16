from typing import Any
from app.services.openai_client import embed_texts, chat_answer
from app.services.pinecone_client import index

def upsert_chunks(user_id: str, item_id: str, title: str, chunks: list[dict]) -> list[str]:
    vectors = embed_texts([c["text"] for c in chunks])
    ids = []
    for ord_, (vec, ch) in enumerate(zip(vectors, chunks)):
        cid = f"{item_id}_{ord_:04d}"
        index.upsert(
            vectors=[{
                "id": cid,
                "values": vec,
                "metadata": {
                    "user_id": user_id, "item_id": item_id, "title": title,
                    "ord": ord_, "preview": ch["text"][:160]
                }
            }],
            namespace=f"user_{user_id}"
        )
        ids.append(cid)
    return ids

def semantic_search(user_id: str, query: str, top_k: int = 8) -> list[dict]:
    qv = embed_texts([query])[0]
    res = index.query(
        namespace=f"user_{user_id}",
        vector=qv,
        top_k=top_k,
        include_values=False,
        include_metadata=True,
        metric="cosine"
    )
    return [m.dict() if hasattr(m, "dict") else m for m in res.matches]

def answer_from_context(query: str, contexts: list[dict]) -> str:
    ctx = "\n\n".join([f"[{c.get('id')}] {c.get('metadata',{}).get('preview','')}" for c in contexts])
    system = (
        "Sei NeuraMind. Rispondi SOLO usando il CONTEXT. "
        "Se non basta, di' che non hai abbastanza dati. Cita gli id tra []."
    )
    user = f"CONTEXT:\n{ctx}\n\nQUESTION:\n{query}"
    return chat_answer(system, user)
