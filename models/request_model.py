"""
📦 Pydantic Models for Request/Response Validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    """Input model for chat endpoint"""
    question: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Natural language question from admin",
        examples=["Show me all pothole complaints from last month"]
    )
    session_id: Optional[str] = Field(
        None,
        description="Optional session ID for tracking"
    )


class AnalyticsData(BaseModel):
    """Analytics visualization metadata"""
    chart_type: Optional[str] = Field(
        None,
        description="Type of chart: bar, line, pie, scatter, table"
    )
    plotly_config: Optional[Dict[str, Any]] = Field(
        None,
        description="Plotly chart configuration JSON"
    )
    data_summary: Optional[Dict[str, Any]] = Field(
        None,
        description="Statistical summary of results"
    )


class ChatResponse(BaseModel):
    """Output model for chat endpoint"""
    success: bool = Field(
        ...,
        description="Whether the request was successful"
    )
    question: str = Field(
        ...,
        description="Original question asked"
    )
    sql_generated: Optional[str] = Field(
        None,
        description="Generated SQL query"
    )
    data: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Query results as list of dictionaries"
    )
    analytics: Optional[AnalyticsData] = Field(
        None,
        description="Visualization and analytics metadata"
    )
    summary: Optional[str] = Field(
        None,
        description="Human-readable summary of results"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if success is False"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp"
    )
    execution_time_ms: Optional[float] = Field(
        None,
        description="Total execution time in milliseconds"
    )