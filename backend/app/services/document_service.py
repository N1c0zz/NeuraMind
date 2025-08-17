import logging
from typing import List, Dict, Optional
from datetime import datetime
from app.services.pinecone_client import PineconeService

logger = logging.getLogger(__name__)

class DocumentService:
    """Servizio per gestione documenti utente"""
    
    def __init__(self):
        self.pinecone_service = PineconeService()
        self.max_documents = 10
    
    def get_user_documents(self, user_id: str) -> List[Dict]:
        """
        Recupera tutti i documenti di un utente da Pinecone metadata
        """
        try:
            # Query Pinecone per tutti i documenti dell'utente
            # Utilizziamo una query con filtro per ottenere i metadati
            filter_dict = {"user_id": user_id}
            
            # Facciamo una query dummy per ottenere tutti i chunk dell'utente
            dummy_vector = [0.0] * 1536  # Vector size per OpenAI embeddings
            
            results = self.pinecone_service.query_vectors(
                query_vector=dummy_vector,
                top_k=1000,  # Alto numero per prendere tutti i chunk
                filter_dict=filter_dict,
                include_metadata=True
            )
            
            # Raggruppa i chunk per documento
            documents_map = {}
            
            for match in results:
                metadata = match.get('metadata', {})
                item_id = metadata.get('item_id')
                
                if item_id and item_id not in documents_map:
                    documents_map[item_id] = {
                        'item_id': item_id,
                        'title': metadata.get('title', 'Documento senza titolo'),
                        'user_id': metadata.get('user_id'),
                        'created_at': metadata.get('timestamp', ''),
                        'upload_date': metadata.get('timestamp', ''),
                        'text_length': len(metadata.get('chunk_text', '')),
                        'chunks_count': 1,
                        'ocr_confidence': metadata.get('ocr_confidence'),
                        'text_preview': metadata.get('chunk_text', '')[:200] + '...',
                        'file_type': metadata.get('file_type', 'Sconosciuto')
                    }
                elif item_id:
                    # Aggiorna conteggio chunk e lunghezza testo
                    documents_map[item_id]['chunks_count'] += 1
                    chunk_text = metadata.get('chunk_text', '')
                    documents_map[item_id]['text_length'] += len(chunk_text)
            
            # Converti in lista e ordina per data
            documents_list = list(documents_map.values())
            documents_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            logger.info(f"Trovati {len(documents_list)} documenti per utente {user_id}")
            return documents_list
            
        except Exception as e:
            logger.error(f"Errore nel recupero documenti per {user_id}: {e}")
            return []
    
    def count_user_documents(self, user_id: str) -> int:
        """Conta i documenti di un utente"""
        try:
            documents = self.get_user_documents(user_id)
            return len(documents)
        except Exception as e:
            logger.error(f"Errore nel conteggio documenti per {user_id}: {e}")
            return 0
    
    def can_upload_document(self, user_id: str) -> bool:
        """Verifica se l'utente può caricare un nuovo documento"""
        try:
            count = self.count_user_documents(user_id)
            return count < self.max_documents
        except Exception as e:
            logger.error(f"Errore nel controllo limite documenti per {user_id}: {e}")
            return False
    
    def delete_oldest_document(self, user_id: str) -> bool:
        """Elimina il documento più vecchio dell'utente"""
        try:
            documents = self.get_user_documents(user_id)
            if not documents:
                return True
            
            # Trova il documento più vecchio
            oldest_doc = min(documents, key=lambda x: x.get('created_at', ''))
            oldest_item_id = oldest_doc['item_id']
            
            # Elimina tutti i chunk di questo documento da Pinecone
            filter_dict = {
                "user_id": user_id,
                "item_id": oldest_item_id
            }
            
            # Per eliminare da Pinecone, dobbiamo prima trovare tutti gli ID dei chunk
            dummy_vector = [0.0] * 1536
            results = self.pinecone_service.query_vectors(
                query_vector=dummy_vector,
                top_k=1000,
                filter_dict=filter_dict,
                include_metadata=True
            )
            
            # Raccogli tutti gli ID dei chunk da eliminare
            chunk_ids = [match['id'] for match in results]
            
            if chunk_ids:
                # Elimina i chunk da Pinecone
                self.pinecone_service.delete_vectors(chunk_ids)
                logger.info(f"Eliminato documento {oldest_item_id} con {len(chunk_ids)} chunk")
            
            return True
            
        except Exception as e:
            logger.error(f"Errore nell'eliminazione del documento più vecchio per {user_id}: {e}")
            return False
    
    def delete_document(self, user_id: str, item_id: str) -> bool:
        """Elimina un documento specifico"""
        try:
            filter_dict = {
                "user_id": user_id,
                "item_id": item_id
            }
            
            # Trova tutti i chunk del documento
            dummy_vector = [0.0] * 1536
            results = self.pinecone_service.query_vectors(
                query_vector=dummy_vector,
                top_k=1000,
                filter_dict=filter_dict,
                include_metadata=True
            )
            
            chunk_ids = [match['id'] for match in results]
            
            if chunk_ids:
                self.pinecone_service.delete_vectors(chunk_ids)
                logger.info(f"Eliminato documento {item_id} con {len(chunk_ids)} chunk")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Errore nell'eliminazione documento {item_id} per {user_id}: {e}")
            return False

# Istanza globale
document_service = DocumentService()
