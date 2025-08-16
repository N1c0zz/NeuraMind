from typing import List

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> List[str]:
    """
    Divide un testo in chunks con overlap
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Se non siamo alla fine del testo, trova un punto di divisione naturale
        if end < len(text):
            # Cerca l'ultimo spazio o punto per non spezzare le parole
            last_space = text.rfind(' ', start, end)
            last_period = text.rfind('.', start, end)
            last_newline = text.rfind('\n', start, end)
            
            # Usa il punto di divisione più vicino alla fine
            split_point = max(last_space, last_period, last_newline)
            if split_point > start:
                end = split_point
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Prossimo chunk inizia con overlap
        start = end - overlap if end < len(text) else len(text)
    
    return chunks