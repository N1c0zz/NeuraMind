import requests
import json
import time
import os
from dotenv import load_dotenv

# Carica configurazione
load_dotenv('../.env')

BASE_URL = "http://127.0.0.1:8000/v1"
API_KEY = os.getenv('DEV_API_KEY', 'super-secret-for-local')

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def test_step_by_step():
    """Test del workflow RAG step-by-step con controlli di sicurezza"""
    
    print("🧪 NeuraMind - Workflow Demo Leggero")
    print("=" * 50)
    
    # Step 0: Verifica connessione
    print("📡 Step 0: Verifica connessione server...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server non raggiungibile")
            return
        print("✅ Server OK")
    except Exception as e:
        print(f"❌ Errore connessione: {e}")
        return
    
    print("\n" + "="*50)
    print("🔄 WORKFLOW RAG - Step by Step")
    print("="*50)
    
    # Step 1: Upsert (molto leggero)
    print("\n📝 Step 1: UPSERT - Salvataggio documento...")
    print("Cosa fa: Converte il testo in embeddings e lo salva in Pinecone")
    
    # Testo molto piccolo per ridurre carico
    document_text = """
    NeuraMind è un assistente AI personale.
    Aiuta a gestire documenti e note.
    Utilizza la ricerca semantica.
    """
    
    upsert_data = {
        "user_id": "demo_user",
        "item_id": "demo_doc_001", 
        "title": "Demo Document",
        "text": document_text.strip()
    }
    
    print(f"📄 Documento da salvare: {len(document_text)} caratteri")
    print("⏳ Invio richiesta a OpenAI per embeddings...")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/embed-upsert", 
            headers=headers, 
            json=upsert_data,
            timeout=30  # Timeout più lungo
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upsert completato in {elapsed:.2f}s")
            print(f"📊 Chunks creati: {len(result.get('ids', []))}")
            print(f"🆔 IDs: {result.get('ids', [])}")
        else:
            print(f"❌ Upsert fallito: {response.status_code}")
            print(f"Errore: {response.text}")
            return
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - L'operazione è troppo lenta per questo PC")
        print("💡 Prova con un testo più corto o controlla la connessione internet")
        return
    except Exception as e:
        print(f"❌ Errore durante upsert: {e}")
        return
    
    # Step 2: Query (più veloce)
    print(f"\n🔍 Step 2: QUERY - Ricerca semantica...")
    print("Cosa fa: Cerca documenti simili alla domanda")
    
    query_data = {
        "user_id": "demo_user",
        "query": "Cos'è NeuraMind?",
        "top_k": 3
    }
    
    print(f"❓ Domanda: {query_data['query']}")
    print("⏳ Ricerca in corso...")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/query",
            headers=headers,
            json=query_data,
            timeout=15
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            matches = result.get("matches", [])
            print(f"✅ Query completata in {elapsed:.2f}s")
            print(f"📊 Risultati trovati: {len(matches)}")
            
            for i, match in enumerate(matches):
                score = match.get('score', 0)
                preview = match.get('metadata', {}).get('preview', 'N/A')
                print(f"  {i+1}. Score: {score:.3f} - {preview[:50]}...")
                
        else:
            print(f"❌ Query fallita: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Errore durante query: {e}")
        return
    
    # Step 3: Answer (dipende da OpenAI)
    print(f"\n💬 Step 3: ANSWER - Generazione risposta AI...")
    print("Cosa fa: GPT genera una risposta basata sui documenti trovati")
    
    answer_data = {
        "query": query_data["query"],
        "contexts": matches[:2]  # Usa solo i primi 2 risultati
    }
    
    print("⏳ GPT sta pensando...")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/answer",
            headers=headers,
            json=answer_data,
            timeout=20
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("answer", "")
            print(f"✅ Risposta generata in {elapsed:.2f}s")
            print(f"\n🤖 Risposta di NeuraMind:")
            print("-" * 40)
            print(answer)
            print("-" * 40)
        else:
            print(f"❌ Answer fallito: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Errore durante answer: {e}")
    
    print(f"\n🎉 Workflow RAG completato!")
    print("\n📚 Riepilogo del processo:")
    print("1. 📝 UPSERT: Documento → Embeddings → Pinecone")
    print("2. 🔍 QUERY: Domanda → Ricerca vettoriale → Risultati")
    print("3. 💬 ANSWER: Risultati + Domanda → GPT → Risposta finale")

if __name__ == "__main__":
    test_step_by_step()
