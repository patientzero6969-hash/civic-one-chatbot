# app/model_service.py

"""
🤖 Groq API Integration WITH LangChain
Converts natural language to SQL using structured prompts
"""

import os
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
import logging
from groq import Groq

# --- REFINEMENT: Import from a central config file ---
# You will need to create app/config.py with the CATEGORY_MAPPING
from config import CATEGORY_MAPPING

logger = logging.getLogger(__name__)


class SQLOutputParser(BaseOutputParser):
    """Parse SQL output from LLM"""
    
    def parse(self, text: str) -> str:
        """Extract and clean SQL from LLM response"""
        # Remove markdown code blocks
        text = text.replace("```sql", "").replace("```", "")
        
        # Extract SELECT statement
        text = text.strip()
        if "SELECT" in text.upper():
            text = text[text.upper().find("SELECT"):]
        
        # --- REFINEMENT: Removed the part that adds a semicolon ---
        # The executor will handle sanitization before running.
        
        return text.strip()


class GroqService:
    """Service for Groq API integration"""
    
    def __init__(self):
        self.client = None
        self.model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        self.prompt_template = None
        self.output_parser = SQLOutputParser()
    
    def initialize(self):
        """Initialize Groq client and LangChain prompt"""
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key)
        
        # --- FIX: Use an f-string with escaped braces for the template ---
        # This resolves the KeyError on startup.
        valid_categories = ", ".join([f"'{cat}'" for cat in CATEGORY_MAPPING.values()])
        
        # The f"" formats valid_categories immediately.
        # The {{schema}} and {{question}} are escaped, so they become
        # {schema} and {question} in the final string for LangChain to use later.
        self.prompt_template = PromptTemplate(
            input_variables=["schema", "question"],
            template=f"""You are an expert PostgreSQL query generator for a civic complaints database.

Database Schema:
{{schema}}

Instructions:
- Generate ONLY a valid PostgreSQL SELECT query.
- When filtering by the 'category' column, you MUST use one of these exact values: {valid_categories}.
- Always refer to the timestamp column as 'created_at'.
- Return ONLY the SQL query itself without any explanations, markdown, or code blocks.

Question: {{question}}

SQL Query:"""
        )
        
        logger.info(f"Groq + LangChain initialized with model: {self.model}")
    
    def generate_sql(self, question: str, schema: str) -> str:
        """Generate SQL query using LangChain prompt template"""
        try:
            formatted_prompt = self.prompt_template.format(
                schema=schema,
                question=question
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": formatted_prompt}
                ],
                temperature=0.0, # Set to 0 for deterministic SQL generation
                max_tokens=500,
                top_p=1,
                stream=False
            )
            
            sql = response.choices[0].message.content.strip()
            sql = self.output_parser.parse(sql)
            
            logger.info(f"LangChain generated SQL: {sql}")
            return sql
            
        except Exception as e:
            logger.error(f"Error generating SQL with Groq: {str(e)}")
            raise
    
    def is_initialized(self) -> bool:
        """Check if Groq client is initialized"""
        return self.client is not None and self.prompt_template is not None


# Global instance
groq_service = GroqService()
