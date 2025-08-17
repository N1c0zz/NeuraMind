#!/usr/bin/env python3
"""
Test specifico per calcoli matematici dopo fix
"""

import requests
import time

def test_math_queries():
    """Test query matematiche con prompt migliorato"""
    
    RAILWAY_URL = "https://neuramind-production.up.railway.app/v1"
    API_KEY = "super-secret-for-local"
    USER_ID = "nicom_test"
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Query matematiche specifiche
    math_queries = [
        "Calcola la media di tutti i voti numerici degli esami",
        "Quanti esami hanno un voto superiore a 25?",
        "Qual è la differenza tra il voto più alto e più basso?",
        "Quanti esami ho superato in totale?",
        "Elenca gli esami con voto inferiore a 20",
        "Calcola la media ponderata se ogni esame vale 6 CFU"
    ]
    
    print("🧮 TEST CALCOLI MATEMATICI")
    print("="*50)
    
    for i, query in enumerate(math_queries, 1):
        print(f"\n{i}. 🤔 {query}")
        
        try:
            # Search
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
    print("⏳ Aspetto 30 secondi per il deploy Railway...")
    time.sleep(30)
    test_math_queries()
