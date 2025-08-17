import logging
from typing import List
import openai
from app.core.config import settings

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key non configurata")
        
        # Inizializzazione robusta del client
        try:
            self.client = openai.OpenAI(api_key=self.api_key)
        except Exception as e:
            # Fallback per versioni più vecchie
            logger.warning(f"Errore inizializzazione client OpenAI: {e}")
            openai.api_key = self.api_key
            self.client = None

    def create_embedding(self, text: str) -> List[float]:
        """Crea embedding per un testo"""
        try:
            if self.client:
                # Versione nuova
                response = self.client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=text
                )
                return response.data[0].embedding
            else:
                # Versione vecchia
                response = openai.Embedding.create(
                    model="text-embedding-ada-002", 
                    input=text
                )
                return response['data'][0]['embedding']
        except Exception as e:
            logger.error(f"Errore creazione embedding: {e}")
            raise

    def generate_answer(self, query: str, context: str) -> str:
        """Genera una risposta basata su query e contesto"""
        try:
            prompt = f"""Basandoti esclusivamente sui seguenti documenti, rispondi alla domanda dell'utente.
Se la risposta non è presente nei documenti, rispondi "Non ho informazioni sufficienti per rispondere a questa domanda nei documenti forniti."

DOCUMENTI:
{context}

DOMANDA: {query}

RISPOSTA:"""

            if self.client:
                # Versione nuova
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Sei un assistente che risponde solo basandosi sui documenti forniti."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.3
                )
                return response.choices[0].message.content.strip()
            else:
                # Versione vecchia
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Sei un assistente che risponde solo basandosi sui documenti forniti."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.3
                )
                return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Errore generazione risposta: {e}")
            raise