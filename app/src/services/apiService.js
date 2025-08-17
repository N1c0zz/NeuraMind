import axios from 'axios';
import { ENV, validateConfig } from '../utils/env';

// Valida configurazione all'avvio
validateConfig();

class ApiService {
  constructor() {
    console.log('🔧 Initializing ApiService with:', {
      baseURL: ENV.API_BASE_URL,
      apiKey: ENV.API_KEY ? 'SET' : 'MISSING'
    });
    
    this.api = axios.create({
      baseURL: ENV.API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': ENV.API_KEY,
      },
      timeout: 30000, // 30 secondi timeout
    });

    // Interceptor per logging in debug mode
    if (ENV.DEBUG) {
      this.api.interceptors.request.use(request => {
        console.log('🚀 API Request:', request.method?.toUpperCase(), request.url);
        console.log('🚀 Headers:', request.headers);
        console.log('🚀 Full URL:', request.baseURL + request.url);
        return request;
      });

      this.api.interceptors.response.use(
        response => {
          console.log('✅ API Response:', response.status, response.config.url);
          return response;
        },
        error => {
          console.error('❌ API Error:', error.response?.status, error.config?.url, error.message);
          console.error('❌ Error response data:', error.response?.data);
          return Promise.reject(error);
        }
      );
    }
  }

  // Health check
  async healthCheck() {
    try {
      console.log('🏥 Testing health endpoint...');
      console.log('🏥 Base URL:', ENV.API_BASE_URL);
      console.log('🏥 API Key:', ENV.API_KEY);
      
      const response = await this.api.get('/health');
      console.log('🏥 Health response:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Health check failed:', error);
      console.error('❌ Health error details:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        url: error.config?.url,
        baseURL: error.config?.baseURL,
      });
      throw error;
    }
  }

  // Upload documento con OCR
  async uploadDocument(fileUri, title, userId, language = 'ita+eng') {
    try {
      console.log('📤 Upload starting with:', { fileUri, title, userId, language });
      
      const formData = new FormData();
      
      // Aggiungi il file con il formato corretto per React Native
      formData.append('file', {
        uri: fileUri,
        type: 'image/jpeg',
        name: 'document.jpg',
      });
      
      formData.append('title', title);
      formData.append('user_id', userId);
      formData.append('language', language);

      console.log('📤 FormData prepared, sending request...');

      const response = await this.api.post('/upload-document', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'X-API-Key': ENV.API_KEY, // Assicuriamoci che l'API key sia inclusa
        },
        timeout: 60000, // 60 secondi per upload
      });
      
      console.log('✅ Upload successful:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Upload document failed:', error);
      console.error('❌ Error details:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        config: {
          url: error.config?.url,
          method: error.config?.method,
          headers: error.config?.headers,
        }
      });
      throw error;
    }
  }

  // Embedding e upsert testo
  async embedUpsert(userId, itemId, title, text) {
    try {
      const response = await this.api.post('/embed-upsert', {
        user_id: userId,
        item_id: itemId,
        title: title,
        text: text,
      });
      return response.data;
    } catch (error) {
      console.error('Embed upsert failed:', error);
      throw error;
    }
  }

  // Query semantica
  async query(userId, query, topK = 5) {
    try {
      console.log('🔍 Query starting:', { userId, query, topK });
      console.log('🔍 Full URL will be:', ENV.API_BASE_URL + '/query');
      
      const response = await this.api.post('/query', {
        user_id: userId,
        query: query,
        top_k: topK,
      });
      
      console.log('🔍 Query successful:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Query failed:', error);
      console.error('❌ Query error details:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        url: error.config?.url,
        fullURL: error.config?.baseURL + error.config?.url,
      });
      throw error;
    }
  }

  // Genera risposta dal contesto
  async generateAnswer(query, contexts) {
    try {
      console.log('💡 Generate answer starting:', { query, contextsCount: contexts.length });
      console.log('💡 Contexts preview:', contexts.slice(0, 2)); // Prime 2 per debug
      
      const response = await this.api.post('/answer', {
        query: query,
        contexts: contexts,
      });
      
      console.log('💡 Answer generated successfully:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Generate answer failed:', error);
      console.error('❌ Request payload was:', { query, contexts });
      throw error;
    }
  }

  // Lista documenti
  async listDocuments(userId) {
    try {
      console.log('📁 Loading documents for user:', userId);
      
      const response = await this.api.get(`/documents/${userId}`);
      
      console.log('📁 Documents loaded successfully:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ List documents failed:', error);
      console.error('❌ Error details:', {
        status: error.response?.status,
        data: error.response?.data,
      });
      throw error;
    }
  }

  // Elimina documento
  async deleteDocument(userId, itemId) {
    try {
      console.log('🗑️ Deleting document:', { userId, itemId });
      
      const response = await this.api.delete(`/documents/${userId}/${itemId}`);
      
      console.log('🗑️ Document deleted successfully:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Delete document failed:', error);
      throw error;
    }
  }

  // Pipeline completa: query + answer
  async askQuestion(userId, question, topK = 5) {
    try {
      console.log('🤔 Ask question starting:', { userId, question, topK });
      
      // 1. Ricerca semantica
      const queryResponse = await this.query(userId, question, topK);
      console.log('🔍 Query response:', queryResponse);
      
      // 2. Estrai i contesti - FIX: usa la struttura corretta
      const contexts = queryResponse.matches.map(match => ({
        text: match.metadata?.chunk_text || match.metadata?.text || '',
        title: match.metadata?.title || 'Documento senza titolo',
        score: match.score || 0,
      }));
      
      console.log('📝 Extracted contexts:', contexts);
      
      // 3. Genera risposta
      const answerResponse = await this.generateAnswer(question, contexts);
      console.log('💡 Answer response:', answerResponse);
      
      return {
        answer: answerResponse.answer,
        sources: queryResponse.matches,
      };
    } catch (error) {
      console.error('❌ Ask question failed:', error);
      console.error('❌ Full error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
      });
      throw error;
    }
  }
}

export default new ApiService();
