#!/usr/bin/env python3
"""
Test locale del servizio OCR
Testa il servizio senza server
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.ocr_service import ocr_service
from PIL import Image, ImageDraw, ImageFont
import io

def create_test_image():
    """Crea immagine di test"""
    img = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    text = """DOCUMENTO DI TEST

Questo è un documento di prova per testare
il sistema OCR di NeuraMind.

Contiene testo in italiano e anche qualche
parola in English per testare il multilinguismo.

Informazioni importanti:
- Data: 17 Agosto 2025
- Progetto: NeuraMind
- Stato: Testing fase 1

Il sistema dovrebbe essere in grado di
estrarre questo testo correttamente."""
    
    y = 30
    for line in text.split('\n'):
        if line.strip():
            draw.text((30, y), line, fill='black', font=font)
        y += 25
    
    # Converti in bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', quality=95)
    return img_bytes.getvalue()

def test_ocr_basic():
    """Test base OCR"""
    print("🔍 Test OCR Base...")
    
    try:
        # Crea immagine test
        image_data = create_test_image()
        print(f"   Immagine creata: {len(image_data)} bytes")
        
        # Test OCR
        extracted_text, metadata = ocr_service.extract_text_from_image(image_data)
        
        print("✅ OCR completato!")
        print(f"   Testo estratto ({len(extracted_text)} caratteri):")
        print(f"   {extracted_text[:200]}...")
        print(f"   Metadata: {metadata}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore OCR: {e}")
        return False

def test_supported_formats():
    """Test formati supportati"""
    print("\n🔍 Test Formati Supportati...")
    
    formats_to_test = [
        'image/jpeg',
        'image/png', 
        'image/bmp',
        'image/tiff',
        'application/pdf',  # Non supportato
        'text/plain'        # Non supportato
    ]
    
    for fmt in formats_to_test:
        supported = ocr_service.is_supported_format(fmt)
        status = "✅" if supported else "❌"
        print(f"   {status} {fmt}: {'Supportato' if supported else 'Non supportato'}")

def test_confidence_estimation():
    """Test stima confidenza"""
    print("\n🔍 Test Stima Confidenza...")
    
    test_texts = [
        "",  # Vuoto
        "a b c",  # Troppo corto
        "Questo è un testo di prova con parole comuni in italiano.",  # Buono
        "xzxzxz qwqwqw asdasd zxczxc",  # Rumore
        "The quick brown fox jumps over the lazy dog.",  # Inglese
    ]
    
    for text in test_texts:
        confidence = ocr_service._estimate_confidence(text)
        print(f"   Testo: '{text[:50]}...' → Confidenza: {confidence:.2f}")

def main():
    """Test completo locale"""
    print("🧪 TEST LOCALE SERVIZIO OCR")
    print("=" * 40)
    
    # Test formati
    test_supported_formats()
    
    # Test confidenza
    test_confidence_estimation()
    
    # Test OCR base
    if test_ocr_basic():
        print("\n🎉 Tutti i test locali passati!")
    else:
        print("\n❌ Test OCR fallito")

if __name__ == "__main__":
    main()
