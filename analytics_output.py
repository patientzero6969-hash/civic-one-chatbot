"""
📊 Analytics and Visualization Generator
Auto-detects chart types and creates Plotly configs
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Generate analytics and visualizations from query results"""
    
    @staticmethod
    def generate_analytics(data: List[Dict[str, Any]], question: str = "") -> Dict[str, Any]:
        """
        Generate analytics with auto-detected chart type
        
        Args:
            data: Query results
            question: Original question for context
        
        Returns:
            Dictionary with chart_type, plotly_config, and data_summary
        """
        if not data or len(data) == 0:
            return {
                "chart_type": "none",
                "plotly_config": None,
                "data_summary": {"message": "No data returned"}
            }
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Detect best chart type
            chart_type, x_col, y_col = AnalyticsService._detect_chart_type(df, question)
            
            # Generate Plotly config
            plotly_config = AnalyticsService._generate_plotly_config(
                df, chart_type, x_col, y_col, question
            )
            
            # Generate summary statistics
            data_summary = AnalyticsService._generate_summary(df)
            
            return {
                "chart_type": chart_type,
                "plotly_config": plotly_config,
                "data_summary": data_summary
            }
            
        except Exception as e:
            logger.error(f"Error generating analytics: {str(e)}")
            return {
                "chart_type": "error",
                "plotly_config": None,
                "data_summary": {"error": str(e)}
            }
    
    @staticmethod
    def _detect_chart_type(df: pd.DataFrame, question: str) -> Tuple[str, Optional[str], Optional[str]]:
        """Auto-detect best chart type based on data structure"""
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        # Try to detect date columns from string columns
        for col in cat_cols[:]:
            try:
                pd.to_datetime(df[col].head(), errors='coerce')
                if df[col].head().notna().sum() > 0:
                    date_cols.append(col)
                    cat_cols.remove(col)
            except:
                pass
        
        # Time series (date + numeric)
        if len(date_cols) > 0 and len(num_cols) > 0:
            return "line", date_cols[0], num_cols[0]
        
        # Categorical + numeric (bar chart)
        if len(cat_cols) >= 1 and len(num_cols) >= 1:
            # Pie chart for distribution/breakdown questions
            if any(word in question.lower() for word in ["distribution", "breakdown", "percentage", "proportion"]):
                return "pie", cat_cols[0], num_cols[0]
            return "bar", cat_cols[0], num_cols[0]
        
        # Multiple numeric columns (scatter)
        if len(num_cols) >= 2:
            if any(word in question.lower() for word in ["correlation", "relationship", "vs", "versus"]):
                return "scatter", num_cols[0], num_cols[1]
            return "bar", num_cols[0], num_cols[1]
        
        # Default: table
        return "table", None, None
    
    @staticmethod
    def _generate_plotly_config(
        df: pd.DataFrame,
        chart_type: str,
        x_col: Optional[str],
        y_col: Optional[str],
        question: str
    ) -> Optional[Dict]:
        """Generate Plotly chart configuration"""
        
        if chart_type == "table" or not x_col:
            return None
        
        try:
            # Limit data for performance
            if len(df) > 100:
                df = df.head(100)
                logger.info("Data limited to 100 rows for visualization")
            
            # Generate chart based on type
            if chart_type == "bar":
                fig = px.bar(
                    df, 
                    x=x_col, 
                    y=y_col,
                    title=f"{y_col} by {x_col}",
                    labels={x_col: x_col.title(), y_col: y_col.title()}
                )
            
            elif chart_type == "line":
                fig = px.line(
                    df, 
                    x=x_col, 
                    y=y_col,
                    title=f"{y_col} over time",
                    labels={x_col: x_col.title(), y_col: y_col.title()}
                )
            
            elif chart_type == "pie":
                fig = px.pie(
                    df, 
                    names=x_col, 
                    values=y_col,
                    title=f"{y_col} Distribution"
                )
            
            elif chart_type == "scatter":
                fig = px.scatter(
                    df, 
                    x=x_col, 
                    y=y_col,
                    title=f"{y_col} vs {x_col}",
                    labels={x_col: x_col.title(), y_col: y_col.title()}
                )
            
            else:
                return None
            
            # Update layout for better appearance
            fig.update_layout(
                template="plotly_white",
                height=400,
                margin=dict(l=50, r=50, t=50, b=50)
            )
            
            # Convert to JSON-serializable dict
            return fig.to_dict()
            
        except Exception as e:
            logger.error(f"Error generating Plotly config: {str(e)}")
            return None
    
    @staticmethod
    def _generate_summary(df: pd.DataFrame) -> Dict[str, Any]:
        """Generate statistical summary"""
        summary = {
            "total_rows": len(df),
            "columns": list(df.columns),
            "column_types": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
        # Numeric statistics
        num_cols = df.select_dtypes(include=['number']).columns
        if len(num_cols) > 0:
            summary["numeric_stats"] = {}
            for col in num_cols:
                summary["numeric_stats"][col] = {
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "sum": float(df[col].sum())
                }
        
        # Categorical statistics
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(cat_cols) > 0:
            summary["categorical_stats"] = {}
            for col in cat_cols:
                unique_count = df[col].nunique()
                summary["categorical_stats"][col] = {
                    "unique_values": int(unique_count),
                    "most_common": str(df[col].mode()[0]) if len(df[col].mode()) > 0 else None
                }
        
        return summary
    
    @staticmethod
    def generate_text_summary(data: List[Dict[str, Any]], question: str) -> str:
        """Generate human-readable text summary"""
        if not data:
            return "No results found for your question."
        
        df = pd.DataFrame(data)
        num_rows = len(df)
        
        summary_parts = [f"Found {num_rows} result{'s' if num_rows != 1 else ''}."]
        
        # Add numeric insights
        num_cols = df.select_dtypes(include=['number']).columns
        for col in num_cols[:2]:
            total = df[col].sum()
            avg = df[col].mean()
            summary_parts.append(f"{col.title()}: Total={total:,.2f}, Average={avg:,.2f}")
        
        # Add categorical insights
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in cat_cols[:1]:
            top_value = df[col].mode()[0] if len(df[col].mode()) > 0 else "N/A"
            summary_parts.append(f"Most common {col}: {top_value}")
        
        return " ".join(summary_parts)


# Global instance
analytics_service = AnalyticsService()