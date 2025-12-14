import uvicorn
import os
from main_simple import app

if __name__ == "__main__":
    # Get port from environment variable or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    print(f"Starting backend server on port {port}")
    print("Backend API endpoints will be available at:")
    print(f"  - http://localhost:{port}/")
    print(f"  - http://localhost:{port}/docs (API documentation)")
    
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        reload_dirs=["./"],
        reload_includes=["*.py"]
    )