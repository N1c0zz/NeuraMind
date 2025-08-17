#!/usr/bin/env python3
"""
🚀 Test Workflow Completo Railway
Test end-to-end del sistema RAG su produzione
"""

import requests
import json
import time

# Configurazione Railway
RAILWAY_URL = "https://neuramind-production.up.railway.app"
BASE_URL = f"{RAILWAY_URL}/v1"
API_KEY = "super-secret-for-local"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def print_step(step, title):
    """Stampa un step del test"""
    print(f"\n{'='*60}")
    print(f"🔹 STEP {step}: {title}")
    print('='*60)

def test_complete_rag_workflow():
    """Test completo del workflow RAG"""
    print("🚀 TEST WORKFLOW COMPLETO NEURAMIND - RAILWAY")
    print("🌐 Target: " + RAILWAY_URL)
    print("🎯 Testiamo: Upsert → Query → Answer")
    
    # STEP 1: Health Check
    print_step(1, "HEALTH CHECK")
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Railway server è UP e running!")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Impossibile raggiungere Railway: {e}")
        return False
    
    # STEP 2: Upsert - Salviamo un documento di test
    print_step(2, "UPSERT - Salvataggio Documento")
    print("🎯 Cosa testiamo: Testo → Chunking → OpenAI Embeddings → Pinecone Storage")
    
    test_document = {
        "user_id": "test_railway_user",
        "item_id": "doc_test_railway_001",
        "title": "Test Document - NeuraMind Railway Deploy",
        "text": """
        NeuraMind è un assistente AI personale avanzato deployato su Railway.
        
        ARCHITETTURA TECNICA:
        - Backend API sviluppato con FastAPI per performance elevate
        - Database vettoriale Pinecone per ricerca semantica ultra-veloce
        - Integrazione OpenAI per embeddings e generazione risposte intelligenti
        - Sistema RAG (Retrieval-Augmented Generation) per risposte contestuali
        
        FUNZIONALITÀ PRINCIPALI:
        - Chunking automatico dei documenti per ottimizzare la ricerca
        - Embedding vettoriali con modello text-embedding-ada-002
        - Ricerca semantica con similarity matching
        - Generazione risposte con GPT-4o-mini
        
        DEPLOYMENT:
        - Hosting su Railway per scalabilità automatica
        - Variabili ambiente sicure per API keys
        - Docker container per consistency cross-platform
        - Health checks e monitoring integrati
        
        UTILIZZO:
        NeuraMind può essere usato per gestire knowledge base personali,
        rispondere a domande sui propri documenti, e fornire assistenza
        AI contestualizzata basata sui contenuti dell'utente.
        """
    }
    
    print(f"📄 Documento: {test_document['title']}")
    print(f"📊 Dimensione: {len(test_document['text'])} caratteri")
    print("⏳ Invio a Railway...")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/embed-upsert",
            headers=headers,
            json=test_document,
            timeout=60  # Timeout più lungo per l'elaborazione
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            chunk_ids = result.get("ids", [])
            print(f"✅ Upsert completato in {elapsed:.2f}s")
            print(f"📦 Chunks creati: {len(chunk_ids)}")
            print(f"🆔 IDs: {chunk_ids[:3]}..." if len(chunk_ids) > 3 else f"🆔 IDs: {chunk_ids}")
        else:
            print(f"❌ Upsert fallito: {response.status_code}")
            print(f"📄 Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout durante upsert - Operazione troppo lenta")
        return False
    except Exception as e:
        print(f"❌ Errore durante upsert: {e}")
        return False
    
    # STEP 3: Query - Ricerca semantica
    print_step(3, "QUERY - Ricerca Semantica")
    print("🎯 Cosa testiamo: Domanda → OpenAI Embedding → Pinecone Search → Risultati")
    
    test_queries = [
        "Come funziona l'architettura di NeuraMind?",
        "Quali tecnologie usa NeuraMind per l'AI?",
        "Come viene deployato NeuraMind?"
    ]
    
    all_matches = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: '{query}'")
        
        query_data = {
            "user_id": "test_railway_user",
            "query": query,
            "top_k": 3
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/query",
                headers=headers,
                json=query_data,
                timeout=30
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                matches = result.get("matches", [])
                print(f"✅ Query completata in {elapsed:.2f}s")
                print(f"📊 Risultati trovati: {len(matches)}")
                
                # Mostra i primi risultati
                for j, match in enumerate(matches[:2], 1):
                    score = match.get("score", 0)
                    text_preview = match.get("metadata", {}).get("text", "")[:100]
                    print(f"   {j}. Score: {score:.3f} - {text_preview}...")
                
                # Usa i migliori match per il test answer
                if i == 1:  # Prima query
                    all_matches = matches
                    
            else:
                print(f"❌ Query fallita: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Errore durante query: {e}")
            return False
    
    # STEP 4: Answer - Generazione risposta AI
    print_step(4, "ANSWER - Generazione Risposta AI")
    print("🎯 Cosa testiamo: Query + Contesti → OpenAI GPT → Risposta Finale")
    
    final_question = "Spiegami dettagliatamente NeuraMind: architettura, tecnologie e deployment"
    
    print(f"❓ Domanda finale: {final_question}")
    print("⏳ GPT sta generando la risposta...")
    
    answer_data = {
        "query": final_question,
        "contexts": all_matches[:3]  # Usa i 3 migliori risultati
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/answer",
            headers=headers,
            json=answer_data,
            timeout=45
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("answer", "")
            print(f"✅ Risposta generata in {elapsed:.2f}s")
            print(f"\n🤖 RISPOSTA FINALE DI NEURAMIND:")
            print("─" * 80)
            print(answer)
            print("─" * 80)
        else:
            print(f"❌ Answer fallito: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante answer: {e}")
        return False
    
    # STEP 5: Risultati finali
    print_step(5, "RISULTATI FINALI")
    
    print("🎉 WORKFLOW RAG COMPLETATO CON SUCCESSO!")
    print("\n📊 Componenti testati:")
    print("✅ Railway Hosting - Server raggiungibile e stabile")
    print("✅ FastAPI Backend - API endpoints funzionanti")
    print("✅ OpenAI Integration - Embeddings e GPT operativi")
    print("✅ Pinecone Database - Storage e ricerca vettoriale OK")
    print("✅ RAG Pipeline - Workflow end-to-end funzionante")
    
    print(f"\n🚀 NeuraMind è PRODUCTION-READY su Railway!")
    print(f"🌐 API Endpoint: {RAILWAY_URL}")
    print(f"📚 Docs: {RAILWAY_URL}/docs")
    
    return True

if __name__ == "__main__":
    success = test_complete_rag_workflow()
    
    if success:
        print(f"\n🏆 SUCCESSO TOTALE! Il backend NeuraMind è completamente operativo.")
    else:
        print(f"\n💥 Alcuni test sono falliti. Controlla i logs per dettagli.")
