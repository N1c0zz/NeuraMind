#!/usr/bin/env python3
"""
🔍 Test Debug Query Pinecone
Verifica perché le query non trovano risultati
"""

import requests
import json

RAILWAY_URL = "https://neuramind-production.up.railway.app"
BASE_URL = f"{RAILWAY_URL}/v1"
API_KEY = "super-secret-for-local"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def test_query_debug():
    """Test debug delle query"""
    print("🔍 Debug Query Pinecone")
    print("=" * 40)
    
    # Test 1: Query senza filtro user_id specifico
    print("1. 🔍 Test query generica...")
    
    query_data = {
        "user_id": "test_railway_user",
        "query": "NeuraMind",
        "top_k": 5
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            headers=headers,
            json=query_data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            matches = result.get("matches", [])
            print(f"✅ Query OK - {len(matches)} risultati")
            
            for i, match in enumerate(matches, 1):
                score = match.get("score", 0)
                user_id = match.get("metadata", {}).get("user_id", "N/A")
                item_id = match.get("metadata", {}).get("item_id", "N/A")
                text_preview = match.get("metadata", {}).get("text", "")[:100]
                print(f"   {i}. Score: {score:.3f}")
                print(f"      User: {user_id}")
                print(f"      Item: {item_id}")
                print(f"      Text: {text_preview}...")
                print()
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    test_query_debug()
