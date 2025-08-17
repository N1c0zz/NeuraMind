import { ENV } from './env';

// Colori tema NeuraMind
export const COLORS = {
  primary: '#1a1a2e',
  secondary: '#16213e',
  accent: '#0f3460',
  background: '#f5f5f5',
  surface: '#ffffff',
  text: '#333333',
  textLight: '#666666',
  success: '#4caf50',
  warning: '#ff9800',
  error: '#f44336',
  blue: '#2196f3',
  purple: '#9c27b0',
};

// Dimensioni
export const SIZES = {
  padding: 16,
  margin: 8,
  borderRadius: 12,
  headerHeight: 60,
  tabBarHeight: 80,
};

// Configurazioni (ora importate da env.js)
export const CONFIG = {
  API_BASE_URL: ENV.API_BASE_URL,
  API_KEY: ENV.API_KEY,
  USER_ID: ENV.USER_ID,
  
  // Massimo file size (10MB)
  MAX_FILE_SIZE: 10 * 1024 * 1024,
  
  // Lingue supportate per OCR
  OCR_LANGUAGES: [
    { label: 'Italiano + Inglese', value: 'ita+eng' },
    { label: 'Solo Italiano', value: 'ita' },
    { label: 'Solo Inglese', value: 'eng' },
    { label: 'Francese', value: 'fra' },
    { label: 'Spagnolo', value: 'spa' },
    { label: 'Tedesco', value: 'deu' },
  ],
};

// Messaggi
export const MESSAGES = {
  upload: {
    success: 'Documento caricato con successo!',
    error: 'Errore durante il caricamento del documento',
    processing: 'Elaborazione in corso...',
  },
  query: {
    error: 'Errore durante la ricerca',
    noResults: 'Nessun risultato trovato',
    thinking: 'Sto pensando...',
  },
  camera: {
    permission: 'Permesso camera necessario per scattare foto',
    error: 'Errore durante l\'acquisizione dell\'immagine',
  },
  documents: {
    empty: 'Nessun documento caricato',
    error: 'Errore durante il caricamento dei documenti',
  },
};
