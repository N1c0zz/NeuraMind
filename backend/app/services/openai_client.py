import logging
from typing import List
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key non configurata")
        
        # Inizializzazione semplificata
        try:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("✅ OpenAI client inizializzato")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione OpenAI: {e}")
            raise ValueError(f"Impossibile inizializzare OpenAI: {e}")

    def create_embedding(self, text: str) -> List[float]:
        """Crea embedding per un testo"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Errore creazione embedding: {e}")
            raise

    def generate_answer(self, query: str, context: str) -> str:
        """Genera una risposta basata su query e contesto"""
        try:
            prompt = f"""Basandoti sui seguenti documenti estratti tramite OCR, rispondi alla domanda dell'utente.

ISTRUZIONI:
- Analizza attentamente tutto il contenuto fornito
- Se il contenuto è frammentato (tipico dell'OCR), cerca di interpretarlo nel contesto
- Rispondi in modo utile e informativo
- Se devi fare calcoli, mostra sempre il procedimento
- IMPORTANTE: Il contenuto qui sotto proviene da documenti reali dell'utente, anche se può sembrare formattato male a causa dell'OCR

CONTENUTO DEI DOCUMENTI:
{context}

DOMANDA: {query}

RISPOSTA:"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Sei un assistente AI che analizza documenti estratti tramite OCR. Il tuo compito è fornire risposte utili basandoti sul contenuto fornito, anche quando il testo è mal formattato a causa dell'OCR. Sii flessibile nell'interpretazione e utile nelle risposte."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,  # Aumentato per risposte più complete
                temperature=0.1  # Più deterministico
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Errore generazione risposta: {e}")
            raise