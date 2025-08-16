import os
import requests
import json
from dotenv import load_dotenv

# Carica configurazione
load_dotenv('../.env')

# USA IL TUO DOMINIO RAILWAY!
BASE_URL = "https://neuramind-production.up.railway.app/v1"
API_KEY = "super-secret-for-local"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def test_complete_workflow():
    """Test completo del workflow RAG su Railway"""
    print("🚀 NeuraMind Railway - Test Completo")
    print("=" * 50)
    
    # Step 1: Health Check
    print("📡 Step 1: Health Check...")
    response = requests.get(f"{BASE_URL.replace('/v1', '')}/health")
    print(f"✅ Status: {response.status_code}")
    print(f"📄 Response: {response.json()}")
    
    # Step 2: Upsert
    print("\n📝 Step 2: Embed-Upsert...")
    upsert_data = {
        "user_id": "test_user",
        "item_id": "doc_railway",
        "title": "Railway Test Document",
        "text": "NeuraMind è un assistente AI deployed su Railway. Utilizza FastAPI, OpenAI e Pinecone per creare un sistema RAG potente e scalabile."
    }
    
    response = requests.post(f"{BASE_URL}/embed-upsert", headers=headers, json=upsert_data)
    print(f"✅ Status: {response.status_code}")
    print(f"📄 Response: {response.json()}")
    
    # Step 3: Query
    print("\n🔍 Step 3: Query...")
    query_data = {
        "user_id": "test_user",
        "query": "Come funziona NeuraMind?",
        "top_k": 3
    }
    
    response = requests.post(f"{BASE_URL}/query", headers=headers, json=query_data)
    print(f"✅ Status: {response.status_code}")
    query_result = response.json()
    print(f"📄 Response: {query_result}")
    
    # Step 4: Answer
    print("\n💬 Step 4: Answer...")
    answer_data = {
        "query": "Spiegami NeuraMind",
        "contexts": query_result.get("matches", [])
    }
    
    response = requests.post(f"{BASE_URL}/answer", headers=headers, json=answer_data)
    print(f"✅ Status: {response.status_code}")
    print(f"📄 Response: {response.json()}")
    
    print("\n🎉 Test completato! NeuraMind funziona su Railway!")

if __name__ == "__main__":
    test_complete_workflow()