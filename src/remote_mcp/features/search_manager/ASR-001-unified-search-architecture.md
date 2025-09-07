# ASR-001: Unified Search Architecture

**Date**: 2025-09-07  
**Status**: Implemented  
**Author**: Ivan  
**Feature**: Search Manager  

## Context

The toolset-mcp project needed a unified way to search across multiple web and academic paper providers. Previously, users would need to call individual search tools (Brave, Tavily, ArXiv, PubMed, etc.) separately, leading to:
- Inefficient sequential searches
- Inconsistent result formats
- Complex integration logic in client code
- Manual result consolidation

## Decision

We implemented a Unified Search Manager that:
1. Consolidates all search providers under two simple methods: `web_search` and `paper_search`
2. Executes searches in parallel for optimal performance
3. Provides consistent result formatting across all providers
4. Handles provider failures gracefully
5. Maintains the ability to call specific providers when needed

### Architecture Overview

```
SearchManagerEngine
├── Web Providers
│   ├── BraveSearchProvider (refer to: `M:\ref_projects\brave-search-mcp-server`)
│   └── TavilySearchProvider (refere to: `M:\ref_projects\tavily-mcp`)
│   └── SearxngSearchProvider (refer to: `M:\ref_projects\SearXNG-MCP`)
└── Paper Providers (refer to: `M:\ref_projects\paper-search-mcp`)
    ├── ArxivSearchProvider
    ├── PubMedSearchProvider
    └── SemanticScholarProvider
```

### Key Design Decisions

1. **Two Simple Methods**: Instead of exposing all providers as separate tools, we provide just `web_search` and `paper_search`, dramatically simplifying the API surface.

2. **Parallel Execution**: All selected providers run concurrently using `asyncio.gather()`, with individual timeout handling.

3. **Optional Provider Selection**: Users can specify which providers to use, or let the system use all available providers.

4. **Graceful Degradation**: If a provider fails or isn't configured, the search continues with remaining providers.

5. **No Optional[] Usage**: Due to FastMCP limitations, we use `Union[List[str], None]` instead of `Optional[]`.

6. **Environment-Based Configuration**: Each provider validates its required environment variables on initialization.

## Implementation Details

### Base Provider Pattern

```python
class BaseSearchProvider(ABC):
    def __init__(self, name: str, timeout: float = 5.0)
    
    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]
    
    @abstractmethod
    def get_env_requirements(self) -> Dict[str, Dict[str, Any]]
    
    def validate_env(self) -> None
```

### Unified Result Format

```python
@dataclass
class SearchResult:
    # Common fields
    title: str
    url: str
    snippet: str
    source: str
    score: float
    
    # Paper-specific
    authors: Union[List[str], None]
    published_date: Union[str, None]
    doi: Union[str, None]
    abstract: Union[str, None]
    pdf_url: Union[str, None]
    
    # Web-specific
    domain: Union[str, None]
    published_time: Union[str, None]
```

### Parallel Search Pattern

```python
async def web_search(self, query: str, providers: Union[List[str], None] = None, max_results: int = 10):
    # Determine providers
    if providers is None:
        providers = list(self.web_providers.keys())
    
    # Run in parallel
    tasks = []
    for provider_name in providers:
        provider = self.web_providers[provider_name]
        task = provider.search(query, max_results)
        tasks.append((provider_name, task))
    
    # Gather with error handling
    results = await asyncio.gather(*[t[1] for t in tasks], return_exceptions=True)
```

## Environment Configuration

### Required Environment Variables

```yaml
# Web Providers
BRAVE_API_KEY: Required for Brave search
TAVILY_API_KEY: Required for Tavily AI-enhanced search
SEARXNG_SERVER_URL: Required for SearXNG meta-search (self-hosted or public instance)

# Paper Providers (Optional - increase rate limits)
PUBMED_API_KEY: Optional for PubMed
SEMANTIC_SCHOLAR_API_KEY: Optional for Semantic Scholar
```

### Caprover Deployment

The system is designed for easy deployment on Caprover with environment variable injection:

```yaml
environment:
  BRAVE_API_KEY: "$$cap_brave_api_key"
  TAVILY_API_KEY: "$$cap_tavily_api_key"
  SEARXNG_SERVER_URL: "$$cap_searxng_server_url"
  PUBMED_API_KEY: "$$cap_pubmed_api_key"
  SEMANTIC_SCHOLAR_API_KEY: "$$cap_semantic_api_key"
```

## Result Consolidation

### Deduplication Strategy

1. **Web Results**: Deduplicate by URL
2. **Paper Results**: Deduplicate by DOI or title similarity

### Ranking Algorithm

- Base scoring from provider (position-based)
- Provider weights (e.g., Tavily gets 1.2x boost for AI enhancement)
- Sort by final score, return top N results

## Error Handling

Each provider failure is isolated and recorded:
```python
{
    "providers_used": ["brave", "tavily"],
    "errors": {
        "arxiv": "Connection timeout"
    }
}
```

## Usage Examples

### Simple Web Search
```python
# Search all available web providers
results = await search_manager.web_search("python asyncio tutorial")
```

### Targeted Paper Search
```python
# Search specific academic databases
papers = await search_manager.paper_search(
    "transformer neural networks",
    providers=["arxiv", "semantic"]
)
```

### Paper Download
```python
# Download a paper PDF
result = await search_manager.paper_download(
    paper_id="2106.12345",
    provider="arxiv",
    save_path="./downloads"
)
```

## Future Enhancements

1. **Additional Providers**: Easy to add new providers following the base pattern
2. **Smart Provider Selection**: Automatically choose providers based on query type
3. **Result Caching**: Cache results for repeated queries
4. **Advanced Deduplication**: Use ML-based similarity for better duplicate detection
5. **PDF Text Extraction**: Implement proper PDF parsing for `paper_read` functionality

## Consequences

### Positive
- Simplified API with just two main search methods
- Significant performance improvement through parallelization
- Consistent result format across all providers
- Easy to add new providers
- Graceful handling of provider failures

### Negative
- Slightly more complex internal implementation
- Requires careful environment configuration
- Some provider-specific features might be hidden in the unified interface

## Lessons Learned

1. **Parallel by Default**: For I/O-bound operations like API calls, parallel execution should be the default
2. **Graceful Degradation**: Systems should continue functioning even when some components fail
3. **Simple APIs Win**: Two well-designed methods are better than exposing ten individual providers
4. **Environment Validation**: Validate configuration early and provide clear error messages