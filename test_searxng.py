#!/usr/bin/env python3
"""
Test SearXNG integration specifically
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from remote_mcp.features.search_manager.engine import SearXNGSearchProvider


async def test_searxng():
    """Test SearXNG provider directly"""
    
    # Check if SearXNG is configured
    server_url = os.getenv('SEARXNG_SERVER_URL')
    if not server_url:
        print("SEARXNG_SERVER_URL not set. Please configure it:")
        print("export SEARXNG_SERVER_URL=https://your-searxng-instance.com")
        return
    
    print(f"Testing SearXNG at: {server_url}")
    print("-" * 50)
    
    # Initialize provider
    try:
        provider = SearXNGSearchProvider()
        provider.validate_env()
        print("✓ SearXNG provider initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        return
    
    # Test search
    query = "open source privacy tools"
    print(f"\nSearching for: '{query}'")
    
    try:
        results = await provider.search(query, max_results=5)
        print(f"\nFound {len(results)} results:")
        
        # Show engines used
        all_engines = set()
        for result in results:
            if 'engines' in result.metadata:
                all_engines.update(result.metadata['engines'])
        
        if all_engines:
            print(f"Search engines used: {', '.join(sorted(all_engines))}")
        
        print("\nTop results:")
        for i, result in enumerate(results[:3], 1):
            print(f"\n{i}. {result.title}")
            print(f"   URL: {result.url}")
            print(f"   Score: {result.score}")
            if result.metadata.get('engines'):
                print(f"   Found by: {', '.join(result.metadata['engines'])}")
            print(f"   Snippet: {result.snippet[:100]}...")
            
    except Exception as e:
        print(f"Search failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_searxng())
