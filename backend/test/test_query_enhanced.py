#!/usr/bin/env python3
"""
Test query enhancement per migliorare le risposte
"""

import requests

def test_enhanced_queries():
    """Test query con strategie diverse"""
    
    RAILWAY_URL = "https://neuramind-production.up.railway.app/v1"
    API_KEY = "super-secret-for-local"
    USER_ID = "nicom_test"
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Query problematiche e versioni migliorate
    query_pairs = [
        {
            "originale": "quali sono gli esami con il voto piu alto?",
            "migliorata": "elenca tutti gli esami con i relativi voti, dal più alto al più basso"
        },
        {
            "originale": "quanti crediti ho acquisito?",
            "migliorata": "quanti CFU o crediti formativi universitari totali sono indicati nel documento?"
        },
        {
            "originale": "qual è la mia media?",
            "migliorata": "calcola la media dei voti di tutti gli esami elencati nel documento"
        }
    ]
    
    for pair in query_pairs:
        print(f"\n🔍 CONFRONTO QUERY:")
        print(f"   📝 Originale: {pair['originale']}")
        print(f"   ✨ Migliorata: {pair['migliorata']}")
        print("   " + "="*50)
        
        for query_type, query in pair.items():
            print(f"\n   🤔 {query_type.upper()}: {query}")
            
            try:
                # 1. Search
                search_response = requests.post(
                    f"{RAILWAY_URL}/query",
                    headers=headers,
                    json={
                        "user_id": USER_ID,
                        "query": query,
                        "top_k": 5  # Più contesti
                    },
                    timeout=15
                )
                
                if search_response.status_code == 200:
                    contexts = search_response.json()["matches"]
                    print(f"      📚 Contesti: {len(contexts)}")
                    if contexts:
                        print(f"      🎯 Score: {contexts[0].get('score', 0):.3f}")
                    
                    # 2. Answer
                    answer_response = requests.post(
                        f"{RAILWAY_URL}/answer",
                        headers=headers,
                        json={
                            "query": query,
                            "contexts": contexts
                        },
                        timeout=20
                    )
                    
                    if answer_response.status_code == 200:
                        answer = answer_response.json()["answer"]
                        print(f"      🤖 Risposta: {answer}")
                    else:
                        print(f"      ❌ Answer failed: {answer_response.status_code}")
                        
                else:
                    print(f"      ❌ Search failed: {search_response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ Errore: {e}")

def test_specific_queries():
    """Test query specifiche per il documento esami"""
    
    RAILWAY_URL = "https://neuramind-production.up.railway.app/v1"
    API_KEY = "super-secret-for-local"
    USER_ID = "nicom_test"
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Query più specifiche e dettagliate
    specific_queries = [
        "Estrai tutti i nomi degli esami e i voti corrispondenti dal documento",
        "Trova tutte le date degli esami nel formato gg/mm/aaaa",
        "Identifica il voto numerico più alto tra tutti gli esami",
        "Cerca informazioni sui crediti formativi o CFU nel documento",
        "Elenca tutti i numeri che potrebbero essere voti di esami (da 18 a 30)",
        "Trova il nome completo dello studente e la matricola",
        "Identifica il corso di laurea o di studi"
    ]
    
    print(f"\n🎯 TEST QUERY SPECIFICHE")
    print("="*60)
    
    for i, query in enumerate(specific_queries, 1):
        print(f"\n{i}. 🤔 {query}")
        
        try:
            # Search con top_k più alto
            search_response = requests.post(
                f"{RAILWAY_URL}/query",
                headers=headers,
                json={
                    "user_id": USER_ID,
                    "query": query,
                    "top_k": 3
                },
                timeout=15
            )
            
            if search_response.status_code == 200:
                contexts = search_response.json()["matches"]
                
                if contexts:
                    # Answer
                    answer_response = requests.post(
                        f"{RAILWAY_URL}/answer",
                        headers=headers,
                        json={
                            "query": query,
                            "contexts": contexts
                        },
                        timeout=20
                    )
                    
                    if answer_response.status_code == 200:
                        answer = answer_response.json()["answer"]
                        print(f"   ✅ {answer}")
                    else:
                        print(f"   ❌ Answer error: {answer_response.status_code}")
                else:
                    print(f"   ❌ Nessun contesto trovato")
                    
        except Exception as e:
            print(f"   ❌ Errore: {e}")

if __name__ == "__main__":
    print("🧪 TEST QUERY ENHANCEMENT")
    
    choice = input("\n1. Confronto query (1)\n2. Query specifiche (2)\n3. Entrambi (3)\nScelta: ").strip()
    
    if choice in ['1', '3']:
        test_enhanced_queries()
    
    if choice in ['2', '3']:
        test_specific_queries()
