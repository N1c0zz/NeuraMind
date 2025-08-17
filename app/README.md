# NeuraMind Mobile App

App mobile iOS/Android per l'assistente AI NeuraMind, creata con Expo React Native.

## 🚀 Funzionalità

- **Upload documenti**: Scatta foto o seleziona file per caricare documenti
- **OCR automatico**: Estrazione automatica del testo dalle immagini
- **Chat AI**: Chatta con i tuoi documenti utilizzando intelligenza artificiale
- **Ricerca semantica**: Trova informazioni nei tuoi documenti con ricerca intelligente
- **Multi-lingua**: Supporto OCR per italiano, inglese, francese, spagnolo, tedesco

## 📱 Schermate

- **Home**: Panoramica dell'app e accesso rapido alle funzioni
- **Upload**: Caricamento documenti con OCR
- **Chat**: Interfaccia chat per interagire con l'AI
- **Documenti**: Gestione e visualizzazione documenti caricati

## 🛠 Setup

### Prerequisiti

- Node.js 18+ 
- npm o yarn
- Expo CLI
- Backend NeuraMind deployato su Railway

### Installazione

1. **Clona il repository** (se non già fatto)
   ```bash
   git clone <repository-url>
   cd NeuraMind/app
   ```

2. **Installa dipendenze**
   ```bash
   npm install
   ```

3. **Configura environment**
   
   Modifica `src/utils/env.js` con i tuoi valori:
   ```javascript
   export const ENV = {
     API_BASE_URL: 'https://your-railway-app.railway.app',
     API_KEY: 'your-actual-api-key',
     USER_ID: 'mobile-user-001',
   };
   ```

4. **Avvia l'app**
   ```bash
   npx expo start
   ```

## 📦 Struttura del progetto

```
app/
├── src/
│   ├── components/          # Componenti riutilizzabili
│   ├── screens/            # Schermate dell'app
│   │   ├── HomeScreen.js
│   │   ├── ChatScreen.js
│   │   ├── UploadScreen.js
│   │   └── DocumentsScreen.js
│   ├── services/           # Servizi API
│   │   └── apiService.js
│   └── utils/             # Utilità e costanti
│       ├── constants.js
│       └── env.js
├── assets/                # Immagini e icone
├── App.js                # Componente principale
└── app.json              # Configurazione Expo
```

## 🔧 Configurazione Backend

L'app si connette al backend NeuraMind su Railway. Assicurati che:

1. Il backend sia deployato e funzionante
2. L'API key sia configurata correttamente
3. Gli endpoint siano accessibili dall'app mobile

### Endpoint utilizzati

- `GET /health` - Health check
- `POST /upload-document` - Upload documenti con OCR
- `POST /embed-upsert` - Embedding e storage
- `POST /query` - Ricerca semantica
- `POST /answer` - Generazione risposte AI

## 📱 Test su dispositivo

### iOS (con Expo Go)

1. Installa Expo Go dall'App Store
2. Avvia `npx expo start`
3. Scansiona il QR code con la fotocamera iOS

### Android (con Expo Go)

1. Installa Expo Go dal Google Play Store
2. Avvia `npx expo start`
3. Scansiona il QR code con Expo Go

### Simulatore iOS (solo macOS)

```bash
npm run ios
```

### Simulatore Android

```bash
npm run android
```

## 🏗 Build per produzione

### EAS Build (raccomandato)

1. Installa EAS CLI:
   ```bash
   npm install -g @expo/eas-cli
   ```

2. Configura EAS:
   ```bash
   eas build:configure
   ```

3. Build per iOS:
   ```bash
   eas build --platform ios
   ```

4. Build per Android:
   ```bash
   eas build --platform android
   ```

## 🎨 Personalizzazione

### Colori e tema

Modifica `src/utils/constants.js` per personalizzare i colori:

```javascript
export const COLORS = {
  primary: '#1a1a2e',
  secondary: '#16213e',
  accent: '#0f3460',
  // ...
};
```

### Configurazioni app

Modifica `app.json` per cambiare nome, icone, splash screen, ecc.

## 🐛 Troubleshooting

### Errori comuni

1. **Backend non raggiungibile**
   - Verifica che l'URL in `env.js` sia corretto
   - Controlla che il backend Railway sia attivo
   - Verifica l'API key

2. **Errori upload documenti**
   - Controlla i permessi camera/galleria
   - Verifica la dimensione del file (max 10MB)
   - Controlla la connessione internet

3. **Chat non funziona**
   - Assicurati di aver caricato almeno un documento
   - Verifica che l'embedding sia completato
   - Controlla i log del backend

### Debug mode

L'app include logging automatico in modalità sviluppo. Controlla la console per:
- Richieste API
- Errori di rete
- Stato delle chiamate

## 📋 TODO

- [ ] Autenticazione utenti
- [ ] Caching offline
- [ ] Push notifications
- [ ] Condivisione documenti
- [ ] Export chat history
- [ ] Tema scuro
- [ ] Supporto più formati file
- [ ] Backup automatico

## 🤝 Contribuire

1. Fork del progetto
2. Crea branch feature (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push branch (`git push origin feature/AmazingFeature`)
5. Apri Pull Request

## 📄 Licenza

Questo progetto è licenziato sotto la licenza MIT - vedi il file LICENSE per dettagli.

## 📞 Supporto

Per supporto, apri un issue su GitHub o contatta il team di sviluppo.

---

**NeuraMind** - Il tuo assistente AI personale per documenti 🧠📱
