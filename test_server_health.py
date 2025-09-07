#!/usr/bin/env python3
"""
Simple health check for the toolset-mcp server
"""

import httpx
import asyncio
import json
import sys

async def test_health():
    """Test if the server is running and healthy"""
    
    port = 8000  # Default port
    base_url = f"http://localhost:{port}"
    
    print(f"Testing Atlas Toolset MCP Server at {base_url}")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Health check endpoint
        try:
            print("\n1. Testing health endpoint...")
            response = await client.get(f"{base_url}/health")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Server: {data.get('service')}")
                print(f"   Version: {data.get('version')}")
                print(f"   Features: {', '.join(data.get('features', []))}")
        except Exception as e:
            print(f"   ERROR: {e}")
            print("   Is the server running? Start it with: python run_server.py")
            return False
        
        # Test 2: MCP endpoint
        try:
            print("\n2. Testing MCP endpoint...")
            # Send a simple MCP request
            mcp_request = {
                "jsonrpc": "2.0",
                "method": "mcp.describe",
                "params": {},
                "id": 1
            }
            
            response = await client.post(
                f"{base_url}/mcp", 
                json=mcp_request,
                headers={"Content-Type": "application/json"}
            )
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                # The response might be streaming or regular JSON
                content = response.text
                print(f"   Response preview: {content[:200]}...")
                
        except Exception as e:
            print(f"   ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("Server check completed!")
    return True

if __name__ == "__main__":
    result = asyncio.run(test_health())
    sys.exit(0 if result else 1)
