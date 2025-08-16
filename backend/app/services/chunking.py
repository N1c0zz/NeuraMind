from hashlib import sha256

def chunk_text(text: str, max_chars: int = 1000, overlap: int = 150) -> list[dict]:
    text = " ".join(text.split())
    chunks, i = [], 0
    while i < len(text):
        end = min(i + max_chars, len(text))
        chunk = text[i:end]
        chunks.append({"text": chunk, "hash": sha256(chunk.encode()).hexdigest()})
        i = end - overlap
        if i < 0: i = 0
        if i >= len(text): break
    return chunks
