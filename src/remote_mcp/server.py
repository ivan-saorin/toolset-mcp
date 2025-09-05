#!/usr/bin/env python3
"""
Atlas Toolset MCP Server v3 - Modular architecture with enhanced features
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
import uvicorn

# Import features
from .features import (
    CalculatorEngine,
    TextAnalyzerEngine,
    TaskManagerEngine,
    TimeEngine
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("atlas-toolset")

# Initialize MCP server
mcp = FastMCP("Atlas Toolset MCP")
mcp.description = "Enhanced utility toolset with calculator, text analysis, task management, and time features"

# Initialize feature engines
calculator = CalculatorEngine()
text_analyzer = TextAnalyzerEngine()
task_manager = TaskManagerEngine()
time_engine = TimeEngine()

# ============================================================================
# SYSTEM INFO
# ============================================================================

@mcp.tool()
async def system_info() -> Dict[str, Any]:
    """Get system information and server status"""
    return {
        "server_name": "Atlas Toolset MCP",
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat(),
        "transport": "streamable-http",
        "features": {
            "calculator": {
                "version": calculator.version,
                "capabilities": ["basic", "scientific", "statistical", "financial"]
            },
            "text_analyzer": {
                "version": text_analyzer.version,
                "modes": ["basic", "detailed", "readability", "sentiment", "keywords"]
            },
            "task_manager": {
                "version": task_manager.version,
                "capabilities": ["priorities", "categories", "dependencies", "time_tracking"]
            },
            "time": {
                "version": time_engine.version,
                "formats": ["italian", "iso", "us"],
                "shortcuts": ["now", "yesterday", "tomorrow", "EoD", "EoM", "last_month", "next_month"]
            }
        }
    }

# ============================================================================
# CALCULATOR TOOLS
# ============================================================================

@mcp.tool()
async def calculate(
    a: float,
    b: Optional[float] = None,
    operation: str = "add"
) -> Dict[str, Any]:
    """
    Perform mathematical calculations
    
    Args:
        a: First number or list of numbers
        b: Second number (optional for some operations)
        operation: Operation (add, subtract, multiply, divide, power, modulo, sqrt, factorial, percentage, average)
    """
    response = calculator.calculate(a, b, operation)
    return response.to_dict()

@mcp.tool()
async def calculate_advanced(
    expression: str,
    variables: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Evaluate mathematical expressions safely
    
    Args:
        expression: Mathematical expression (e.g., "2 * pi * r")
        variables: Optional dictionary of variables
    """
    response = calculator.calculate_advanced(expression, variables)
    return response.to_dict()

@mcp.tool()
async def calculate_statistics(
    data: List[float],
    operations: List[str]
) -> Dict[str, Any]:
    """
    Perform statistical calculations on data
    
    Args:
        data: List of numbers
        operations: Operations to perform (mean, median, mode, stdev, variance, sum, min, max, range)
    """
    response = calculator.calculate_statistics(data, operations)
    return response.to_dict()

@mcp.tool()
async def calculate_financial(
    calc_type: str,
    params: Dict[str, float]
) -> Dict[str, Any]:
    """
    Perform financial calculations
    
    Args:
        calc_type: Type of calculation (compound_interest, loan_payment, roi, present_value)
        params: Parameters specific to calculation type
    """
    response = calculator.calculate_financial(calc_type, params)
    return response.to_dict()

# ============================================================================
# TEXT ANALYZER TOOLS
# ============================================================================

@mcp.tool()
async def text_analyze(
    text: str,
    mode: str = "basic"
) -> Dict[str, Any]:
    """
    Analyze text with various metrics
    
    Args:
        text: Text to analyze
        mode: Analysis mode (basic, detailed, readability, sentiment, keywords)
    """
    response = text_analyzer.text_analyze(text, mode)
    return response.to_dict()

@mcp.tool()
async def text_compare(
    text1: str,
    text2: str
) -> Dict[str, Any]:
    """
    Compare two texts for similarity and differences
    
    Args:
        text1: First text
        text2: Second text
    """
    response = text_analyzer.text_compare(text1, text2)
    return response.to_dict()

@mcp.tool()
async def text_extract(
    text: str,
    extract_type: str
) -> Dict[str, Any]:
    """
    Extract specific information from text
    
    Args:
        text: Source text
        extract_type: Type of extraction (urls, emails, numbers, dates, hashtags, mentions)
    """
    response = text_analyzer.text_extract(text, extract_type)
    return response.to_dict()

@mcp.tool()
async def text_transform(
    text: str,
    transformation: str
) -> Dict[str, Any]:
    """
    Transform text in various ways
    
    Args:
        text: Text to transform
        transformation: Transformation type (uppercase, lowercase, title, reverse, remove_punctuation, remove_spaces, snake_case, camel_case)
    """
    response = text_analyzer.text_transform(text, transformation)
    return response.to_dict()

# ============================================================================
# TASK MANAGER TOOLS
# ============================================================================

@mcp.tool()
async def task_create(
    title: str,
    description: str = "",
    priority: str = "medium",
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    due_date: Optional[str] = None,
    estimated_hours: Optional[float] = None
) -> Dict[str, Any]:
    """
    Create a new task with advanced options
    
    Args:
        title: Task title
        description: Task description
        priority: Priority (low, medium, high, urgent, critical)
        category: Task category
        tags: List of tags
        due_date: Due date (ISO format)
        estimated_hours: Estimated hours to complete
    """
    response = task_manager.task_create(
        title, description, priority, category, 
        tags, due_date, estimated_hours
    )
    return response.to_dict()

@mcp.tool()
async def task_list(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    overdue: bool = False
) -> Dict[str, Any]:
    """
    List tasks with filtering
    
    Args:
        status: Filter by status (pending, in_progress, blocked, review, completed, cancelled, archived)
        priority: Filter by priority
        category: Filter by category
        overdue: Show only overdue tasks
    """
    response = task_manager.task_list(status, priority, category, None, overdue)
    return response.to_dict()

@mcp.tool()
async def task_update(
    task_id: str,
    updates: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update a task
    
    Args:
        task_id: Task ID to update
        updates: Dictionary of fields to update
    """
    response = task_manager.task_update(task_id, updates)
    return response.to_dict()

@mcp.tool()
async def task_delete(
    task_id: str
) -> Dict[str, Any]:
    """
    Delete a task
    
    Args:
        task_id: Task ID to delete
    """
    response = task_manager.task_delete(task_id)
    return response.to_dict()

@mcp.tool()
async def task_complete(
    task_id: str,
    completion_notes: Optional[str] = None,
    actual_hours: Optional[float] = None
) -> Dict[str, Any]:
    """
    Mark a task as complete
    
    Args:
        task_id: Task ID to complete
        completion_notes: Optional completion notes
        actual_hours: Actual hours taken
    """
    response = task_manager.task_complete(task_id, completion_notes, actual_hours)
    return response.to_dict()

@mcp.tool()
async def task_stats() -> Dict[str, Any]:
    """Get comprehensive task statistics"""
    response = task_manager.task_stats()
    return response.to_dict()

# ============================================================================
# TIME TOOLS
# ============================================================================

@mcp.tool()
async def time_now(
    format: str = "italian",
    timezone: int = 0
) -> Dict[str, Any]:
    """
    Get current date and time
    
    Args:
        format: Output format (italian, iso, us, timestamp, full_italian)
        timezone: Timezone offset in hours
    """
    response = time_engine.time_now(format, timezone)
    return response.to_dict()

@mcp.tool()
async def time_parse(
    shortcut: str,
    format: str = "italian"
) -> Dict[str, Any]:
    """
    Parse date shortcuts
    
    Examples:
        - 'now': Current datetime
        - 'yesterday': Yesterday at same time
        - 'tomorrow': Tomorrow at same time
        - 'EoD': End of Day (23:59:59)
        - 'EoM': End of Month
        - 'tomorrow EoD': Tomorrow at 23:59:59
        - 'next month EoM': Last day of next month
    
    Args:
        shortcut: Date shortcut to parse
        format: Output format
    """
    response = time_engine.time_parse(shortcut, format)
    return response.to_dict()

@mcp.tool()
async def time_calculate(
    date1: str,
    date2: str,
    unit: str = "days"
) -> Dict[str, Any]:
    """
    Calculate difference between two dates with detailed statistics
    
    Args:
        date1: First date (ISO format or shortcut)
        date2: Second date (ISO format or shortcut)
        unit: Result unit (seconds, minutes, hours, days, weeks, months, years)
    """
    response = time_engine.time_calculate(date1, date2, unit)
    return response.to_dict()

@mcp.tool()
async def time_add(
    base_date: str,
    amount: float,
    unit: str = "days",
    format: str = "italian"
) -> Dict[str, Any]:
    """
    Add or subtract time from a date
    
    Args:
        base_date: Base date (ISO format or shortcut)
        amount: Amount to add (negative to subtract)
        unit: Unit (seconds, minutes, hours, days, weeks, months, years)
        format: Output format
    """
    response = time_engine.time_add(base_date, amount, unit, format)
    return response.to_dict()

@mcp.tool()
async def time_format(
    date_input: str,
    input_format: str = "auto",
    output_format: str = "italian"
) -> Dict[str, Any]:
    """
    Convert between date formats
    
    Args:
        date_input: Date to format
        input_format: Input format (auto-detect if 'auto')
        output_format: Output format (italian, iso, us, timestamp, full_italian)
    """
    response = time_engine.time_format(date_input, input_format, output_format)
    return response.to_dict()

# ============================================================================
# ASGI APPLICATION WITH HEALTH CHECK
# ============================================================================

async def health_check(request):
    """Health check endpoint for CapRover"""
    return JSONResponse(
        {
            "status": "healthy",
            "service": "Atlas Toolset MCP",
            "version": "3.0.0",
            "features": ["calculator", "text_analyzer", "task_manager", "time"],
            "timestamp": datetime.now().isoformat()
        },
        status_code=200
    )

# Create MCP app
try:
    if hasattr(mcp, 'http_app'):
        mcp_app = mcp.http_app()
        logger.info("Created MCP app with /mcp path")
    elif hasattr(mcp, 'streamable_http_app'):
        mcp_app = mcp.streamable_http_app()
        logger.warning("Using older streamable_http_app()")
    else:
        raise AttributeError("No HTTP app method found in FastMCP")
    
except Exception as e:
    logger.error(f"Failed to create MCP HTTP app: {e}")
    raise

# Create main Starlette app with health check
app = Starlette(
    lifespan=mcp_app.lifespan,
    routes=[
        Route("/health", health_check, methods=["GET"]),
        Route("/", health_check, methods=["GET"]),
        Route("/mcp", mcp_app, methods=["POST", "GET"]),
        Route("/mcp/", mcp_app, methods=["POST", "GET"]),
    ]
)

# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Get configuration from environment
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"Starting Atlas Toolset MCP Server v3.0.0")
    logger.info(f"Server will be available at {host}:{port}/mcp")
    logger.info(f"Health check at {host}:{port}/health")
    logger.info(f"Features loaded: calculator, text_analyzer, task_manager, time")
    logger.info(f"Italian date format enabled with shortcuts")
    
    try:
        uvicorn.run(app, host=host, port=port)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
