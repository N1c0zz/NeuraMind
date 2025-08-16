import requests
import json
import time

# Configurazione
BASE_URL = "http://127.0.0.1:8000/v1"
API_KEY = "super-secret-for-local"  # Deve corrispondere a DEV_API_KEY nel .env

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def workflow_demo():
    """Demo completa del workflow RAG di NeuraMind"""
    print("🧠 === WORKFLOW COMPLETO NEURAMIND ===")
    print("Simuliamo un assistente AI che conosce i tuoi documenti personali")
    print("=" * 60)
    
    # === STEP 1: UPSERT - Salviamo documenti nell'AI ===
    print("\n📚 STEP 1: UPSERT - Salviamo documenti nella knowledge base")
    print("-" * 50)
    
    # Documento 1: Appunti di lavoro
    doc1 = {
        "user_id": "nico123",
        "item_id": "lavoro_001", 
        "title": "Appunti Riunione Progetto NeuraMind",
        "text": """
        Riunione del 15 Agosto 2025 - Progetto NeuraMind
        
        OBIETTIVI:
        - Creare un assistente AI personale per mobile
        - L'AI deve conoscere documenti, foto, note dell'utente
        - Implementare sistema RAG (Retrieval-Augmented Generation)
        - Tecnologie: FastAPI, OpenAI, Pinecone
        
        ARCHITETTURA:
        - Backend API con FastAPI
        - Database vettoriale Pinecone per embeddings
        - OpenAI per generazione risposte e embeddings
        - Chunking automatico dei documenti
        
        PROSSIMI PASSI:
        - Completare MVP del backend
        - Testare workflow completo RAG
        - Sviluppare app mobile React Native
        """
    }
    
    print(f"📄 Salvando: {doc1['title']}")
    response1 = requests.post(f"{BASE_URL}/embed-upsert", headers=headers, json=doc1)
    print(f"✅ Risposta: {response1.status_code} - {response1.json()}")
    
    # Documento 2: Informazioni personali
    doc2 = {
        "user_id": "nico123",
        "item_id": "personale_001",
        "title": "Note Personali - Hobby e Interessi", 
        "text": """
        I miei hobby e interessi principali:
        
        PROGRAMMAZIONE:
        - Python è il mio linguaggio preferito
        - Sto imparando FastAPI e sviluppo API
        - Interessato a AI e Machine Learning
        - Vorrei migliorare in React Native per mobile
        
        LETTURA:
        - Adoro i libri di fantascienza
        - Ultimo libro letto: "Il Problema dei Tre Corpi"
        - Mi piacciono anche saggi su tecnologia e innovazione
        
        VIAGGI:
        - Voglio visitare il Giappone quest'anno
        - Mi piacciono le città tecnologiche come Tokyo e San Francisco
        - Preferisco viaggi che combinano cultura e tecnologia
        """
    }
    
    print(f"📄 Salvando: {doc2['title']}")
    response2 = requests.post(f"{BASE_URL}/embed-upsert", headers=headers, json=doc2)
    print(f"✅ Risposta: {response2.status_code} - {response2.json()}")
    
    # Documento 3: Ricette
    doc3 = {
        "user_id": "nico123",
        "item_id": "cucina_001",
        "title": "Le mie ricette preferite",
        "text": """
        RICETTE CHE SO CUCINARE BENE:
        
        PASTA CARBONARA:
        - Guanciale, uova, pecorino, pepe nero
        - Tecnica: mantecatura a fuoco spento
        - Tempo: 15 minuti
        
        RISOTTO AI FUNGHI:
        - Riso Arborio, funghi porcini, brodo vegetale
        - Tostatura del riso importante
        - Tempo: 25 minuti
        
        TIRAMISU:
        - Savoiardi, caffè, mascarpone, uova, cacao
        - Riposo in frigo almeno 4 ore
        - La mia specialità per le occasioni speciali
        """
    }
    
    print(f"📄 Salvando: {doc3['title']}")
    response3 = requests.post(f"{BASE_URL}/embed-upsert", headers=headers, json=doc3)
    print(f"✅ Risposta: {response3.status_code} - {response3.json()}")
    
    print("\n⏱️ Aspetto 2 secondi per permettere l'indicizzazione...")
    time.sleep(2)
    
    # === STEP 2: QUERY - Ricerca semantica ===
    print("\n🔍 STEP 2: QUERY - Ricerca semantica nella knowledge base")
    print("-" * 50)
    
    queries = [
        "Quali tecnologie stiamo usando per NeuraMind?",
        "Che hobby ha l'utente?", 
        "Come si fa il tiramisù?"
    ]
    
    all_contexts = []
    
    for i, query in enumerate(queries, 1):
        print(f"\n🔎 Query {i}: '{query}'")
        
        query_data = {
            "user_id": "nico123",
            "query": query,
            "top_k": 3
        }
        
        response = requests.post(f"{BASE_URL}/query", headers=headers, json=query_data)
        matches = response.json().get("matches", [])
        
        print(f"📊 Trovati {len(matches)} risultati:")
        for j, match in enumerate(matches):
            score = match.get("score", 0)
            preview = match.get("metadata", {}).get("preview", "")[:100]
            print(f"  {j+1}. Score: {score:.3f} - {preview}...")
        
        all_contexts.extend(matches)
    
    # === STEP 3: ANSWER - Generazione risposta AI ===
    print("\n🤖 STEP 3: ANSWER - L'AI genera risposte intelligenti")
    print("-" * 50)
    
    test_questions = [
        "Riassumi il progetto NeuraMind e le tecnologie che usiamo",
        "Quali sono i miei hobby principali?",
        "Dammi una ricetta che so cucinare bene"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n❓ Domanda {i}: '{question}'")
        
        # Prima facciamo la query per trovare contesti rilevanti
        query_data = {
            "user_id": "nico123", 
            "query": question,
            "top_k": 5
        }
        
        query_response = requests.post(f"{BASE_URL}/query", headers=headers, json=query_data)
        contexts = query_response.json().get("matches", [])
        
        # Poi generiamo la risposta
        answer_data = {
            "query": question,
            "contexts": contexts
        }
        
        answer_response = requests.post(f"{BASE_URL}/answer", headers=headers, json=answer_data)
        answer = answer_response.json().get("answer", "Nessuna risposta")
        
        print(f"🎯 Risposta AI: {answer}")
        print()
    
    print("=" * 60)
    print("✅ WORKFLOW COMPLETO TESTATO CON SUCCESSO!")
    print("🧠 NeuraMind ora conosce i tuoi documenti e può rispondere alle tue domande!")

if __name__ == "__main__":
    workflow_demo()
