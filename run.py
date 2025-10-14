"""
🚀 CrowCivic Insight Bot - Startup Script
"""

import uvicorn
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ['PYTHONPATH'] = project_root

def main():
    """Run the FastAPI application"""
    print("=" * 60)
    print("🚀 Starting CrowCivic Insight Bot Backend")
    print("=" * 60)
    print(f"📊 Model: {os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')} (via Groq)")
    print(f"🗄️  Database: {os.getenv('SUPABASE_URL', 'Not configured')}")
    print(f"🔌 Port: {os.getenv('API_PORT', 8000)}")
    print("=" * 60)
    print("\n💡 Access the API at:")
    print(f"   • Main: http://localhost:{os.getenv('API_PORT', 8000)}")
    print(f"   • Docs: http://localhost:{os.getenv('API_PORT', 8000)}/docs")
    print(f"   • Health: http://localhost:{os.getenv('API_PORT', 8000)}/api/v1/health")
    print("\n🛑 Press CTRL+C to stop\n")
    
    # Run uvicorn with correct PYTHONPATH
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True,
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        reload_dirs=[project_root]
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting application: {str(e)}")
        sys.exit(1)