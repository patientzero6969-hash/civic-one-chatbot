# app/chatbot.py

"""
💬 Chatbot API Endpoint
Main /chat endpoint that orchestrates everything
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter
import logging
import time

from models.request_model import ChatRequest, ChatResponse, AnalyticsData
from model_service import groq_service
from query_executor import supabase_client
from analytics_output import analytics_service

# --- REFINEMENT: Import from utility files ---
# You will need to create app/utils.py
from utils import convert_numpy_to_python

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chatbot endpoint"""
    start_time = time.time()
    sql_query = "" # Initialize to ensure it's available in error responses
    try:
        logger.info(f"📝 Question: {request.question}")
        
        schema = supabase_client.get_schema()
        logger.info("📋 Schema retrieved")
        
        sql_query = groq_service.generate_sql(
            question=request.question,
            schema=schema
        )
        logger.info(f"🤖 Generated SQL: {sql_query}")
        
        # --- REFINEMENT: Removed the manual string.replace() loop ---
        # The improved prompt in model_service.py handles this now.

        data = supabase_client.execute_query(sql_query)
        logger.info(f"✅ Query executed: {len(data)} rows")
        
        analytics_data_numpy = analytics_service.generate_analytics(
            data=data,
            question=request.question
        )
        
        summary = analytics_service.generate_text_summary(
            data=data,
            question=request.question
        )
        
        # --- FIX: Convert all numpy types to native Python types before responding ---
        final_data = convert_numpy_to_python(data)
        final_analytics = convert_numpy_to_python(analytics_data_numpy)
        
        execution_time = (time.time() - start_time) * 1000
        logger.info(f"✅ Response generated in {execution_time:.2f}ms")
        
        return ChatResponse(
            success=True,
            question=request.question,
            sql_generated=sql_query,
            data=final_data,
            analytics=AnalyticsData(**final_analytics) if final_analytics else None,
            summary=summary,
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing request for question '{request.question}': {str(e)}", exc_info=True)
        execution_time = (time.time() - start_time) * 1000
        
        # Determine error type for a more specific message
        error_message = str(e)
        if isinstance(e, ValueError): # Catches security validation errors
             error_message = f"Security validation failed: {str(e)}"
        else:
             error_message = f"An internal error occurred: {str(e)}"

        return ChatResponse(
            success=False,
            question=request.question,
            sql_generated=sql_query,
            error=error_message,
            execution_time_ms=execution_time
        )

# ... (your other endpoints like /schema and /test can remain the same) ...