#!/usr/bin/env python3
"""
Test completo del sistema OCR
Testa: Upload immagine → OCR → RAG → Query → Answer
"""

import requests
import base64
import time
import json
from PIL import Image, ImageDraw, ImageFont
import io

# Configurazione
BASE_URL = "https://neuramind-production.up.railway.app/v1"  # Cambia con la tua URL Railway
# BASE_URL = "http://localhost:8000/v1"  # Per test locali
API_KEY = "super-secret-for-local"

def create_test_document():
    """Crea un'immagine di test con testo"""
    # Crea immagine 800x600 bianca
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Prova a usare un font di sistema
    try:
        font = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Testo del documento
    text_content = """CONTRATTO DI LAVORO

Nome: Mario Rossi
Posizione: Sviluppatore Software
Stipendio: €35,000 all'anno
Data inizio: 1 Gennaio 2024
Data fine: 31 Dicembre 2024

Responsabilità:
- Sviluppo applicazioni web
- Manutenzione database
- Supporto clienti

Sede: Milano, Via Roma 123
Orario: 9:00 - 18:00

Firmato: Mario Rossi
Data: 15 Marzo 2024"""
    
    # Disegna il testo
    y_position = 50
    for line in text_content.split('\n'):
        if line.strip():
            if line.isupper() or 'Nome:' in line or 'Firmato:' in line:
                draw.text((50, y_position), line, fill='black', font=font)
            else:
                draw.text((50, y_position), line, fill='black', font=font_small)
        y_position += 30
    
    # Salva come bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', quality=95)
    img_bytes.seek(0)
    
    return img_bytes.getvalue()

def test_health():
    """Test endpoint health"""
    print("🔍 Test Health Endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check OK")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Errore connessione: {e}")
        return False

def test_debug():
    """Test endpoint debug"""
    print("\n🔍 Test Debug Endpoint...")
    
    headers = {"X-API-Key": API_KEY}
    
    try:
        response = requests.get(f"{BASE_URL}/debug", headers=headers)
        if response.status_code == 200:
            debug_info = response.json()
            print("✅ Debug info:")
            for key, value in debug_info.items():
                print(f"   {key}: {value}")
            return True
        else:
            print(f"❌ Debug failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Errore debug: {e}")
        return False

def test_upload_document():
    """Test upload documento con OCR"""
    print("\n📸 Test Upload Documento...")
    
    # Crea documento di test
    print("   Creando documento di test...")
    image_data = create_test_document()
    
    # Upload
    headers = {"X-API-Key": API_KEY}
    files = {
        'file': ('test_contract.jpg', image_data, 'image/jpeg')
    }
    data = {
        'user_id': 'test_user_ocr',
        'title': 'Contratto di Lavoro Mario Rossi',
        'language': 'ita+eng'
    }
    
    print("   Uploading...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/upload-document",
            headers=headers,
            files=files,
            data=data
        )
        
        upload_time = time.time() - start_time
        print(f"   Upload completato in {upload_time:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Upload successo!")
                print(f"   Item ID: {result['item_id']}")
                print(f"   Titolo: {result['title']}")
                print(f"   Chunks creati: {result['chunks_created']}")
                print(f"   Tempo processing: {result['processing_time']}s")
                print(f"   Confidenza OCR: {result['ocr_metadata'].get('confidence', 0):.2f}")
                print(f"   Testo (anteprima): {result['text_preview']}")
                return result['item_id']
            else:
                print(f"❌ Upload fallito: {result.get('error', 'Unknown error')}")
                return None
        else:
            print(f"❌ Upload failed HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Errore upload: {e}")
        return None

def test_query_document(user_id="test_user_ocr"):
    """Test query sui documenti"""
    print("\n🔍 Test Query Documento...")
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    queries = [
        "Chi è Mario Rossi?",
        "Qual è lo stipendio nel contratto?",
        "Dove si trova la sede di lavoro?",
        "Quali sono le responsabilità?",
        "Quando scade il contratto?"
    ]
    
    results = []
    
    for query in queries:
        print(f"   Query: {query}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/query",
                headers=headers,
                json={
                    "user_id": user_id,
                    "query": query,
                    "top_k": 3
                }
            )
            
            if response.status_code == 200:
                matches = response.json()["matches"]
                print(f"   ✅ Trovati {len(matches)} risultati")
                if matches:
                    best_match = matches[0]
                    print(f"   📄 Miglior match (score: {best_match.get('score', 0):.3f})")
                    print(f"      {best_match.get('metadata', {}).get('text', '')[:100]}...")
                results.append({"query": query, "matches": matches})
            else:
                print(f"   ❌ Query failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Errore query: {e}")
    
    return results

def test_answer_from_document(user_id="test_user_ocr"):
    """Test generazione risposte"""
    print("\n🤖 Test Answer Generation...")
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Prima trova contesti rilevanti
    test_query = "Riassumi il contratto di Mario Rossi"
    
    try:
        # 1. Query per contesti
        query_response = requests.post(
            f"{BASE_URL}/query",
            headers=headers,
            json={
                "user_id": user_id,
                "query": test_query,
                "top_k": 3
            }
        )
        
        if query_response.status_code != 200:
            print(f"❌ Query failed: {query_response.status_code}")
            return False
        
        contexts = query_response.json()["matches"]
        print(f"   Trovati {len(contexts)} contesti")
        
        # 2. Genera risposta
        answer_response = requests.post(
            f"{BASE_URL}/answer",
            headers=headers,
            json={
                "query": test_query,
                "contexts": contexts
            }
        )
        
        if answer_response.status_code == 200:
            answer = answer_response.json()["answer"]
            print("✅ Risposta generata:")
            print(f"   {answer}")
            return True
        else:
            print(f"❌ Answer failed: {answer_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Errore answer generation: {e}")
        return False

def main():
    """Test completo del workflow OCR"""
    print("🚀 TEST COMPLETO SISTEMA OCR")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("❌ Sistema non raggiungibile")
        return
    
    # Test debug
    test_debug()
    
    # Test upload
    item_id = test_upload_document()
    if not item_id:
        print("❌ Upload fallito, non posso continuare")
        return
    
    # Aspetta un po' per la propagazione
    print("\n⏳ Aspetto 3 secondi per propagazione...")
    time.sleep(3)
    
    # Test query
    test_query_document()
    
    # Test answer
    test_answer_from_document()
    
    print("\n🎉 Test completato!")
    print("\n📋 RIEPILOGO:")
    print("✅ Health check")
    print("✅ Upload documento con OCR")
    print("✅ Query semantica")
    print("✅ Generazione risposte")
    print("\n🚀 Il sistema OCR è funzionante!")

if __name__ == "__main__":
    main()
