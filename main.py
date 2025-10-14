"""
🚀 CrowCivic Insight Bot - FastAPI Main Application
Groq + LangChain + Supabase Integration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    
    logger.info("=" * 60)
    logger.info("🚀 Starting CrowCivic Insight Bot")
    logger.info("=" * 60)
    
    # Initialize Groq client
    from model_service import groq_service
    try:
        groq_service.initialize()
        logger.info("✅ Groq API connected!")
    except Exception as e:
        logger.error(f"❌ Groq initialization failed: {str(e)}")
        raise
    
    # Initialize Supabase connection
    from query_executor import supabase_client
    try:
        supabase_client.initialize()
        logger.info("✅ Supabase connected!")
    except Exception as e:
        logger.error(f"❌ Supabase initialization failed: {str(e)}")
        raise
    
    logger.info("=" * 60)
    logger.info(f"🎉 Ready! Visit http://localhost:{os.getenv('API_PORT', 8000)}/docs")
    logger.info("=" * 60)
    
    yield
    
    # Cleanup on shutdown
    logger.info("👋 Shutting down CrowCivic Insight Bot...")


# Create FastAPI app
app = FastAPI(
    title="CrowCivic Insight Bot",
    description="AI-powered chatbot for civic data analytics using Groq + Supabase",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
from chatbot import router as chatbot_router
app.include_router(chatbot_router, prefix="/api/v1", tags=["Chatbot"])


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "🤖 CrowCivic Insight Bot API",
        "version": "1.0.0",
        "tech_stack": {
            "backend": "FastAPI",
            "ai": "Groq (Llama 3.1 8B)",
            "database": "Supabase",
            "analytics": "Plotly"
        },
        "docs": "/docs",
        "endpoints": {
            "chat": "POST /api/v1/chat",
            "health": "GET /api/v1/health",
            "schema": "GET /api/v1/schema"
        }
    }


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    from model_service import groq_service
    from query_executor import supabase_client
    
    return {
        "status": "healthy",
        "groq": "connected" if groq_service.is_initialized() else "disconnected",
        "supabase": "connected" if supabase_client.is_initialized() else "disconnected",
        "model": os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000))
    )