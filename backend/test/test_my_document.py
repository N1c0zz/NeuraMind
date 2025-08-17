#!/usr/bin/env python3
"""
Test rapido con TUO documento
Carica un tuo file e fai domande reali
"""

import requests
import os
import time

# ⚙️ CONFIGURAZIONE
RAILWAY_URL = "https://neuramind-production.up.railway.app/v1"
API_KEY = "super-secret-for-local"
YOUR_USER_ID = "nicom_test"  # Cambia con il tuo ID

def upload_your_document(file_path, title=""):
    """Carica il tuo documento"""
    print(f"📸 Caricando: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ File non trovato: {file_path}")
        return None
    
    # Verifica dimensione
    file_size = os.path.getsize(file_path)
    print(f"   📁 Dimensione: {file_size/1024:.1f} KB")
    
    if file_size > 20 * 1024 * 1024:  # 20MB limit
        print("   ⚠️ File troppo grande (max 20MB)")
        return None
    
    # Upload
    headers = {"X-API-Key": API_KEY}
    
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'image/jpeg')}
        data = {
            'user_id': YOUR_USER_ID,
            'title': title or os.path.basename(file_path),
            'language': 'ita+eng'
        }
        
        print("   ⬆️ Uploading...")
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{RAILWAY_URL}/upload-document",
                headers=headers,
                files=files,
                data=data,
                timeout=60  # 1 minuto per documenti grandi
            )
            
            upload_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✅ SUCCESS! ({upload_time:.1f}s)")
                    print(f"      📋 ID: {result['item_id']}")
                    print(f"      🧩 Chunks: {result['chunks_created']}")
                    print(f"      🎯 Confidenza: {result['ocr_metadata'].get('confidence', 0):.2f}")
                    print(f"      📖 Testo estratto:")
                    print("      " + "="*50)
                    print(f"      {result['text_preview']}")
                    print("      " + "="*50)
                    return result['item_id']
                else:
                    print(f"   ❌ Errore: {result.get('error')}")
                    return None
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"   ❌ Errore upload: {e}")
            return None

def ask_questions_interactive():
    """Sessione interattiva di domande"""
    print("\n💬 SESSIONE DOMANDE INTERATTIVA")
    print("Digita le tue domande (o 'quit' per uscire)")
    print("=" * 50)
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    while True:
        question = input("\n🤔 La tua domanda: ").strip()
        
        if question.lower() in ['quit', 'exit', 'basta', 'fine']:
            print("👋 Ciao!")
            break
            
        if not question:
            continue
            
        print(f"   🔍 Cercando risposta...")
        
        try:
            # 1. Query per contesti
            query_response = requests.post(
                f"{RAILWAY_URL}/query",
                headers=headers,
                json={
                    "user_id": YOUR_USER_ID,
                    "query": question,
                    "top_k": 3
                },
                timeout=15
            )
            
            if query_response.status_code != 200:
                print(f"   ❌ Errore ricerca: {query_response.status_code}")
                continue
            
            contexts = query_response.json()["matches"]
            
            if not contexts:
                print("   ❌ Nessun risultato trovato per questa domanda")
                continue
                
            print(f"   📚 Trovati {len(contexts)} contesti (score: {contexts[0].get('score', 0):.3f})")
            
            # 2. Genera risposta
            answer_response = requests.post(
                f"{RAILWAY_URL}/answer",
                headers=headers,
                json={
                    "query": question,
                    "contexts": contexts
                },
                timeout=20
            )
            
            if answer_response.status_code == 200:
                answer = answer_response.json()["answer"]
                print(f"\n   🤖 RISPOSTA:")
                print("   " + "="*50)
                print(f"   {answer}")
                print("   " + "="*50)
            else:
                print(f"   ❌ Errore generazione risposta: {answer_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Errore: {e}")

def calculate_cost_estimate(text_length, queries_count):
    """Calcola stima costi"""
    print(f"\n💰 STIMA COSTI:")
    
    # Costi per documento
    tokens_embedding = text_length // 3  # Circa 1 token ogni 3 caratteri
    cost_embedding = tokens_embedding * 0.0000001  # $0.0001 per 1K tokens
    
    # Costi per query (stima)
    cost_per_query = 0.001  # Embedding query + GPT response
    cost_queries = queries_count * cost_per_query
    
    total_cost = cost_embedding + cost_queries
    
    print(f"   📄 Documento ({text_length} char): ${cost_embedding:.6f}")
    print(f"   🔍 {queries_count} domande: ${cost_queries:.4f}")
    print(f"   💸 TOTALE: ${total_cost:.4f}")
    print(f"   📊 Per 100 documenti simili: ${total_cost * 100:.2f}")

def main():
    """Test con tuo documento"""
    print("🧪 TEST CON TUO DOCUMENTO")
    print("=" * 50)
    
    # Chiedi il file
    print("📁 ESEMPI DI FILE SUPPORTATI:")
    print("   • Foto contratti, fatture")
    print("   • Screenshot email, chat") 
    print("   • Documenti scansionati")
    print("   • Appunti fotografati")
    print("   • Ricevute, certificati")
    print()
    
    file_path = input("📎 Percorso del tuo file (es: C:/Users/..../documento.jpg): ").strip()
    
    if not file_path:
        print("❌ Nessun file specificato")
        return
    
    # Titolo opzionale
    title = input("📝 Titolo documento (opzionale): ").strip()
    
    # Upload
    item_id = upload_your_document(file_path, title)
    
    if not item_id:
        print("❌ Upload fallito")
        return
    
    print("\n⏳ Aspetto 3 secondi per propagazione...")
    time.sleep(3)
    
    # Sessione domande
    ask_questions_interactive()
    
    # Stima costi (basata su dimensione file)
    try:
        file_size = os.path.getsize(file_path)
        estimated_text = file_size // 10  # Stima grossolana
        calculate_cost_estimate(estimated_text, 5)  # 5 domande di esempio
    except:
        pass

if __name__ == "__main__":
    main()
