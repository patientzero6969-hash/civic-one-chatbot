# app/query_executor.py

"""
🗄️ Supabase Query Executor
Executes SQL queries securely on Supabase
"""

import os
from supabase import create_client, Client
import logging
import re # <-- FIX: Import regular expressions
from typing import List, Dict, Any

# --- REFINEMENT: Import from a central config file ---
# You will need to create app/config.py with the ALLOWED_CATEGORIES
from config import ALLOWED_CATEGORIES

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Service for Supabase database operations"""
    
    DANGEROUS_KEYWORDS = [
        "DROP", "DELETE", "TRUNCATE", "INSERT", "UPDATE",
        "ALTER", "CREATE", "GRANT", "REVOKE", "EXEC",
        "EXECUTE", "PROCEDURE", "FUNCTION"
    ]
    
    def __init__(self):
        self.client: Client = None
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
    
    def initialize(self):
        """Initialize Supabase client"""
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment")
        
        self.client = create_client(self.url, self.key)
        logger.info(f"Supabase client initialized: {self.url}")
    
    def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """Execute a validated SQL query on Supabase via RPC."""
        self._validate_sql(sql)
        
        # --- FIX: Sanitize SQL by removing trailing semicolon for the RPC call ---
        sanitized_sql = sql.strip().rstrip(';')

        try:
            # Note: You need to create this 'execute_sql' function in Supabase
            result = self.client.rpc('execute_sql', {'query': sanitized_sql}).execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error(f"Supabase RPC error: {result.error}")
                raise Exception(f"Database query failed: {result.error.message}")

            return result.data if hasattr(result, 'data') else []
            
        except Exception as e:
            logger.error(f"Query execution error: {str(e)}")
            raise # Re-raise the exception to be handled by the endpoint

    def _validate_sql(self, sql: str):
        """Validates the SQL query to ensure it is a safe, read-only SELECT statement."""
        sql_clean = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        sql_clean = re.sub(r'/\*.*?\*/', '', sql_clean, flags=re.DOTALL)
        
        # --- FIX: Use regex with word boundaries for keyword checking ---
        sql_upper = sql_clean.upper()
        for keyword in self.DANGEROUS_KEYWORDS:
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, sql_upper):
                raise ValueError(
                    f"Query contains forbidden keyword: {keyword}. Only SELECT queries are allowed."
                )
        
        if not sql_clean.strip().upper().startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed")
        
        # Validate categories used in the query
        category_match = re.findall(r"category\s*=\s*'([^']+)'", sql_clean, flags=re.IGNORECASE)
        if category_match:
            for cat in category_match:
                if cat not in ALLOWED_CATEGORIES:
                    raise ValueError(f"Query uses a category that is not allowed: {cat}")
    
    def get_schema(self) -> str:
        # This function seems complex and might be simplified, but is left as is for now.
        # It's better to define the schema manually or have a more reliable fetch method.
        # ... (your existing get_schema and _format_schema logic) ...
        return """
        Table: issue_analytics
        Columns:
         - id (uuid)
         - title (text)
         - description (text)
         - category (text)
         - status (text)
         - created_at (timestamp with time zone)
         - updated_at (timestamp with time zone)
         - latitude (double precision)
         - longitude (double precision)
        """
    
    def is_initialized(self) -> bool:
        """Check if Supabase client is initialized"""
        return self.client is not None

# Global instance
supabase_client = SupabaseClient()