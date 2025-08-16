from openai import OpenAI
from app.core.config import get_settings

settings = get_settings()
oa = OpenAI(api_key=settings.OPENAI_API_KEY)

def embed_texts(texts: list[str]) -> list[list[float]]:
    # Usa il modello light per costi/latency contenuti (dim=1536)
    resp = oa.embeddings.create(model="text-embedding-3-small", input=texts)
    return [d.embedding for d in resp.data]

def chat_answer(system: str, user: str) -> str:
    resp = oa.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"system","content":system},{"role":"user","content":user}],
        temperature=0.2,
    )
    return resp.choices[0].message.content
