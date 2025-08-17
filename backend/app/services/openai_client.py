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
            prompt = f"""Basandoti esclusivamente sui seguenti documenti, rispondi alla domanda dell'utente.

ISTRUZIONI SPECIALI:
- Se la domanda richiede calcoli (media, somma, totale), eseguili utilizzando i numeri trovati nei documenti
- Per domande su voti: estrai tutti i voti numerici e calcola la media se richiesto
- Per domande sui crediti: cerca termini come "CFU", "crediti", "ECTS" nei documenti
- Se devi fare calcoli, mostra sempre il procedimento: es. "Media: (28+30+24)/3 = 27.3"
- Se la risposta non è presente nei documenti, rispondi "Non ho informazioni sufficienti per rispondere a questa domanda nei documenti forniti."

DOCUMENTI:
{context}

DOMANDA: {query}

RISPOSTA:"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Sei un assistente intelligente che risponde solo basandosi sui documenti forniti. Puoi fare calcoli matematici quando necessario utilizzando i dati trovati nei documenti."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Errore generazione risposta: {e}")
            raise