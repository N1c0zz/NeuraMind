#!/usr/bin/env python3
"""
Test qualità OCR con preprocessing migliorato
"""

import requests
from PIL import Image, ImageEnhance, ImageFilter
import io
import os

def enhance_image_for_ocr(image_path):
    """Migliora l'immagine per OCR più accurato"""
    print(f"🔧 Migliorando immagine: {image_path}")
    
    try:
        # Carica immagine
        with Image.open(image_path) as img:
            # Converti in RGB se necessario
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 1. Aumenta contrasto
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)
            
            # 2. Aumenta nitidezza
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.3)
            
            # 3. Scala a dimensione ottimale
            width, height = img.size
            if width < 1200:  # Se troppo piccola, ingrandisci
                scale = 1200 / width
                new_size = (int(width * scale), int(height * scale))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                print(f"   📏 Scalata da {(width, height)} a {new_size}")
            
            # Salva versione migliorata
            enhanced_path = image_path.replace('.jpeg', '_enhanced.jpeg')
            img.save(enhanced_path, 'JPEG', quality=95)
            print(f"   ✅ Salvata in: {enhanced_path}")
            
            return enhanced_path
            
    except Exception as e:
        print(f"   ❌ Errore enhancement: {e}")
        return image_path

def test_enhanced_upload(original_path):
    """Test upload con immagine migliorata"""
    
    # Migliora immagine
    enhanced_path = enhance_image_for_ocr(original_path)
    
    # Upload normale
    print(f"\n📸 Upload originale...")
    result_original = upload_document(original_path, "Originale")
    
    # Upload migliorata  
    print(f"\n🔧 Upload migliorata...")
    result_enhanced = upload_document(enhanced_path, "Migliorata")
    
    # Confronto
    if result_original and result_enhanced:
        print(f"\n📊 CONFRONTO:")
        print(f"   Originale - Confidenza: {result_original.get('ocr_metadata', {}).get('confidence', 0):.2f}")
        print(f"   Migliorata - Confidenza: {result_enhanced.get('ocr_metadata', {}).get('confidence', 0):.2f}")
        
        print(f"\n   📖 TESTO ORIGINALE:")
        print(f"   {result_original.get('text_preview', '')[:200]}...")
        
        print(f"\n   📖 TESTO MIGLIORATO:")
        print(f"   {result_enhanced.get('text_preview', '')[:200]}...")

def upload_document(file_path, title):
    """Upload documento via API"""
    url = "https://neuramind-production.up.railway.app/v1/upload-document"
    headers = {"X-API-Key": "super-secret-for-local"}
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'image/jpeg')}
            data = {
                'user_id': 'nicom_test_enhanced',
                'title': title,
                'language': 'ita+eng'
            }
            
            response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✅ Success! Confidenza: {result['ocr_metadata'].get('confidence', 0):.2f}")
                    return result
                    
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        
    return None

if __name__ == "__main__":
    image_path = input("📎 Percorso immagine da migliorare: ")
    if os.path.exists(image_path):
        test_enhanced_upload(image_path)
    else:
        print("❌ File non trovato")
