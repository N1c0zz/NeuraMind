import requests
import json

# URL base del tuo server
BASE_URL = "http://localhost:8000/v1"
API_KEY = "super-secret-for-local"  # Deve corrispondere a DEV_API_KEY nel .env

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def test_health():
    """Test basic health check"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code} - {response.json()}")
    return response.status_code == 200

def test_embed_upsert():
    """Test embedding and upserting text"""
    data = {
        "user_id": "user123",
        "item_id": "doc001", 
        "title": "Test Document",
        "text": """
        NeuraMind è un assistente AI personale che conosce i tuoi documenti.
        Può aiutarti a trovare informazioni rapidamente e rispondere alle tue domande.
        Il sistema utilizza embeddings vettoriali per la ricerca semantica.
        L'architettura è basata su FastAPI, OpenAI e Pinecone.
        """
    }
    
    response = requests.post(f"{BASE_URL}/embed-upsert", 
                           headers=headers, 
                           json=data)
    print(f"Embed upsert: {response.status_code} - {response.json()}")
    return response.status_code == 200

def test_query():
    """Test semantic search"""
    data = {
        "user_id": "user123",
        "query": "Come funziona la ricerca semantica?",
        "top_k": 3
    }
    
    response = requests.post(f"{BASE_URL}/query",
                           headers=headers,
                           json=data)
    result = response.json()
    print(f"Query: {response.status_code}")
    print(f"Found {len(result.get('matches', []))} matches")
    return response.status_code == 200, result

def test_answer():
    """Test answer generation"""
    # Prima facciamo una query per ottenere i contesti
    success, query_result = test_query()
    if not success:
        print("Query failed, cannot test answer")
        return False
    
    data = {
        "query": "Come funziona la ricerca semantica in NeuraMind?",
        "contexts": query_result.get("matches", [])
    }
    
    response = requests.post(f"{BASE_URL}/answer",
                           headers=headers,
                           json=data)
    result = response.json()
    print(f"Answer: {response.status_code}")
    print(f"Generated answer: {result.get('answer', 'No answer')}")
    return response.status_code == 200

def main():
    """Run all tests"""
    print("🧪 Testing NeuraMind Backend...")
    print("="*50)
    
    # Test sequence
    print("1. Testing health endpoint...")
    test_health()
    print()
    
    print("2. Testing embed-upsert...")
    test_embed_upsert()
    print()
    
    print("3. Testing query...")
    test_query()
    print()
    
    print("4. Testing answer generation...")
    test_answer()
    print()
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    main()
