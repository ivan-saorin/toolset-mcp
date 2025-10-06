"""
Unified Search Manager Engine for web and academic paper searches

Consolidates multiple search providers into two simple interfaces:
- web_search: General web searches (Brave, Tavily)
- paper_search: Academic paper searches (ArXiv, PubMed, etc.)

All searches run in parallel for optimal performance.
"""

import os
import asyncio
import logging
from typing import Dict, Any, List, Union, Tuple
from datetime import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import aiohttp

from ...shared.base import BaseFeature, ToolResponse

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Unified search result format"""
    title: str
    url: str
    snippet: str
    source: str  # provider name
    score: float = 0.0  # relevance score
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # For papers
    authors: Union[List[str], None = None
    published_date: Union[str, None = None
    doi: Union[str, None = None
    abstract: Union[str, None = None
    pdf_url: Union[str, None = None
    
    # For web results
    domain: Union[str, None = None
    published_time: Union[str, None = None


@dataclass
class SearchResponse:
    """Response containing search results and metadata"""
    query: str
    results: List[SearchResult]
    total_results: int
    providers_used: List[str]
    search_time: float
    errors: Dict[str, str] = field(default_factory=dict)


class BaseSearchProvider(ABC):
    """Base class for all search providers"""
    
    def __init__(self, name: str, timeout: float = 5.0):
        self.name = name
        self.timeout = timeout
        self.logger = logging.getLogger(f"provider.{name}")
        
    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Execute search and return results"""
        pass
    
    @abstractmethod
    def get_env_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Return environment variable requirements"""
        pass
    
    def validate_env(self) -> None:
        """Validate required environment variables"""
        requirements = self.get_env_requirements()
        for var, details in requirements.items():
            if details.get('required', False) and not os.getenv(var):
                raise ValueError(f"{var} environment variable is required for {self.name}")


# ============================================================================
# WEB SEARCH PROVIDERS
# ============================================================================

class SearXNGSearchProvider(BaseSearchProvider):
    """SearXNG meta-search engine provider"""
    
    def __init__(self):
        super().__init__("searxng", timeout=10.0)  # Longer timeout for meta-search
        self.server_url = os.getenv('SEARXNG_SERVER_URL')
        if self.server_url:
            self.server_url = self.server_url.rstrip('/')
            self.search_url = f"{self.server_url}/search"
        
    def get_env_requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'SEARXNG_SERVER_URL': {
                'required': True,
                'description': 'Base URL of your SearXNG instance',
                'obtain_from': 'Self-hosted SearXNG instance or public instance',
                'example': 'https://searx.example.com'
            }
        }
    
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search using SearXNG meta-search engine"""
        if not self.server_url:
            raise ValueError("SEARXNG_SERVER_URL not configured")
        
        params = {
            'q': query,
            'format': 'json',
            'pageno': '1'  # SearXNG uses string page numbers
        }
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    self.search_url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # SearXNG returns results in a 'results' array
                        searxng_results = data.get('results', [])
                        
                        for idx, item in enumerate(searxng_results[:max_results]):
                            # Extract domain from URL
                            url = item.get('url', '')
                            domain = ''
                            if url.startswith('http'):
                                parts = url.split('/')
                                if len(parts) >= 3:
                                    domain = parts[2]
                            
                            # Build metadata including search engines
                            metadata = {
                                'engines': item.get('engines', [])
                            }
                            
                            # Add any additional fields SearXNG provides
                            for key in ['publishedDate', 'engine', 'score', 'category']:
                                if key in item:
                                    metadata[key] = item[key]
                            
                            results.append(SearchResult(
                                title=item.get('title', ''),
                                url=url,
                                snippet=item.get('content', ''),
                                source=self.name,
                                score=1.0 - (idx * 0.05),  # Simple ranking
                                domain=domain,
                                published_time=item.get('publishedDate', ''),
                                metadata=metadata
                            ))
                    else:
                        self.logger.error(f"SearXNG API error: {response.status}")
                        # Try to get error message
                        try:
                            error_data = await response.json()
                            self.logger.error(f"Error details: {error_data}")
                        except:
                            pass
                        
            except asyncio.TimeoutError:
                self.logger.error(f"SearXNG search timeout for query: {query}")
            except Exception as e:
                self.logger.error(f"SearXNG search error: {str(e)}")
                
        return results
    
    async def extract(self, urls: List[str], extract_depth: str = "basic", 
                     include_images: bool = False, format: str = "markdown",
                     include_favicon: bool = False) -> Dict[str, Any]:
        """Extract content from URLs"""
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            'api_key': self.api_key,
            'urls': urls,
            'extract_depth': extract_depth,
            'include_images': include_images,
            'format': format,
            'include_favicon': include_favicon
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.extract_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=15.0)  # Longer timeout for extraction
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_msg = f"Tavily Extract API error: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg, "status": response.status}
                        
            except asyncio.TimeoutError:
                self.logger.error("Tavily extract timeout")
                return {"error": "Extract timeout"}
            except Exception as e:
                self.logger.error(f"Tavily extract error: {str(e)}")
                return {"error": str(e)}
    
    async def crawl(self, url: str, max_depth: int = 1, max_breadth: int = 20,
                   limit: int = 50, instructions: str = None, select_paths: List[str] = None,
                   select_domains: List[str] = None, allow_external: bool = False,
                   categories: List[str] = None, extract_depth: str = "basic",
                   format: str = "markdown", include_favicon: bool = False) -> Dict[str, Any]:
        """Crawl a website starting from base URL"""
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            'api_key': self.api_key,
            'url': url,
            'max_depth': max_depth,
            'max_breadth': max_breadth,
            'limit': limit,
            'extract_depth': extract_depth,
            'format': format,
            'include_favicon': include_favicon,
            'allow_external': allow_external
        }
        
        if instructions:
            payload['instructions'] = instructions
        if select_paths:
            payload['select_paths'] = select_paths
        if select_domains:
            payload['select_domains'] = select_domains
        if categories:
            payload['categories'] = categories
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.crawl_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30.0)  # Longer timeout for crawling
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_msg = f"Tavily Crawl API error: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg, "status": response.status}
                        
            except asyncio.TimeoutError:
                self.logger.error("Tavily crawl timeout")
                return {"error": "Crawl timeout"}
            except Exception as e:
                self.logger.error(f"Tavily crawl error: {str(e)}")
                return {"error": str(e)}
    
    async def map(self, url: str, max_depth: int = 1, max_breadth: int = 20,
                 limit: int = 50, instructions: str = None, select_paths: List[str] = None,
                 select_domains: List[str] = None, allow_external: bool = False,
                 categories: List[str] = None) -> Dict[str, Any]:
        """Create a map of website structure"""
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            'api_key': self.api_key,
            'url': url,
            'max_depth': max_depth,
            'max_breadth': max_breadth,
            'limit': limit,
            'allow_external': allow_external
        }
        
        if instructions:
            payload['instructions'] = instructions
        if select_paths:
            payload['select_paths'] = select_paths
        if select_domains:
            payload['select_domains'] = select_domains
        if categories:
            payload['categories'] = categories
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.map_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=20.0)  # Moderate timeout for mapping
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_msg = f"Tavily Map API error: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg, "status": response.status}
                        
            except asyncio.TimeoutError:
                self.logger.error("Tavily map timeout")
                return {"error": "Map timeout"}
            except Exception as e:
                self.logger.error(f"Tavily map error: {str(e)}")
                return {"error": str(e)}

class BraveSearchProvider(BaseSearchProvider):
    """Brave Search API provider"""
    
    def __init__(self):
        super().__init__("brave", timeout=5.0)
        self.api_key = os.getenv('BRAVE_API_KEY')
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        
    def get_env_requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'BRAVE_API_KEY': {
                'required': True,
                'description': 'Brave Search API key',
                'obtain_from': 'https://brave.com/search/api/'
            }
        }
    
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search using Brave API"""
        if not self.api_key:
            raise ValueError("BRAVE_API_KEY not configured")
        
        headers = {
            'X-Subscription-Token': self.api_key,
            'Accept': 'application/json'
        }
        
        params = {
            'q': query,
            'count': min(max_results, 20),  # Brave max is 20
            'text_decorations': False,
            'spellcheck': False
        }
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    self.base_url,
                    headers=headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for idx, item in enumerate(data.get('web', {}).get('results', [])):
                            results.append(SearchResult(
                                title=item.get('title', ''),
                                url=item.get('url', ''),
                                snippet=item.get('description', ''),
                                source=self.name,
                                score=1.0 - (idx * 0.1),  # Simple ranking score
                                domain=item.get('domain', ''),
                                metadata={
                                    'age': item.get('age', ''),
                                    'language': item.get('language', '')
                                }
                            ))
                    else:
                        self.logger.error(f"Brave API error: {response.status}")
                        
            except asyncio.TimeoutError:
                self.logger.error(f"Brave search timeout for query: {query}")
            except Exception as e:
                self.logger.error(f"Brave search error: {str(e)}")
                
        return results
    
    async def extract(self, urls: List[str], extract_depth: str = "basic", 
                     include_images: bool = False, format: str = "markdown",
                     include_favicon: bool = False) -> Dict[str, Any]:
        """Extract content from URLs"""
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            'api_key': self.api_key,
            'urls': urls,
            'extract_depth': extract_depth,
            'include_images': include_images,
            'format': format,
            'include_favicon': include_favicon
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.extract_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=15.0)  # Longer timeout for extraction
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_msg = f"Tavily Extract API error: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg, "status": response.status}
                        
            except asyncio.TimeoutError:
                self.logger.error("Tavily extract timeout")
                return {"error": "Extract timeout"}
            except Exception as e:
                self.logger.error(f"Tavily extract error: {str(e)}")
                return {"error": str(e)}
    
    async def crawl(self, url: str, max_depth: int = 1, max_breadth: int = 20,
                   limit: int = 50, instructions: str = None, select_paths: List[str] = None,
                   select_domains: List[str] = None, allow_external: bool = False,
                   categories: List[str] = None, extract_depth: str = "basic",
                   format: str = "markdown", include_favicon: bool = False) -> Dict[str, Any]:
        """Crawl a website starting from base URL"""
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            'api_key': self.api_key,
            'url': url,
            'max_depth': max_depth,
            'max_breadth': max_breadth,
            'limit': limit,
            'extract_depth': extract_depth,
            'format': format,
            'include_favicon': include_favicon,
            'allow_external': allow_external
        }
        
        if instructions:
            payload['instructions'] = instructions
        if select_paths:
            payload['select_paths'] = select_paths
        if select_domains:
            payload['select_domains'] = select_domains
        if categories:
            payload['categories'] = categories
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.crawl_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30.0)  # Longer timeout for crawling
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_msg = f"Tavily Crawl API error: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg, "status": response.status}
                        
            except asyncio.TimeoutError:
                self.logger.error("Tavily crawl timeout")
                return {"error": "Crawl timeout"}
            except Exception as e:
                self.logger.error(f"Tavily crawl error: {str(e)}")
                return {"error": str(e)}
    
    async def map(self, url: str, max_depth: int = 1, max_breadth: int = 20,
                 limit: int = 50, instructions: str = None, select_paths: List[str] = None,
                 select_domains: List[str] = None, allow_external: bool = False,
                 categories: List[str] = None) -> Dict[str, Any]:
        """Create a map of website structure"""
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            'api_key': self.api_key,
            'url': url,
            'max_depth': max_depth,
            'max_breadth': max_breadth,
            'limit': limit,
            'allow_external': allow_external
        }
        
        if instructions:
            payload['instructions'] = instructions
        if select_paths:
            payload['select_paths'] = select_paths
        if select_domains:
            payload['select_domains'] = select_domains
        if categories:
            payload['categories'] = categories
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.map_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=20.0)  # Moderate timeout for mapping
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_msg = f"Tavily Map API error: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg, "status": response.status}
                        
            except asyncio.TimeoutError:
                self.logger.error("Tavily map timeout")
                return {"error": "Map timeout"}
            except Exception as e:
                self.logger.error(f"Tavily map error: {str(e)}")
                return {"error": str(e)}


class TavilySearchProvider(BaseSearchProvider):
    """Tavily AI-enhanced search provider"""
    
    def __init__(self):
        super().__init__("tavily", timeout=8.0)  # Slightly longer for AI processing
        self.api_key = os.getenv('TAVILY_API_KEY')
        self.base_url = "https://api.tavily.com/search"
        self.extract_url = "https://api.tavily.com/extract"
        self.crawl_url = "https://api.tavily.com/crawl"
        self.map_url = "https://api.tavily.com/map"
        
    def get_env_requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'TAVILY_API_KEY': {
                'required': True,
                'description': 'Tavily API key for AI-enhanced search',
                'obtain_from': 'https://app.tavily.com/'
            }
        }
    
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search using Tavily API"""
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            'api_key': self.api_key,
            'query': query,
            'max_results': min(max_results, 20),
            'search_depth': 'advanced',
            'include_domains': [],
            'exclude_domains': []
        }
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for idx, item in enumerate(data.get('results', [])):
                            # Extract domain from URL
                            domain = item.get('url', '').split('/')[2] if item.get('url', '').startswith('http') else ''
                            
                            results.append(SearchResult(
                                title=item.get('title', ''),
                                url=item.get('url', ''),
                                snippet=item.get('content', ''),
                                source=self.name,
                                score=item.get('score', 1.0 - (idx * 0.05)) * 1.2,  # Tavily gets higher weight
                                domain=domain,
                                published_time=item.get('published_date', ''),
                                metadata={
                                    'raw_content': item.get('raw_content', ''),
                                    'relevance_score': item.get('score', 0)
                                }
                            ))
                    else:
                        self.logger.error(f"Tavily API error: {response.status}")
                        
            except asyncio.TimeoutError:
                self.logger.error(f"Tavily search timeout for query: {query}")
            except Exception as e:
                self.logger.error(f"Tavily search error: {str(e)}")
                
        return results
    
    async def extract(self, urls: List[str], extract_depth: str = "basic", 
                     include_images: bool = False, format: str = "markdown",
                     include_favicon: bool = False) -> Dict[str, Any]:
        """Extract content from URLs"""
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            'api_key': self.api_key,
            'urls': urls,
            'extract_depth': extract_depth,
            'include_images': include_images,
            'format': format,
            'include_favicon': include_favicon
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.extract_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=15.0)  # Longer timeout for extraction
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_msg = f"Tavily Extract API error: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg, "status": response.status}
                        
            except asyncio.TimeoutError:
                self.logger.error("Tavily extract timeout")
                return {"error": "Extract timeout"}
            except Exception as e:
                self.logger.error(f"Tavily extract error: {str(e)}")
                return {"error": str(e)}
    
    async def crawl(self, url: str, max_depth: int = 1, max_breadth: int = 20,
                   limit: int = 50, instructions: str = None, select_paths: List[str] = None,
                   select_domains: List[str] = None, allow_external: bool = False,
                   categories: List[str] = None, extract_depth: str = "basic",
                   format: str = "markdown", include_favicon: bool = False) -> Dict[str, Any]:
        """Crawl a website starting from base URL"""
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            'api_key': self.api_key,
            'url': url,
            'max_depth': max_depth,
            'max_breadth': max_breadth,
            'limit': limit,
            'extract_depth': extract_depth,
            'format': format,
            'include_favicon': include_favicon,
            'allow_external': allow_external
        }
        
        if instructions:
            payload['instructions'] = instructions
        if select_paths:
            payload['select_paths'] = select_paths
        if select_domains:
            payload['select_domains'] = select_domains
        if categories:
            payload['categories'] = categories
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.crawl_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30.0)  # Longer timeout for crawling
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_msg = f"Tavily Crawl API error: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg, "status": response.status}
                        
            except asyncio.TimeoutError:
                self.logger.error("Tavily crawl timeout")
                return {"error": "Crawl timeout"}
            except Exception as e:
                self.logger.error(f"Tavily crawl error: {str(e)}")
                return {"error": str(e)}
    
    async def map(self, url: str, max_depth: int = 1, max_breadth: int = 20,
                 limit: int = 50, instructions: str = None, select_paths: List[str] = None,
                 select_domains: List[str] = None, allow_external: bool = False,
                 categories: List[str] = None) -> Dict[str, Any]:
        """Create a map of website structure"""
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            'api_key': self.api_key,
            'url': url,
            'max_depth': max_depth,
            'max_breadth': max_breadth,
            'limit': limit,
            'allow_external': allow_external
        }
        
        if instructions:
            payload['instructions'] = instructions
        if select_paths:
            payload['select_paths'] = select_paths
        if select_domains:
            payload['select_domains'] = select_domains
        if categories:
            payload['categories'] = categories
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.map_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=20.0)  # Moderate timeout for mapping
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_msg = f"Tavily Map API error: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg, "status": response.status}
                        
            except asyncio.TimeoutError:
                self.logger.error("Tavily map timeout")
                return {"error": "Map timeout"}
            except Exception as e:
                self.logger.error(f"Tavily map error: {str(e)}")
                return {"error": str(e)}


# ============================================================================
# ACADEMIC SEARCH PROVIDERS
# ============================================================================

class ArxivSearchProvider(BaseSearchProvider):
    """ArXiv paper search provider"""
    
    def __init__(self):
        super().__init__("arxiv", timeout=5.0)
        self.base_url = "http://export.arxiv.org/api/query"
        
    def get_env_requirements(self) -> Dict[str, Dict[str, Any]]:
        return {}  # ArXiv doesn't require API key
    
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search ArXiv papers"""
        params = {
            'search_query': f'all:{query}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    self.base_url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        # Parse XML response
                        text = await response.text()
                        results = self._parse_arxiv_response(text)
                    else:
                        self.logger.error(f"ArXiv API error: {response.status}")
                        
            except asyncio.TimeoutError:
                self.logger.error(f"ArXiv search timeout for query: {query}")
            except Exception as e:
                self.logger.error(f"ArXiv search error: {str(e)}")
                
        return results
    
    async def extract(self, urls: List[str], extract_depth: str = "basic", 
                     include_images: bool = False, format: str = "markdown",
                     include_favicon: bool = False) -> Dict[str, Any]:
        """Extract content from URLs"""
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            'api_key': self.api_key,
            'urls': urls,
            'extract_depth': extract_depth,
            'include_images': include_images,
            'format': format,
            'include_favicon': include_favicon
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.extract_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=15.0)  # Longer timeout for extraction
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_msg = f"Tavily Extract API error: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg, "status": response.status}
                        
            except asyncio.TimeoutError:
                self.logger.error("Tavily extract timeout")
                return {"error": "Extract timeout"}
            except Exception as e:
                self.logger.error(f"Tavily extract error: {str(e)}")
                return {"error": str(e)}
    
    async def crawl(self, url: str, max_depth: int = 1, max_breadth: int = 20,
                   limit: int = 50, instructions: str = None, select_paths: List[str] = None,
                   select_domains: List[str] = None, allow_external: bool = False,
                   categories: List[str] = None, extract_depth: str = "basic",
                   format: str = "markdown", include_favicon: bool = False) -> Dict[str, Any]:
        """Crawl a website starting from base URL"""
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            'api_key': self.api_key,
            'url': url,
            'max_depth': max_depth,
            'max_breadth': max_breadth,
            'limit': limit,
            'extract_depth': extract_depth,
            'format': format,
            'include_favicon': include_favicon,
            'allow_external': allow_external
        }
        
        if instructions:
            payload['instructions'] = instructions
        if select_paths:
            payload['select_paths'] = select_paths
        if select_domains:
            payload['select_domains'] = select_domains
        if categories:
            payload['categories'] = categories
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.crawl_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30.0)  # Longer timeout for crawling
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_msg = f"Tavily Crawl API error: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg, "status": response.status}
                        
            except asyncio.TimeoutError:
                self.logger.error("Tavily crawl timeout")
                return {"error": "Crawl timeout"}
            except Exception as e:
                self.logger.error(f"Tavily crawl error: {str(e)}")
                return {"error": str(e)}
    
    async def map(self, url: str, max_depth: int = 1, max_breadth: int = 20,
                 limit: int = 50, instructions: str = None, select_paths: List[str] = None,
                 select_domains: List[str] = None, allow_external: bool = False,
                 categories: List[str] = None) -> Dict[str, Any]:
        """Create a map of website structure"""
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            'api_key': self.api_key,
            'url': url,
            'max_depth': max_depth,
            'max_breadth': max_breadth,
            'limit': limit,
            'allow_external': allow_external
        }
        
        if instructions:
            payload['instructions'] = instructions
        if select_paths:
            payload['select_paths'] = select_paths
        if select_domains:
            payload['select_domains'] = select_domains
        if categories:
            payload['categories'] = categories
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.map_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=20.0)  # Moderate timeout for mapping
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_msg = f"Tavily Map API error: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg, "status": response.status}
                        
            except asyncio.TimeoutError:
                self.logger.error("Tavily map timeout")
                return {"error": "Map timeout"}
            except Exception as e:
                self.logger.error(f"Tavily map error: {str(e)}")
                return {"error": str(e)}
    
    def _parse_arxiv_response(self, xml_text: str) -> List[SearchResult]:
        """Parse ArXiv XML response"""
        results = []
        
        # Simple XML parsing (in production, use proper XML parser)
        import re
        
        entries = re.findall(r'<entry>(.*?)</entry>', xml_text, re.DOTALL)
        
        for idx, entry in enumerate(entries):
            # Extract fields
            title = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
            title = title.group(1).strip() if title else ''
            
            summary = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
            summary = summary.group(1).strip() if summary else ''
            
            # Extract ID for URL
            id_match = re.search(r'<id>http://arxiv.org/abs/(.*?)</id>', entry)
            arxiv_id = id_match.group(1) if id_match else ''
            
            # Extract authors
            authors = re.findall(r'<name>(.*?)</name>', entry)
            
            # Extract published date
            published = re.search(r'<published>(.*?)</published>', entry)
            published_date = published.group(1) if published else ''
            
            if title and arxiv_id:
                results.append(SearchResult(
                    title=title,
                    url=f"https://arxiv.org/abs/{arxiv_id}",
                    snippet=summary[:200] + '...' if len(summary) > 200 else summary,
                    source=self.name,
                    score=1.0 - (idx * 0.1),
                    authors=authors,
                    published_date=published_date,
                    abstract=summary,
                    pdf_url=f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                    metadata={
                        'arxiv_id': arxiv_id,
                        'categories': re.findall(r'<category.*?term="(.*?)"', entry)
                    }
                ))
                
        return results
    
    async def extract(self, urls: List[str], extract_depth: str = "basic", 
                     include_images: bool = False, format: str = "markdown",
                     include_favicon: bool = False) -> Dict[str, Any]:
        """Extract content from URLs"""
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            'api_key': self.api_key,
            'urls': urls,
            'extract_depth': extract_depth,
            'include_images': include_images,
            'format': format,
            'include_favicon': include_favicon
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.extract_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=15.0)  # Longer timeout for extraction
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_msg = f"Tavily Extract API error: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg, "status": response.status}
                        
            except asyncio.TimeoutError:
                self.logger.error("Tavily extract timeout")
                return {"error": "Extract timeout"}
            except Exception as e:
                self.logger.error(f"Tavily extract error: {str(e)}")
                return {"error": str(e)}
    
    async def crawl(self, url: str, max_depth: int = 1, max_breadth: int = 20,
                   limit: int = 50, instructions: str = None, select_paths: List[str] = None,
                   select_domains: List[str] = None, allow_external: bool = False,
                   categories: List[str] = None, extract_depth: str = "basic",
                   format: str = "markdown", include_favicon: bool = False) -> Dict[str, Any]:
        """Crawl a website starting from base URL"""
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            'api_key': self.api_key,
            'url': url,
            'max_depth': max_depth,
            'max_breadth': max_breadth,
            'limit': limit,
            'extract_depth': extract_depth,
            'format': format,
            'include_favicon': include_favicon,
            'allow_external': allow_external
        }
        
        if instructions:
            payload['instructions'] = instructions
        if select_paths:
            payload['select_paths'] = select_paths
        if select_domains:
            payload['select_domains'] = select_domains
        if categories:
            payload['categories'] = categories
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.crawl_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30.0)  # Longer timeout for crawling
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_msg = f"Tavily Crawl API error: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg, "status": response.status}
                        
            except asyncio.TimeoutError:
                self.logger.error("Tavily crawl timeout")
                return {"error": "Crawl timeout"}
            except Exception as e:
                self.logger.error(f"Tavily crawl error: {str(e)}")
                return {"error": str(e)}
    
    async def map(self, url: str, max_depth: int = 1, max_breadth: int = 20,
                 limit: int = 50, instructions: str = None, select_paths: List[str] = None,
                 select_domains: List[str] = None, allow_external: bool = False,
                 categories: List[str] = None) -> Dict[str, Any]:
        """Create a map of website structure"""
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            'api_key': self.api_key,
            'url': url,
            'max_depth': max_depth,
            'max_breadth': max_breadth,
            'limit': limit,
            'allow_external': allow_external
        }
        
        if instructions:
            payload['instructions'] = instructions
        if select_paths:
            payload['select_paths'] = select_paths
        if select_domains:
            payload['select_domains'] = select_domains
        if categories:
            payload['categories'] = categories
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.map_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=20.0)  # Moderate timeout for mapping
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_msg = f"Tavily Map API error: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg, "status": response.status}
                        
            except asyncio.TimeoutError:
                self.logger.error("Tavily map timeout")
                return {"error": "Map timeout"}
            except Exception as e:
                self.logger.error(f"Tavily map error: {str(e)}")
                return {"error": str(e)}
    
    async def download(self, paper_id: str, save_path: str) -> str:
        """Download paper PDF"""
        pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
        file_path = os.path.join(save_path, f"{paper_id.replace('/', '_')}.pdf")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(pdf_url) as response:
                if response.status == 200:
                    content = await response.read()
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    return file_path
                else:
                    raise Exception(f"Failed to download: {response.status}")


class PubMedSearchProvider(BaseSearchProvider):
    """PubMed paper search provider"""
    
    def __init__(self):
        super().__init__("pubmed", timeout=5.0)
        self.api_key = os.getenv('PUBMED_API_KEY')
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        
    def get_env_requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'PUBMED_API_KEY': {
                'required': False,
                'description': 'PubMed API key (optional, increases rate limit)',
                'obtain_from': 'https://www.ncbi.nlm.nih.gov/account/'
            }
        }
    
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search PubMed papers"""
        # First, search for IDs
        search_params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'json'
        }
        
        if self.api_key:
            search_params['api_key'] = self.api_key
            
        results = []
        
        async with aiohttp.ClientSession() as session:
            try:
                # Search for IDs
                async with session.get(
                    f"{self.base_url}/esearch.fcgi",
                    params=search_params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        id_list = data.get('esearchresult', {}).get('idlist', [])
                        
                        if id_list:
                            # Fetch summaries
                            results = await self._fetch_summaries(session, id_list)
                    else:
                        self.logger.error(f"PubMed search error: {response.status}")
                        
            except asyncio.TimeoutError:
                self.logger.error(f"PubMed search timeout for query: {query}")
            except Exception as e:
                self.logger.error(f"PubMed search error: {str(e)}")
                
        return results
    
    async def extract(self, urls: List[str], extract_depth: str = "basic", 
                     include_images: bool = False, format: str = "markdown",
                     include_favicon: bool = False) -> Dict[str, Any]:
        """Extract content from URLs"""
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            'api_key': self.api_key,
            'urls': urls,
            'extract_depth': extract_depth,
            'include_images': include_images,
            'format': format,
            'include_favicon': include_favicon
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.extract_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=15.0)  # Longer timeout for extraction
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_msg = f"Tavily Extract API error: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg, "status": response.status}
                        
            except asyncio.TimeoutError:
                self.logger.error("Tavily extract timeout")
                return {"error": "Extract timeout"}
            except Exception as e:
                self.logger.error(f"Tavily extract error: {str(e)}")
                return {"error": str(e)}
    
    async def crawl(self, url: str, max_depth: int = 1, max_breadth: int = 20,
                   limit: int = 50, instructions: str = None, select_paths: List[str] = None,
                   select_domains: List[str] = None, allow_external: bool = False,
                   categories: List[str] = None, extract_depth: str = "basic",
                   format: str = "markdown", include_favicon: bool = False) -> Dict[str, Any]:
        """Crawl a website starting from base URL"""
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            'api_key': self.api_key,
            'url': url,
            'max_depth': max_depth,
            'max_breadth': max_breadth,
            'limit': limit,
            'extract_depth': extract_depth,
            'format': format,
            'include_favicon': include_favicon,
            'allow_external': allow_external
        }
        
        if instructions:
            payload['instructions'] = instructions
        if select_paths:
            payload['select_paths'] = select_paths
        if select_domains:
            payload['select_domains'] = select_domains
        if categories:
            payload['categories'] = categories
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.crawl_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30.0)  # Longer timeout for crawling
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_msg = f"Tavily Crawl API error: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg, "status": response.status}
                        
            except asyncio.TimeoutError:
                self.logger.error("Tavily crawl timeout")
                return {"error": "Crawl timeout"}
            except Exception as e:
                self.logger.error(f"Tavily crawl error: {str(e)}")
                return {"error": str(e)}
    
    async def map(self, url: str, max_depth: int = 1, max_breadth: int = 20,
                 limit: int = 50, instructions: str = None, select_paths: List[str] = None,
                 select_domains: List[str] = None, allow_external: bool = False,
                 categories: List[str] = None) -> Dict[str, Any]:
        """Create a map of website structure"""
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            'api_key': self.api_key,
            'url': url,
            'max_depth': max_depth,
            'max_breadth': max_breadth,
            'limit': limit,
            'allow_external': allow_external
        }
        
        if instructions:
            payload['instructions'] = instructions
        if select_paths:
            payload['select_paths'] = select_paths
        if select_domains:
            payload['select_domains'] = select_domains
        if categories:
            payload['categories'] = categories
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.map_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=20.0)  # Moderate timeout for mapping
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_msg = f"Tavily Map API error: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg, "status": response.status}
                        
            except asyncio.TimeoutError:
                self.logger.error("Tavily map timeout")
                return {"error": "Map timeout"}
            except Exception as e:
                self.logger.error(f"Tavily map error: {str(e)}")
                return {"error": str(e)}
    
    async def _fetch_summaries(self, session: aiohttp.ClientSession, id_list: List[str]) -> List[SearchResult]:
        """Fetch paper summaries from PubMed"""
        summary_params = {
            'db': 'pubmed',
            'id': ','.join(id_list),
            'retmode': 'json'
        }
        
        if self.api_key:
            summary_params['api_key'] = self.api_key
            
        results = []
        
        try:
            async with session.get(
                f"{self.base_url}/esummary.fcgi",
                params=summary_params,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for idx, pmid in enumerate(id_list):
                        doc = data.get('result', {}).get(pmid, {})
                        
                        if doc:
                            # Extract authors
                            authors = []
                            for author in doc.get('authors', []):
                                name = author.get('name', '')
                                if name:
                                    authors.append(name)
                                    
                            results.append(SearchResult(
                                title=doc.get('title', ''),
                                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                                snippet=doc.get('sortpubdate', ''),
                                source=self.name,
                                score=1.0 - (idx * 0.1),
                                authors=authors[:5],  # Limit authors
                                published_date=doc.get('pubdate', ''),
                                doi=doc.get('elocationid', ''),
                                metadata={
                                    'pmid': pmid,
                                    'journal': doc.get('fulljournalname', ''),
                                    'pubtype': doc.get('pubtype', [])
                                }
                            ))
                            
        except Exception as e:
            self.logger.error(f"PubMed fetch summaries error: {str(e)}")
            
        return results


class SemanticScholarProvider(BaseSearchProvider):
    """Semantic Scholar search provider"""
    
    def __init__(self):
        super().__init__("semantic_scholar", timeout=5.0)
        self.api_key = os.getenv('SEMANTIC_SCHOLAR_API_KEY')
        self.base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
        
    def get_env_requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'SEMANTIC_SCHOLAR_API_KEY': {
                'required': False,
                'description': 'Semantic Scholar API key (optional, increases rate limit)',
                'obtain_from': 'https://www.semanticscholar.org/product/api'
            }
        }
    
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search Semantic Scholar papers"""
        headers = {}
        if self.api_key:
            headers['x-api-key'] = self.api_key
            
        params = {
            'query': query,
            'limit': min(max_results, 100),
            'fields': 'title,abstract,authors,year,url,publicationDate,doi,citationCount,openAccessPdf'
        }
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    self.base_url,
                    headers=headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for idx, paper in enumerate(data.get('data', [])):
                            # Extract authors
                            authors = [author.get('name', '') for author in paper.get('authors', [])]
                            
                            # Get PDF URL if available
                            pdf_url = None
                            if paper.get('openAccessPdf'):
                                pdf_url = paper['openAccessPdf'].get('url')
                                
                            results.append(SearchResult(
                                title=paper.get('title', ''),
                                url=paper.get('url', ''),
                                snippet=paper.get('abstract', '')[:200] + '...' if paper.get('abstract') else '',
                                source=self.name,
                                score=(1.0 - (idx * 0.05)) * 1.1,  # Slight boost for Semantic Scholar
                                authors=authors[:5],
                                published_date=paper.get('publicationDate', ''),
                                doi=paper.get('doi', ''),
                                abstract=paper.get('abstract', ''),
                                pdf_url=pdf_url,
                                metadata={
                                    'year': paper.get('year'),
                                    'citation_count': paper.get('citationCount', 0),
                                    'paper_id': paper.get('paperId', '')
                                }
                            ))
                    else:
                        self.logger.error(f"Semantic Scholar API error: {response.status}")
                        
            except asyncio.TimeoutError:
                self.logger.error(f"Semantic Scholar search timeout for query: {query}")
            except Exception as e:
                self.logger.error(f"Semantic Scholar search error: {str(e)}")
                
        return results
    
    async def extract(self, urls: List[str], extract_depth: str = "basic", 
                     include_images: bool = False, format: str = "markdown",
                     include_favicon: bool = False) -> Dict[str, Any]:
        """Extract content from URLs"""
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            'api_key': self.api_key,
            'urls': urls,
            'extract_depth': extract_depth,
            'include_images': include_images,
            'format': format,
            'include_favicon': include_favicon
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.extract_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=15.0)  # Longer timeout for extraction
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_msg = f"Tavily Extract API error: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg, "status": response.status}
                        
            except asyncio.TimeoutError:
                self.logger.error("Tavily extract timeout")
                return {"error": "Extract timeout"}
            except Exception as e:
                self.logger.error(f"Tavily extract error: {str(e)}")
                return {"error": str(e)}
    
    async def crawl(self, url: str, max_depth: int = 1, max_breadth: int = 20,
                   limit: int = 50, instructions: str = None, select_paths: List[str] = None,
                   select_domains: List[str] = None, allow_external: bool = False,
                   categories: List[str] = None, extract_depth: str = "basic",
                   format: str = "markdown", include_favicon: bool = False) -> Dict[str, Any]:
        """Crawl a website starting from base URL"""
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            'api_key': self.api_key,
            'url': url,
            'max_depth': max_depth,
            'max_breadth': max_breadth,
            'limit': limit,
            'extract_depth': extract_depth,
            'format': format,
            'include_favicon': include_favicon,
            'allow_external': allow_external
        }
        
        if instructions:
            payload['instructions'] = instructions
        if select_paths:
            payload['select_paths'] = select_paths
        if select_domains:
            payload['select_domains'] = select_domains
        if categories:
            payload['categories'] = categories
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.crawl_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30.0)  # Longer timeout for crawling
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_msg = f"Tavily Crawl API error: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg, "status": response.status}
                        
            except asyncio.TimeoutError:
                self.logger.error("Tavily crawl timeout")
                return {"error": "Crawl timeout"}
            except Exception as e:
                self.logger.error(f"Tavily crawl error: {str(e)}")
                return {"error": str(e)}
    
    async def map(self, url: str, max_depth: int = 1, max_breadth: int = 20,
                 limit: int = 50, instructions: str = None, select_paths: List[str] = None,
                 select_domains: List[str] = None, allow_external: bool = False,
                 categories: List[str] = None) -> Dict[str, Any]:
        """Create a map of website structure"""
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            'api_key': self.api_key,
            'url': url,
            'max_depth': max_depth,
            'max_breadth': max_breadth,
            'limit': limit,
            'allow_external': allow_external
        }
        
        if instructions:
            payload['instructions'] = instructions
        if select_paths:
            payload['select_paths'] = select_paths
        if select_domains:
            payload['select_domains'] = select_domains
        if categories:
            payload['categories'] = categories
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.map_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=20.0)  # Moderate timeout for mapping
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_msg = f"Tavily Map API error: {response.status}"
                        self.logger.error(error_msg)
                        return {"error": error_msg, "status": response.status}
                        
            except asyncio.TimeoutError:
                self.logger.error("Tavily map timeout")
                return {"error": "Map timeout"}
            except Exception as e:
                self.logger.error(f"Tavily map error: {str(e)}")
                return {"error": str(e)}
    
    async def download(self, paper_id: str, save_path: str) -> str:
        """Download paper if open access PDF is available"""
        headers = {}
        if self.api_key:
            headers['x-api-key'] = self.api_key
            
        # Get paper details
        async with aiohttp.ClientSession() as session:
            url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}?fields=openAccessPdf"
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('openAccessPdf'):
                        pdf_url = data['openAccessPdf']['url']
                        # Download PDF
                        async with session.get(pdf_url) as pdf_response:
                            if pdf_response.status == 200:
                                content = await pdf_response.read()
                                file_path = os.path.join(save_path, f"{paper_id}.pdf")
                                with open(file_path, 'wb') as f:
                                    f.write(content)
                                return file_path
                                
        raise Exception("PDF not available for download")


# ============================================================================
# SEARCH MANAGER ENGINE
# ============================================================================

class SearchManagerEngine(BaseFeature):
    """Unified search manager for web and academic searches"""
    
    def __init__(self):
        super().__init__("search_manager", "1.0.0")
        
        # Initialize providers
        self.web_providers = {}
        self.paper_providers = {}
        
        # Try to initialize each provider
        self._initialize_providers()
        
    def _initialize_providers(self):
        """Initialize available providers based on environment"""
        # Web providers
        try:
            brave = BraveSearchProvider()
            brave.validate_env()
            self.web_providers['brave'] = brave
            self.logger.info("Initialized Brave search provider")
        except Exception as e:
            self.logger.warning(f"Brave provider not available: {e}")
            
        try:
            tavily = TavilySearchProvider()
            tavily.validate_env()
            self.web_providers['tavily'] = tavily
            self.logger.info("Initialized Tavily search provider")
        except Exception as e:
            self.logger.warning(f"Tavily provider not available: {e}")
            
        try:
            searxng = SearXNGSearchProvider()
            searxng.validate_env()
            self.web_providers['searxng'] = searxng
            self.logger.info("Initialized SearXNG search provider")
        except Exception as e:
            self.logger.warning(f"SearXNG provider not available: {e}")
            
        # Paper providers
        try:
            arxiv = ArxivSearchProvider()
            arxiv.validate_env()
            self.paper_providers['arxiv'] = arxiv
            self.logger.info("Initialized ArXiv search provider")
        except Exception as e:
            self.logger.warning(f"ArXiv provider not available: {e}")
            
        try:
            pubmed = PubMedSearchProvider()
            pubmed.validate_env()
            self.paper_providers['pubmed'] = pubmed
            self.logger.info("Initialized PubMed search provider")
        except Exception as e:
            self.logger.warning(f"PubMed provider not available: {e}")
            
        try:
            semantic = SemanticScholarProvider()
            semantic.validate_env()
            self.paper_providers['semantic'] = semantic
            self.logger.info("Initialized Semantic Scholar search provider")
        except Exception as e:
            self.logger.warning(f"Semantic Scholar provider not available: {e}")
            
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of search tools"""
        return [
            {
                "name": "web_search",
                "description": "Search the web using multiple providers",
                "parameters": {
                    "query": "Search query",
                    "providers": "Optional list of providers to use (brave, tavily, searxng)",
                    "max_results": "Maximum results to return (default: 10)"
                }
            },
            {
                "name": "paper_search",
                "description": "Search academic papers",
                "parameters": {
                    "query": "Search query",
                    "providers": "Optional list of providers (arxiv, pubmed, semantic)",
                    "max_results": "Maximum results to return (default: 10)"
                }
            },
            {
                "name": "paper_download",
                "description": "Download a paper PDF",
                "parameters": {
                    "paper_id": "Paper identifier",
                    "provider": "Which provider to use",
                    "save_path": "Where to save (default: ./downloads)"
                }
            },
            {
                "name": "paper_read",
                "description": "Download and extract text from paper",
                "parameters": {
                    "paper_id": "Paper identifier",
                    "provider": "Which provider to use"
                }
            },
            {
                "name": "tavily_extract",
                "description": "Extract and process content from specified URLs with advanced parsing capabilities",
                "parameters": {
                    "urls": "List of URLs to extract content from",
                    "extract_depth": "Depth of extraction - 'basic' or 'advanced' (use advanced for LinkedIn)",
                    "include_images": "Include images from the URLs (default: false)",
                    "format": "Output format - 'markdown' or 'text' (default: markdown)",
                    "include_favicon": "Include favicon URLs (default: false)"
                }
            },
            {
                "name": "tavily_crawl",
                "description": "Crawl a website systematically starting from a base URL, following internal links",
                "parameters": {
                    "url": "The root URL to begin the crawl",
                    "max_depth": "Max depth of crawl (default: 1)",
                    "max_breadth": "Max links per level (default: 20)",
                    "limit": "Total links to process (default: 50)",
                    "instructions": "Natural language instructions for the crawler",
                    "select_paths": "Regex patterns for URL paths (e.g., /docs/.*, /api/v1.*)",
                    "select_domains": "Regex patterns for domains",
                    "allow_external": "Allow external domain links (default: false)",
                    "categories": "Filter by categories: Careers, Blog, Documentation, About, Pricing, Community, Developers, Contact, Media",
                    "extract_depth": "'basic' or 'advanced' extraction",
                    "format": "'markdown' or 'text' output",
                    "include_favicon": "Include favicon URLs"
                }
            },
            {
                "name": "tavily_map",
                "description": "Create a structured map of website URLs for site analysis and navigation understanding",
                "parameters": {
                    "url": "The root URL to begin mapping",
                    "max_depth": "Max depth of mapping (default: 1)",
                    "max_breadth": "Max links per level (default: 20)",
                    "limit": "Total links to process (default: 50)",
                    "instructions": "Natural language instructions",
                    "select_paths": "Regex patterns for URL paths",
                    "select_domains": "Regex patterns for domains",
                    "allow_external": "Allow external domain links (default: false)",
                    "categories": "Filter by categories"
                }
            }
        ]
    
    async def web_search(
        self,
        query: str,
        providers: Union[List[str], None = None,
        max_results: int = 10
    ) -> ToolResponse:
        """Search the web using specified providers"""
        try:
            start_time = datetime.now()
            
            # Determine which providers to use
            if providers is None:
                providers = list(self.web_providers.keys())
            else:
                # Validate providers
                invalid = [p for p in providers if p not in self.web_providers]
                if invalid:
                    return ToolResponse(
                        success=False,
                        error=f"Unknown providers: {invalid}. Available: {list(self.web_providers.keys())}"
                    )
                    
            if not providers:
                return ToolResponse(
                    success=False,
                    error="No web search providers available. Please configure BRAVE_API_KEY or TAVILY_API_KEY"
                )
                
            # Run searches in parallel
            tasks = []
            for provider_name in providers:
                provider = self.web_providers[provider_name]
                task = provider.search(query, max_results)
                tasks.append((provider_name, task))
                
            # Gather results with error handling
            all_results = []
            errors = {}
            
            results = await asyncio.gather(*[t[1] for t in tasks], return_exceptions=True)
            
            for (provider_name, _), result in zip(tasks, results):
                if isinstance(result, Exception):
                    errors[provider_name] = str(result)
                    self.logger.error(f"{provider_name} error: {result}")
                else:
                    all_results.extend(result)
                    
            # Consolidate and rank results
            consolidated = self._consolidate_results(all_results, max_results)
            
            # Calculate search time
            search_time = (datetime.now() - start_time).total_seconds()
            
            return ToolResponse(
                success=True,
                data={
                    "query": query,
                    "results": [self._serialize_result(r) for r in consolidated],
                    "total_results": len(consolidated),
                    "providers_used": [p for p in providers if p not in errors],
                    "search_time": round(search_time, 2),
                    "errors": errors
                }
            )
            
        except Exception as e:
            return self.handle_error("web_search", e)
            
    async def paper_search(
        self,
        query: str,
        providers: Union[List[str], None = None,
        max_results: int = 10
    ) -> ToolResponse:
        """Search academic papers using specified providers"""
        try:
            start_time = datetime.now()
            
            # Determine which providers to use
            if providers is None:
                providers = list(self.paper_providers.keys())
            else:
                # Validate providers
                invalid = [p for p in providers if p not in self.paper_providers]
                if invalid:
                    return ToolResponse(
                        success=False,
                        error=f"Unknown providers: {invalid}. Available: {list(self.paper_providers.keys())}"
                    )
                    
            if not providers:
                return ToolResponse(
                    success=False,
                    error="No paper search providers available"
                )
                
            # Run searches in parallel
            tasks = []
            for provider_name in providers:
                provider = self.paper_providers[provider_name]
                task = provider.search(query, max_results)
                tasks.append((provider_name, task))
                
            # Gather results with error handling
            all_results = []
            errors = {}
            
            results = await asyncio.gather(*[t[1] for t in tasks], return_exceptions=True)
            
            for (provider_name, _), result in zip(tasks, results):
                if isinstance(result, Exception):
                    errors[provider_name] = str(result)
                    self.logger.error(f"{provider_name} error: {result}")
                else:
                    all_results.extend(result)
                    
            # Consolidate and rank results
            consolidated = self._consolidate_papers(all_results, max_results)
            
            # Calculate search time
            search_time = (datetime.now() - start_time).total_seconds()
            
            return ToolResponse(
                success=True,
                data={
                    "query": query,
                    "results": [self._serialize_result(r) for r in consolidated],
                    "total_results": len(consolidated),
                    "providers_used": [p for p in providers if p not in errors],
                    "search_time": round(search_time, 2),
                    "errors": errors
                }
            )
            
        except Exception as e:
            return self.handle_error("paper_search", e)
            
    async def paper_download(
        self,
        paper_id: str,
        provider: str,
        save_path: Union[str, None = None
    ) -> ToolResponse:
        """Download a paper PDF"""
        try:
            if provider not in self.paper_providers:
                return ToolResponse(
                    success=False,
                    error=f"Unknown provider: {provider}. Available: {list(self.paper_providers.keys())}"
                )
                
            provider_obj = self.paper_providers[provider]
            
            # Check if provider supports downloads
            if not hasattr(provider_obj, 'download'):
                return ToolResponse(
                    success=False,
                    error=f"Provider {provider} doesn't support downloads"
                )
                
            save_path = save_path or "./downloads"
            os.makedirs(save_path, exist_ok=True)
            
            file_path = await provider_obj.download(paper_id, save_path)
            
            return ToolResponse(
                success=True,
                data={
                    "file_path": file_path,
                    "provider": provider,
                    "paper_id": paper_id,
                    "message": f"Successfully downloaded to {file_path}"
                }
            )
            
        except Exception as e:
            return self.handle_error(f"paper_download({provider})", e)
            
    async def paper_read(
        self,
        paper_id: str,
        provider: str
    ) -> ToolResponse:
        """Download and extract text from paper"""
        try:
            # First download the paper
            download_result = await self.paper_download(paper_id, provider)
            
            if not download_result.success:
                return download_result
                
            file_path = download_result.data['file_path']
            
            # Extract text from PDF (simplified - in production use proper PDF extraction)
            try:
                # This is a placeholder - you'd use a library like PyPDF2 or pdfplumber
                with open(file_path, 'rb') as f:
                    content = f"[PDF content from {file_path} would be extracted here]"
                    
                return ToolResponse(
                    success=True,
                    data={
                        "paper_id": paper_id,
                        "provider": provider,
                        "file_path": file_path,
                        "content": content,
                        "message": "Note: PDF text extraction not fully implemented"
                    }
                )
                
            except Exception as e:
                return ToolResponse(
                    success=False,
                    error=f"Failed to extract text: {str(e)}"
                )
                
        except Exception as e:
            return self.handle_error(f"paper_read({provider})", e)
    
    async def tavily_extract(
        self,
        urls: List[str],
        extract_depth: str = "basic",
        include_images: bool = False,
        format: str = "markdown",
        include_favicon: bool = False
    ) -> ToolResponse:
        """Extract content from URLs using Tavily"""
        try:
            # Check if Tavily is available
            if 'tavily' not in self.web_providers:
                return ToolResponse(
                    success=False,
                    error="Tavily provider not available. Please configure TAVILY_API_KEY"
                )
            
            tavily_provider = self.web_providers['tavily']
            result = await tavily_provider.extract(
                urls=urls,
                extract_depth=extract_depth,
                include_images=include_images,
                format=format,
                include_favicon=include_favicon
            )
            
            if "error" in result:
                return ToolResponse(
                    success=False,
                    error=result["error"]
                )
            
            return ToolResponse(
                success=True,
                data=result
            )
            
        except Exception as e:
            return self.handle_error("tavily_extract", e)
    
    async def tavily_crawl(
        self,
        url: str,
        max_depth: int = 1,
        max_breadth: int = 20,
        limit: int = 50,
        instructions: Union[str, None = None,
        select_paths: Union[List[str], None = None,
        select_domains: Union[List[str], None = None,
        allow_external: bool = False,
        categories: Union[List[str], None = None,
        extract_depth: str = "basic",
        format: str = "markdown",
        include_favicon: bool = False
    ) -> ToolResponse:
        """Crawl a website using Tavily"""
        try:
            # Check if Tavily is available
            if 'tavily' not in self.web_providers:
                return ToolResponse(
                    success=False,
                    error="Tavily provider not available. Please configure TAVILY_API_KEY"
                )
            
            tavily_provider = self.web_providers['tavily']
            result = await tavily_provider.crawl(
                url=url,
                max_depth=max_depth,
                max_breadth=max_breadth,
                limit=limit,
                instructions=instructions,
                select_paths=select_paths,
                select_domains=select_domains,
                allow_external=allow_external,
                categories=categories,
                extract_depth=extract_depth,
                format=format,
                include_favicon=include_favicon
            )
            
            if "error" in result:
                return ToolResponse(
                    success=False,
                    error=result["error"]
                )
            
            return ToolResponse(
                success=True,
                data=result
            )
            
        except Exception as e:
            return self.handle_error("tavily_crawl", e)
    
    async def tavily_map(
        self,
        url: str,
        max_depth: int = 1,
        max_breadth: int = 20,
        limit: int = 50,
        instructions: Union[str, None = None,
        select_paths: Union[List[str], None = None,
        select_domains: Union[List[str], None = None,
        allow_external: bool = False,
        categories: Union[List[str], None = None
    ) -> ToolResponse:
        """Create a map of website structure using Tavily"""
        try:
            # Check if Tavily is available
            if 'tavily' not in self.web_providers:
                return ToolResponse(
                    success=False,
                    error="Tavily provider not available. Please configure TAVILY_API_KEY"
                )
            
            tavily_provider = self.web_providers['tavily']
            result = await tavily_provider.map(
                url=url,
                max_depth=max_depth,
                max_breadth=max_breadth,
                limit=limit,
                instructions=instructions,
                select_paths=select_paths,
                select_domains=select_domains,
                allow_external=allow_external,
                categories=categories
            )
            
            if "error" in result:
                return ToolResponse(
                    success=False,
                    error=result["error"]
                )
            
            return ToolResponse(
                success=True,
                data=result
            )
            
        except Exception as e:
            return self.handle_error("tavily_map", e)
            
    def _consolidate_results(self, results: List[SearchResult], max_results: int) -> List[SearchResult]:
        """Consolidate and deduplicate web search results"""
        # Simple deduplication by URL
        seen_urls = set()
        unique_results = []
        
        for result in results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                unique_results.append(result)
                
        # Sort by score
        unique_results.sort(key=lambda x: x.score, reverse=True)
        
        return unique_results[:max_results]
        
    def _consolidate_papers(self, results: List[SearchResult], max_results: int) -> List[SearchResult]:
        """Consolidate and deduplicate paper results"""
        # Deduplicate by DOI or title similarity
        seen_dois = set()
        seen_titles = set()
        unique_results = []
        
        for result in results:
            # Skip if we've seen this DOI
            if result.doi and result.doi in seen_dois:
                continue
                
            # Skip if title is too similar to one we've seen
            title_lower = result.title.lower()
            if any(self._similar_titles(title_lower, seen_title) for seen_title in seen_titles):
                continue
                
            if result.doi:
                seen_dois.add(result.doi)
            seen_titles.add(title_lower)
            unique_results.append(result)
            
        # Sort by score
        unique_results.sort(key=lambda x: x.score, reverse=True)
        
        return unique_results[:max_results]
        
    def _similar_titles(self, title1: str, title2: str) -> bool:
        """Check if two titles are similar enough to be duplicates"""
        # Simple similarity check - in production use better algorithm
        if title1 == title2:
            return True
            
        # Check if one is substring of other (common in different versions)
        if title1 in title2 or title2 in title1:
            return True
            
        return False
        
    def _serialize_result(self, result: SearchResult) -> Dict[str, Any]:
        """Convert SearchResult to dictionary"""
        data = {
            "title": result.title,
            "url": result.url,
            "snippet": result.snippet,
            "source": result.source,
            "score": round(result.score, 3)
        }
        
        # Add optional fields if present
        if result.authors:
            data["authors"] = result.authors
        if result.published_date:
            data["published_date"] = result.published_date
        if result.doi:
            data["doi"] = result.doi
        if result.abstract:
            data["abstract"] = result.abstract
        if result.pdf_url:
            data["pdf_url"] = result.pdf_url
        if result.domain:
            data["domain"] = result.domain
        if result.published_time:
            data["published_time"] = result.published_time
        if result.metadata:
            data["metadata"] = result.metadata
            
        return data
