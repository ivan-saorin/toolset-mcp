#!/usr/bin/env python3
"""
Test script for Search Manager feature

This script demonstrates how to use the search manager directly.
Run with appropriate environment variables set for API keys.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from remote_mcp.features.search_manager import SearchManagerEngine


async def test_search_manager():
    """Test the search manager functionality"""
    
    # Initialize the search manager
    search_manager = SearchManagerEngine()
    
    print("=== Search Manager Test ===")
    print(f"Web providers available: {list(search_manager.web_providers.keys())}")
    print(f"Paper providers available: {list(search_manager.paper_providers.keys())}")
    print()
    
    # Test 1: Web search
    if search_manager.web_providers:
        print("Test 1: Web Search")
        print("-" * 40)
        
        query = "FastMCP framework python"
        print(f"Searching for: '{query}'")
        
        result = await search_manager.web_search(query, max_results=5)
        
        if result.success:
            data = result.data
            print(f"Found {data['total_results']} results in {data['search_time']}s")
            print(f"Providers used: {', '.join(data['providers_used'])}")
            
            if data.get('errors'):
                print(f"Errors: {data['errors']}")
            
            print("\nTop results:")
            for i, res in enumerate(data['results'][:3], 1):
                print(f"{i}. {res['title']}")
                print(f"   URL: {res['url']}")
                print(f"   Source: {res['source']} (score: {res['score']})")
                print(f"   Snippet: {res['snippet'][:100]}...")
                print()
        else:
            print(f"Error: {result.error}")
        print()
    
    # Test 2: Paper search
    if search_manager.paper_providers:
        print("Test 2: Academic Paper Search")
        print("-" * 40)
        
        query = "transformer attention mechanism"
        print(f"Searching for: '{query}'")
        
        result = await search_manager.paper_search(query, max_results=5)
        
        if result.success:
            data = result.data
            print(f"Found {data['total_results']} papers in {data['search_time']}s")
            print(f"Providers used: {', '.join(data['providers_used'])}")
            
            if data.get('errors'):
                print(f"Errors: {data['errors']}")
            
            print("\nTop papers:")
            for i, paper in enumerate(data['results'][:3], 1):
                print(f"{i}. {paper['title']}")
                if paper.get('authors'):
                    print(f"   Authors: {', '.join(paper['authors'][:3])}")
                print(f"   Source: {paper['source']} (score: {paper['score']})")
                if paper.get('published_date'):
                    print(f"   Published: {paper['published_date']}")
                if paper.get('pdf_url'):
                    print(f"   PDF: {paper['pdf_url']}")
                print()
        else:
            print(f"Error: {result.error}")
    
    # Test 3: Specific provider search
    if 'arxiv' in search_manager.paper_providers:
        print("\nTest 3: ArXiv-specific Search")
        print("-" * 40)
        
        result = await search_manager.paper_search(
            "quantum computing",
            providers=['arxiv'],
            max_results=3
        )
        
        if result.success:
            data = result.data
            print(f"Found {data['total_results']} papers from ArXiv")
            for paper in data['results']:
                print(f"- {paper['title'][:60]}...")
        else:
            print(f"Error: {result.error}")
    
    # Test 4: SearXNG search (if configured)
    if 'searxng' in search_manager.web_providers:
        print("\nTest 4: SearXNG Meta-search")
        print("-" * 40)
        
        result = await search_manager.web_search(
            "open source privacy tools",
            providers=['searxng'],
            max_results=5
        )
        
        if result.success:
            data = result.data
            print(f"Found {data['total_results']} results via SearXNG")
            print("\nSources aggregated:")
            # Show which search engines provided results
            engines_used = set()
            for res in data['results']:
                if 'engines' in res.get('metadata', {}):
                    engines_used.update(res['metadata']['engines'])
            if engines_used:
                print(f"Engines: {', '.join(sorted(engines_used))}")
            
            print("\nTop results:")
            for i, res in enumerate(data['results'][:3], 1):
                print(f"{i}. {res['title']}")
                print(f"   URL: {res['url']}")
                if 'engines' in res.get('metadata', {}):
                    print(f"   Found by: {', '.join(res['metadata']['engines'])}")
        else:
            print(f"Error: {result.error}")
    
    print("\n=== Test Complete ===")


def check_environment():
    """Check which API keys are configured"""
    print("Environment Configuration:")
    print("-" * 40)
    
    api_keys = {
        'BRAVE_API_KEY': 'Brave Search',
        'TAVILY_API_KEY': 'Tavily AI Search',
        'SEARXNG_SERVER_URL': 'SearXNG Meta-search',
        'PUBMED_API_KEY': 'PubMed (optional)',
        'SEMANTIC_SCHOLAR_API_KEY': 'Semantic Scholar (optional)'
    }
    
    configured = 0
    for key, name in api_keys.items():
        if os.getenv(key):
            print(f"✓ {name}: Configured")
            configured += 1
        else:
            print(f"✗ {name}: Not configured")
    
    if configured == 0:
        print("\n⚠️  No API keys configured. Search features will not work.")
        print("   Set at least BRAVE_API_KEY, TAVILY_API_KEY, or SEARXNG_SERVER_URL to enable web search.")
    
    print()
    return configured > 0


if __name__ == "__main__":
    # Check environment first
    has_keys = check_environment()
    
    if has_keys:
        # Run the tests
        asyncio.run(test_search_manager())
    else:
        print("Please configure API keys in your environment or .env file")
        print("Example:")
        print("  export BRAVE_API_KEY=your_key_here")
        print("  export TAVILY_API_KEY=your_key_here")
        print("  export SEARXNG_SERVER_URL=https://your-searxng-instance.com")
