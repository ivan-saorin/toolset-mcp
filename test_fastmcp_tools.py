#!/usr/bin/env python3
"""
Test FastMCP tool registration and invocation
"""

import asyncio
from fastmcp import FastMCP

# Create a simple test server
mcp = FastMCP("Test Server")

@mcp.tool()
async def test_simple(message: str) -> dict:
    """Simple test tool"""
    return {"message": f"Received: {message}"}

@mcp.tool()
async def test_math(a: float, b: float, operation: str = "add") -> dict:
    """Test math operations"""
    if operation == "add":
        result = a + b
    elif operation == "multiply":
        result = a * b
    else:
        result = 0
    return {"result": result, "operation": operation}

async def test_tools():
    """Test if tools are properly registered"""
    print("Testing FastMCP Tool Registration")
    print("=" * 60)
    
    # Check if tools are registered
    if hasattr(mcp, '_tools'):
        print(f"\nRegistered tools: {list(mcp._tools.keys())}")
    else:
        print("\nNo _tools attribute found")
    
    # Try to get tool list through FastMCP's methods
    if hasattr(mcp, 'get_tools'):
        tools = mcp.get_tools()
        print(f"\nTools from get_tools(): {tools}")
    
    # Test direct invocation
    try:
        result = await test_simple("Hello")
        print(f"\nDirect invocation works: {result}")
    except Exception as e:
        print(f"\nDirect invocation error: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_tools())
