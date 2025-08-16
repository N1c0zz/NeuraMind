import uvicorn
import socket

def check_port_available(host, port):
    """Check if port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return True
    except OSError:
        return False

def test_app_import():
    """Test app import"""
    try:
        from app.main import app
        print("✅ App imported successfully")
        return app
    except Exception as e:
        print(f"❌ Error importing app: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🚀 Starting NeuraMind server...")
    
    # Test app import
    app = test_app_import()
    if not app:
        print("❌ Cannot start server - app import failed")
        exit(1)
    
    # Check port
    if not check_port_available("127.0.0.1", 8000):
        print("❌ Port 8000 is already in use!")
        exit(1)
    
    print("✅ Port 8000 is available")
    print("Server will be available at: http://127.0.0.1:8000")
    print("Docs available at: http://127.0.0.1:8000/docs")
    print("Press Ctrl+C to stop")
    
    try:
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=8000, 
            reload=False,  # Disable reload to avoid issues
            log_level="debug"
        )
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        import traceback
        traceback.print_exc()
