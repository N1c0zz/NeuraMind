#!/usr/bin/env python3
"""
🧪 Test Essenziale NeuraMind
Test completo del workflow RAG locale
"""

import requests
import json
import time

# Configurazione locale
BASE_URL = "http://127.0.0.1:8000/v1"
API_KEY = "super-secret-for-local"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def test_complete_workflow():
    """Test workflow completo RAG"""
    print("🧠 Test Workflow Completo NeuraMind")
    print("=" * 50)
    
    # 1. Health Check
    print("1. 🏥 Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server non raggiungibile")
            return False
        print("✅ Server OK")
    except Exception as e:
        print(f"❌ Errore connessione: {e}")
        return False
    
    # 2. Upsert Document
    print("\n2. 📝 Test Upsert...")
    doc_data = {
        "user_id": "test_user",
        "item_id": "test_doc_001",
        "title": "Documento Test NeuraMind",
        "text": """
        NeuraMind è un assistente AI personale sviluppato con FastAPI.
        Utilizza OpenAI per gli embeddings e la generazione di risposte.
        Il database vettoriale è gestito da Pinecone per la ricerca semantica.
        Il sistema implementa un pattern RAG (Retrieval-Augmented Generation).
        """
    }
    
    try:
        response = requests.post(f"{BASE_URL}/embed-upsert", headers=headers, json=doc_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upsert OK - {len(result.get('ids', []))} chunks creati")
        else:
            print(f"❌ Upsert failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Errore upsert: {e}")
        return False
    
    # 3. Query
    print("\n3. 🔍 Test Query...")
    query_data = {
        "user_id": "test_user",
        "query": "Come funziona NeuraMind?",
        "top_k": 3
    }
    
    try:
        response = requests.post(f"{BASE_URL}/query", headers=headers, json=query_data, timeout=15)
        if response.status_code == 200:
            result = response.json()
            matches = result.get("matches", [])
            print(f"✅ Query OK - {len(matches)} risultati trovati")
        else:
            print(f"❌ Query failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Errore query: {e}")
        return False
    
    # 4. Answer
    print("\n4. 🤖 Test Answer...")
    answer_data = {
        "query": "Spiegami NeuraMind in dettaglio",
        "contexts": matches[:2]  # Usa primi 2 risultati
    }
    
    try:
        response = requests.post(f"{BASE_URL}/answer", headers=headers, json=answer_data, timeout=20)
        if response.status_code == 200:
            result = response.json()
            answer = result.get("answer", "")
            print("✅ Answer OK")
            print(f"\n🤖 Risposta AI:")
            print("-" * 40)
            print(answer)
            print("-" * 40)
        else:
            print(f"❌ Answer failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Errore answer: {e}")
        return False
    
    print(f"\n🎉 Workflow completo funzionante!")
    return True

def quick_test():
    """Test veloce solo health e debug"""
    print("⚡ Quick Test")
    print("=" * 30)
    
    # Health
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Health: {'✅ OK' if response.status_code == 200 else '❌ FAIL'}")
    except:
        print("Health: ❌ FAIL")
        return
    
    # Debug endpoint (se disponibile)
    try:
        response = requests.get(f"{BASE_URL}/debug", headers=headers, timeout=5)
        if response.status_code == 200:
            debug_info = response.json()
            print(f"Pinecone: {'✅ OK' if debug_info.get('pinecone_connection') == 'OK' else '❌ FAIL'}")
            print(f"OpenAI: {'✅ OK' if debug_info.get('openai_connection') == 'OK' else '❌ FAIL'}")
        else:
            print("Debug: ⚠️ Non disponibile")
    except:
        print("Debug: ❌ FAIL")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_test()
    else:
        test_complete_workflow()
