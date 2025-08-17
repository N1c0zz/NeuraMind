#!/usr/bin/env python3
"""
🚀 NeuraMind Railway Tester
Test completo del sistema RAG su Railway con debug dettagliato
"""

import requests
import json
import time
import sys
from typing import Dict, Any

RAILWAY_URL = "https://neuramind-production.up.railway.app"
API_KEY = "super-secret-for-local"

# URLs degli endpoint
BASE_URL = f"{RAILWAY_URL}/v1"
HEALTH_URL = f"{RAILWAY_URL}/health"

headers = {
    "Content-Type": "application/json", 
    "X-API-Key": API_KEY
}

def print_separator(title: str):
    """Stampa un separatore carino"""
    print(f"\n{'='*50}")
    print(f"🔹 {title}")
    print('='*50)

def test_endpoint(name: str, url: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
    """Testa un endpoint con error handling"""
    print(f"\n🔥 Testing {name}...")
    print(f"📡 URL: {url}")
    
    if data:
        print(f"📦 Payload: {json.dumps(data, indent=2)}")
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=60)
        
        elapsed = time.time() - start_time
        
        print(f"⏱️  Tempo: {elapsed:.2f}s")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS!")
            print(f"📄 Response:")
            print(json.dumps(result, indent=2))
            return {"success": True, "data": result, "time": elapsed}
        else:
            print(f"❌ FAILED!")
            print(f"📄 Error: {response.text}")
            return {"success": False, "error": response.text, "status": response.status_code}
            
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT - L'operazione è troppo lenta")
        return {"success": False, "error": "timeout"}
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")
        return {"success": False, "error": str(e)}

def main():
    """Test completo del sistema RAG"""
    
    print("🚀 NeuraMind Railway Test Suite")
    print("🔧 Sistema RAG: OpenAI + Pinecone + FastAPI")
    print(f"🌐 Target: {RAILWAY_URL}")
    
    # Verifica configurazione
    if "IL_TUO_URL" in RAILWAY_URL:
        print("\n❌ ERRORE: Devi aggiornare RAILWAY_URL nel file!")
        print("📝 Apri test_railway.py e metti il tuo URL Railway")
        return
    
    results = {}
    
    # Test 1: Health Check
    print_separator("STEP 1: HEALTH CHECK")
    results["health"] = test_endpoint("Health Check", HEALTH_URL)
    
    if not results["health"]["success"]:
        print("\n💀 Server non raggiungibile! Verifica:")
        print("1. URL Railway corretto")
        print("2. App deployata e running") 
        print("3. Connessione internet")
        return
    
    # Test 2: Upsert (Salvare documento)
    print_separator("STEP 2: UPSERT - Salvataggio Documento")
    print("🎯 Cosa succede: Testo → Chunks → OpenAI Embeddings → Pinecone")
    
    upsert_data = {
        "user_id": "test_railway",
        "item_id": "doc_railway_001", 
        "title": "Test Railway Document",
        "text": """
        NeuraMind è un assistente AI personale deployato su Railway.
        Utilizza FastAPI per l'API REST.
        Integra OpenAI per gli embeddings e la generazione di risposte.
        Usa Pinecone come database vettoriale per la ricerca semantica.
        Il sistema implementa un pattern RAG (Retrieval Augmented Generation).
        """
    }
    
    results["upsert"] = test_endpoint(
        "Embed-Upsert", 
        f"{BASE_URL}/embed-upsert", 
        "POST", 
        upsert_data
    )
    
    if not results["upsert"]["success"]:
        print("\n💀 Upsert fallito! Possibili cause:")
        print("1. Chiavi API OpenAI/Pinecone mancanti")
        print("2. Indice Pinecone non esistente") 
        print("3. Quota OpenAI esaurita")
        return
    
    # Test 3: Query (Ricerca semantica)
    print_separator("STEP 3: QUERY - Ricerca Semantica")
    print("🎯 Cosa succede: Domanda → OpenAI Embedding → Pinecone Search → Risultati")
    
    query_data = {
        "user_id": "test_railway",
        "query": "Cos'è NeuraMind e come funziona?",
        "top_k": 3
    }
    
    results["query"] = test_endpoint(
        "Semantic Search",
        f"{BASE_URL}/query",
        "POST", 
        query_data
    )
    
    if not results["query"]["success"]:
        print("\n💀 Query fallita! Controlla i logs Railway")
        return
    
    # Test 4: Answer (Generazione risposta AI)
    print_separator("STEP 4: ANSWER - Generazione Risposta AI")
    print("🎯 Cosa succede: Domanda + Contesti → OpenAI GPT → Risposta finale")
    
    matches = results["query"]["data"].get("matches", [])
    
    answer_data = {
        "query": "Spiegami dettagliatamente NeuraMind",
        "contexts": matches
    }
    
    results["answer"] = test_endpoint(
        "AI Answer Generation", 
        f"{BASE_URL}/answer",
        "POST",
        answer_data
    )
    
    # Riepilogo finale
    print_separator("RISULTATI FINALI")
    
    for step, result in results.items():
        status = "✅ OK" if result["success"] else "❌ FAIL"
        time_info = f" ({result.get('time', 0):.2f}s)" if result.get("time") else ""
        print(f"{status} {step.upper()}{time_info}")
    
    if all(r["success"] for r in results.values()):
        print(f"\n🎉 SUCCESSO TOTALE! NeuraMind RAG funziona su Railway!")
        print(f"\n📊 Performance:")
        total_time = sum(r.get("time", 0) for r in results.values())
        print(f"⏱️  Tempo totale: {total_time:.2f}s")
        
        # Mostra la risposta finale
        if "answer" in results and results["answer"]["success"]:
            answer_text = results["answer"]["data"].get("answer", "")
            print(f"\n🤖 Risposta finale di NeuraMind:")
            print("-" * 60)
            print(answer_text)
            print("-" * 60)
    else:
        print(f"\n❌ Alcuni test sono falliti. Controlla i logs Railway.")

def quick_test():
    """Test veloce solo health check"""
    print("⚡ Quick Health Check")
    result = test_endpoint("Health", HEALTH_URL)
    if result["success"]:
        print("✅ Railway deployment is UP!")
    else:
        print("❌ Railway deployment has issues")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_test()
    else:
        main()
