#!/usr/bin/env python3
"""
Test OCR completo su Railway
Testa tutto il workflow: Upload → OCR → RAG → Query → Answer
"""

import requests
import base64
import time
import json
import io
from PIL import Image, ImageDraw, ImageFont

# ⚙️ CONFIGURAZIONE
RAILWAY_URL = "https://neuramind-production.up.railway.app/v1"  # 🔄 CAMBIA CON LA TUA URL
API_KEY = "super-secret-for-local"
USER_ID = "test_user_railway"

def create_contract_image():
    """Crea immagine contratto per test"""
    img = Image.new('RGB', (800, 1000), color='white')
    draw = ImageDraw.Draw(img)
    
    # Usa font di default
    try:
        font_large = ImageFont.load_default()
        font_normal = ImageFont.load_default()
    except:
        font_large = font_normal = None
    
    # Contratto dettagliato
    contract_text = [
        ("CONTRATTO DI LAVORO", 50, True),
        ("", 80, False),
        ("DATI PERSONALI:", 120, True),
        ("Nome: Mario Rossi", 150, False),
        ("CF: RSSMRA85M15H501Z", 180, False),
        ("Telefono: +39 333 1234567", 210, False),
        ("Email: mario.rossi@email.com", 240, False),
        ("", 280, False),
        ("DETTAGLI CONTRATTO:", 320, True),
        ("Posizione: Senior Software Developer", 350, False),
        ("Stipendio: €45,000 lordi annui", 380, False),
        ("Data inizio: 1 Gennaio 2024", 410, False),
        ("Data fine: 31 Dicembre 2024", 440, False),
        ("Periodo prova: 3 mesi", 470, False),
        ("", 510, False),
        ("RESPONSABILITÀ PRINCIPALI:", 550, True),
        ("• Sviluppo applicazioni web con React", 580, False),
        ("• Gestione database PostgreSQL", 610, False),
        ("• Code review e mentoring junior", 640, False),
        ("• Partecipazione riunioni agili", 670, False),
        ("• Documentazione tecnica", 700, False),
        ("", 740, False),
        ("SEDE E ORARI:", 780, True),
        ("Indirizzo: Via Milano 42, 20121 Milano", 810, False),
        ("Orario: Lunedì-Venerdì 9:00-18:00", 840, False),
        ("Smart working: 2 giorni/settimana", 870, False),
        ("", 910, False),
        ("Firmato: Mario Rossi", 950, False),
        ("Data firma: 15 Marzo 2024", 980, False),
    ]
    
    # Disegna il testo
    for text, y, is_title in contract_text:
        if text:
            font = font_large if is_title else font_normal
            draw.text((50, y), text, fill='black', font=font)
    
    # Converti in bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', quality=95)
    return img_bytes.getvalue()

def test_railway_health():
    """Test connessione Railway"""
    print("🌐 Test Connessione Railway...")
    
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ Railway raggiungibile")
            return True
        else:
            print(f"   ❌ Railway status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Errore connessione: {e}")
        return False

def test_railway_debug():
    """Test debug info Railway"""
    print("\n🔍 Test Debug Railway...")
    
    headers = {"X-API-Key": API_KEY}
    
    try:
        response = requests.get(f"{RAILWAY_URL}/debug", headers=headers, timeout=15)
        if response.status_code == 200:
            debug_info = response.json()
            print("   ✅ Debug info:")
            for key, value in debug_info.items():
                if isinstance(value, str) and len(value) > 50:
                    value = value[:47] + "..."
                print(f"      {key}: {value}")
            return True
        else:
            print(f"   ❌ Debug failed: {response.status_code}")
            print(f"      Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Errore debug: {e}")
        return False

def test_upload_document_railway():
    """Test upload documento OCR su Railway"""
    print("\n📸 Test Upload Documento Railway...")
    
    # Crea documento
    print("   📄 Creando contratto di test...")
    image_data = create_contract_image()
    print(f"   📁 Immagine creata: {len(image_data)} bytes")
    
    # Upload
    headers = {"X-API-Key": API_KEY}
    files = {
        'file': ('contratto_mario_rossi.jpg', image_data, 'image/jpeg')
    }
    data = {
        'user_id': USER_ID,
        'title': 'Contratto Mario Rossi - Senior Developer',
        'language': 'ita+eng'
    }
    
    print("   ⬆️ Uploading su Railway...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{RAILWAY_URL}/upload-document",
            headers=headers,
            files=files,
            data=data,
            timeout=30  # OCR può richiedere tempo
        )
        
        upload_time = time.time() - start_time
        print(f"   ⏱️ Upload completato in {upload_time:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   🎉 Upload SUCCESS!")
                print(f"      📋 Item ID: {result['item_id']}")
                print(f"      📝 Titolo: {result['title']}")
                print(f"      🧩 Chunks: {result['chunks_created']}")
                print(f"      ⏱️ Processing: {result['processing_time']}s")
                print(f"      🎯 Confidenza OCR: {result['ocr_metadata'].get('confidence', 0):.2f}")
                print(f"      📖 Preview: {result['text_preview'][:100]}...")
                return result['item_id']
            else:
                print(f"   ❌ Upload fallito: {result.get('error')}")
                return None
        else:
            print(f"   ❌ HTTP {response.status_code}")
            print(f"      Response: {response.text[:300]}")
            return None
            
    except requests.exceptions.Timeout:
        print("   ⏰ Timeout! OCR richiede più tempo del previsto")
        return None
    except Exception as e:
        print(f"   ❌ Errore upload: {e}")
        return None

def test_query_railway():
    """Test query documenti su Railway"""
    print("\n🔍 Test Query Railway...")
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    queries = [
        "Qual è il nome del dipendente?",
        "Quanto guadagna Mario Rossi?", 
        "Dove lavora Mario?",
        "Quando inizia il contratto?",
        "Quali sono le sue responsabilità?",
        "Può fare smart working?"
    ]
    
    all_results = []
    
    for query in queries:
        print(f"   💭 Query: '{query}'")
        
        try:
            response = requests.post(
                f"{RAILWAY_URL}/query",
                headers=headers,
                json={
                    "user_id": USER_ID,
                    "query": query,
                    "top_k": 3
                },
                timeout=15
            )
            
            if response.status_code == 200:
                matches = response.json()["matches"]
                print(f"      ✅ {len(matches)} risultati trovati")
                if matches:
                    best_score = matches[0].get('score', 0)
                    print(f"      🎯 Miglior score: {best_score:.3f}")
                all_results.append({"query": query, "matches": matches})
            else:
                print(f"      ❌ Query failed: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Errore: {e}")
    
    return all_results

def test_answer_railway():
    """Test generazione risposte su Railway"""
    print("\n🤖 Test Answer Generation Railway...")
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Query complessa
    complex_query = "Riassumi tutto il contratto di Mario Rossi: chi è, quanto guadagna, dove lavora e cosa fa"
    
    try:
        # 1. Query per contesti
        print(f"   🔍 Cerco contesti per: '{complex_query}'")
        query_response = requests.post(
            f"{RAILWAY_URL}/query",
            headers=headers,
            json={
                "user_id": USER_ID,
                "query": complex_query,
                "top_k": 5
            },
            timeout=15
        )
        
        if query_response.status_code != 200:
            print(f"   ❌ Query fallita: {query_response.status_code}")
            return False
        
        contexts = query_response.json()["matches"]
        print(f"   📚 Trovati {len(contexts)} contesti")
        
        # 2. Genera risposta
        print("   🧠 Generando risposta con GPT...")
        answer_response = requests.post(
            f"{RAILWAY_URL}/answer",
            headers=headers,
            json={
                "query": complex_query,
                "contexts": contexts
            },
            timeout=20
        )
        
        if answer_response.status_code == 200:
            answer = answer_response.json()["answer"]
            print("   🎉 RISPOSTA GENERATA:")
            print("   " + "="*60)
            print(f"   {answer}")
            print("   " + "="*60)
            return True
        else:
            print(f"   ❌ Answer failed: {answer_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        return False

def main():
    """Test completo Railway OCR"""
    print("🚀 TEST COMPLETO RAILWAY OCR")
    print("=" * 60)
    print(f"🌐 URL: {RAILWAY_URL}")
    print(f"👤 User: {USER_ID}")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Connessione
    if test_railway_health():
        tests_passed += 1
    
    # Test 2: Debug
    if test_railway_debug():
        tests_passed += 1
    
    # Test 3: Upload OCR
    item_id = test_upload_document_railway()
    if item_id:
        tests_passed += 1
        
        # Aspetta propagazione
        print("\n⏳ Aspetto 5 secondi per propagazione...")
        time.sleep(5)
        
        # Test 4: Query
        query_results = test_query_railway()
        if query_results:
            tests_passed += 1
        
        # Test 5: Answer
        if test_answer_railway():
            tests_passed += 1
    
    # Risultati finali
    print(f"\n📊 RISULTATI FINALI: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("\n🎉 TUTTI I TEST PASSATI!")
        print("\n✅ SISTEMA OCR RAILWAY FUNZIONA:")
        print("   📸 Upload immagini ✅")
        print("   🔍 OCR Tesseract ✅") 
        print("   🧩 Chunking ✅")
        print("   🔗 OpenAI Embeddings ✅")
        print("   🗄️ Pinecone Storage ✅")
        print("   🔍 Semantic Search ✅")
        print("   🤖 GPT Answers ✅")
        print("\n🚀 PRONTO PER PRODUZIONE!")
    else:
        print(f"\n⚠️ {total_tests - tests_passed} test falliti")
        print("🔧 Controlla i log sopra per debug")

if __name__ == "__main__":
    main()
