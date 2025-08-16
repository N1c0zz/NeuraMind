import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.openai_client import embed_texts
from app.services.chunking import chunk_text

def test_embedding_creation():
    """Test basic embedding creation"""
    print("🧪 Testing embedding creation...")
    
    # Test text
    text = "Questo è un test per verificare che gli embeddings funzionino correttamente."
    
    try:
        # Test chunking
        chunks = chunk_text(text, max_chars=50, overlap=10)
        print(f"✅ Created {len(chunks)} chunks")
        for i, chunk in enumerate(chunks):
            print(f"  Chunk {i}: {chunk['text'][:30]}...")
        
        # Test embedding
        texts = [chunk['text'] for chunk in chunks]
        embeddings = embed_texts(texts)
        print(f"✅ Created {len(embeddings)} embeddings")
        print(f"✅ First embedding dimension: {len(embeddings[0])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_embedding_creation()