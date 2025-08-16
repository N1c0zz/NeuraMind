import requests
import sys

def simple_health_test():
    """Test semplicissimo per verificare che il server sia attivo"""
    try:
        print("🔍 Testing server connection...")
        response = requests.get("http://127.0.0.1:8000/v1/health", timeout=5)
        print(f"✅ Server response: {response.status_code}")
        print(f"✅ Response data: {response.json()}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Server non raggiungibile. È avviato su porta 8000?")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout - il server è troppo lento")
        return False
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False

def test_config():
    """Test per verificare che le configurazioni siano OK"""
    try:
        import os
        from dotenv import load_dotenv
        
        # Carica .env se esiste
        env_path = os.path.join('..', '.env') if os.path.exists(os.path.join('..', '.env')) else '.env'
        if os.path.exists(env_path):
            load_dotenv(env_path)
            print("✅ File .env trovato e caricato")
        else:
            print("⚠️ File .env non trovato")
        
        # Verifica variabili critiche
        openai_key = os.getenv('OPENAI_API_KEY', '')
        pinecone_key = os.getenv('PINECONE_API_KEY', '')
        
        print(f"OpenAI API Key: {'✅ Configurata' if openai_key else '❌ Mancante'}")
        print(f"Pinecone API Key: {'✅ Configurata' if pinecone_key else '❌ Mancante'}")
        
        return bool(openai_key and pinecone_key)
        
    except ImportError:
        print("⚠️ python-dotenv non installato (opzionale)")
        return True
    except Exception as e:
        print(f"❌ Errore nel test config: {e}")
        return False

if __name__ == "__main__":
    print("🧪 NeuraMind - Test Semplice")
    print("=" * 40)
    
    # Test configurazione
    print("1. Test configurazione...")
    config_ok = test_config()
    print()
    
    # Test connessione server
    print("2. Test connessione server...")
    server_ok = simple_health_test()
    print()
    
    if server_ok:
        print("🎉 Server funzionante! Puoi procedere con test più avanzati.")
    else:
        print("🔧 Riavvia il server con: python -m uvicorn app.main:app --reload")
        
    if not config_ok:
        print("⚠️ Configura le API keys nel file .env prima dei test completi")
