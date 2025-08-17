// Environment configuration
// Crea un file .env nella root del progetto per le variabili di ambiente reali

// Environment configuration
// Le variabili sono caricate dal file .env

export const ENV = {
  // URL del backend Railway
  API_BASE_URL: process.env.EXPO_PUBLIC_API_BASE_URL || 'https://neuramind-production.up.railway.app/v1',
  
  // API Key del backend
  API_KEY: process.env.EXPO_PUBLIC_API_KEY || 'super-secret-for-local',
  
  // User ID per il demo
  USER_ID: process.env.EXPO_PUBLIC_USER_ID || 'mobile-user-001',
  
  // Configurazioni Expo
  EXPO_CLIENT_ID: '',
  
  // Debug mode
  DEBUG: __DEV__ || process.env.EXPO_PUBLIC_DEBUG === 'true',
};

// Valida le configurazioni necessarie
export const validateConfig = () => {
  const missingConfigs = [];
  
  if (!ENV.API_BASE_URL || ENV.API_BASE_URL.includes('your-railway-app')) {
    missingConfigs.push('API_BASE_URL');
  }
  
  if (!ENV.API_KEY || ENV.API_KEY === 'your-api-key-here') {
    missingConfigs.push('API_KEY');
  }
  
  if (missingConfigs.length > 0) {
    console.warn('⚠️ Missing configurations:', missingConfigs.join(', '));
    console.warn('Update src/utils/env.js with your actual values');
  }
  
  return missingConfigs.length === 0;
};
