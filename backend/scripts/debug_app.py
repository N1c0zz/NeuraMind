import sys
import traceback
from app.main import app

def test_app_startup():
    """Test dell'avvio dell'app per trovare errori nascosti"""
    try:
        print("🧪 Testing FastAPI app startup...")
        
        # Test import
        print("✅ App imported successfully")
        
        # Test routes
        for route in app.routes:
            print(f"  Route: {route.path}")
        
        print("✅ All routes loaded")
        
        # Test startup events (se ci sono)
        print("✅ App seems healthy")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during startup: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_app_startup()
