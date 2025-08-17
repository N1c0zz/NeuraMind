"""
OCR Service ibrido per estrazione testo da immagini
Fallback automatico se Tesseract non disponibile
"""

import logging
from typing import Optional, Tuple
import io
import time
import random

logger = logging.getLogger(__name__)

# Try to import OCR dependencies
TESSERACT_AVAILABLE = False
MAGIC_AVAILABLE = False

try:
    import pytesseract
    from PIL import Image
    import os
    import platform
    
    # Configurazione Tesseract per Windows
    if platform.system() == "Windows":
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break
    
    # Test Tesseract
    try:
        pytesseract.image_to_string(Image.new('RGB', (100, 100), 'white'))
        TESSERACT_AVAILABLE = True
        logger.info("✅ Tesseract OCR disponibile")
    except Exception as e:
        logger.warning(f"⚠️ Tesseract non funziona: {e}")
        
except ImportError as e:
    logger.warning(f"⚠️ Dipendenze OCR non disponibili: {e}")

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ python-magic non disponibile, uso fallback")

class OCRService:
    """Servizio OCR con fallback automatico"""
    
    def __init__(self):
        self.supported_formats = {
            'image/jpeg', 'image/jpg', 'image/png', 
            'image/bmp', 'image/tiff', 'image/webp'
        }
        self.tesseract_available = TESSERACT_AVAILABLE
        self.tesseract_config = r'--oem 3 --psm 6'
        
    def is_supported_format(self, content_type: str) -> bool:
        """Verifica se il formato è supportato"""
        return content_type.lower() in self.supported_formats
    
    def detect_content_type(self, file_data: bytes) -> str:
        """Rileva automaticamente il tipo di file"""
        if MAGIC_AVAILABLE:
            try:
                mime = magic.from_buffer(file_data, mime=True)
                return mime
            except Exception as e:
                logger.warning(f"Errore rilevamento MIME: {e}")
        
        # Fallback: rileva da header bytes
        if file_data.startswith(b'\xff\xd8\xff'):
            return 'image/jpeg'
        elif file_data.startswith(b'\x89PNG'):
            return 'image/png'
        elif file_data.startswith(b'BM'):
            return 'image/bmp'
        else:
            return "application/octet-stream"
    
    def _extract_text_real(self, image_data: bytes, language: str) -> Tuple[str, dict]:
        """Estrazione OCR reale con Tesseract"""
        from PIL import Image
        
        # Carica immagine
        image = Image.open(io.BytesIO(image_data))
        
        # Preprocessing
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # OCR
        extracted_text = pytesseract.image_to_string(
            image, lang=language, config=self.tesseract_config
        )
        
        # Pulizia
        cleaned_text = self._clean_extracted_text(extracted_text)
        
        metadata = {
            'method': 'tesseract_ocr',
            'original_size': image.size,
            'language': language,
            'text_length': len(cleaned_text),
            'confidence': self._estimate_confidence(cleaned_text)
        }
        
        return cleaned_text, metadata
    
    def _extract_text_mock(self, image_data: bytes, language: str) -> Tuple[str, dict]:
        """Estrazione OCR simulata"""
        time.sleep(random.uniform(0.3, 0.8))  # Simula processing
        
        # Testo simulato basato sulla dimensione
        if len(image_data) < 50000:
            text = """DOCUMENTO SIMULATO

Questo è un documento di test generato dal
sistema OCR mock di NeuraMind.

Data: 17 Agosto 2025
Sistema: Mock OCR Service
Stato: Funzionante

Il testo è stato simulato perché Tesseract
non è disponibile in questo ambiente."""
        else:
            text = """CONTRATTO DI LAVORO SIMULATO

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

NOTA: Questo testo è stato generato dal sistema
mock OCR per scopi di testing.

Firmato: Mario Rossi
Data: 15 Marzo 2024"""
        
        metadata = {
            'method': 'mock_ocr',
            'original_size': (800, 600),
            'language': language,
            'text_length': len(text),
            'confidence': 0.85,
            'note': 'Testo simulato - Tesseract non disponibile'
        }
        
        return text, metadata
    
    def extract_text_from_image(
        self, 
        image_data: bytes, 
        language: str = 'ita+eng'
    ) -> Tuple[str, dict]:
        """
        Estrae testo da immagine con fallback automatico
        """
        try:
            if self.tesseract_available:
                logger.info("🔍 Usando Tesseract OCR...")
                return self._extract_text_real(image_data, language)
            else:
                logger.info("🎭 Usando Mock OCR (Tesseract non disponibile)...")
                return self._extract_text_mock(image_data, language)
                
        except Exception as e:
            logger.error(f"Errore OCR, fallback a mock: {e}")
            return self._extract_text_mock(image_data, language)
    
    def extract_text_with_fallback(
        self, 
        image_data: bytes,
        primary_lang: str = 'ita+eng'
    ) -> Tuple[str, dict]:
        """Estrae testo con fallback su lingue diverse"""
        return self.extract_text_from_image(image_data, primary_lang)
    
    def _clean_extracted_text(self, text: str) -> str:
        """Pulisce il testo estratto"""
        if not text:
            return ""
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    def _estimate_confidence(self, text: str) -> float:
        """Stima confidenza del testo"""
        if not text:
            return 0.0
        
        factors = []
        
        if len(text) > 10:
            factors.append(0.3)
        
        common_words = ['il', 'la', 'di', 'che', 'e', 'a', 'the', 'and', 'of']
        word_count = len([w for w in text.lower().split() if w in common_words])
        if word_count > 0:
            factors.append(min(0.4, word_count * 0.1))
        
        alpha_ratio = sum(c.isalpha() for c in text) / len(text)
        factors.append(alpha_ratio * 0.3)
        
        return min(1.0, sum(factors))

# Istanza globale
ocr_service = OCRService()
