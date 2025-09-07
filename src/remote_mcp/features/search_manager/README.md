# Search Manager Feature

Unified search interface for web and academic paper searches with parallel execution across multiple providers.

## Overview

The Search Manager consolidates multiple search APIs into two simple interfaces:
- **web_search**: For general web searches (Brave, Tavily)
- **paper_search**: For academic papers (ArXiv, PubMed, Semantic Scholar)

All searches execute in parallel for optimal performance, with automatic result consolidation and ranking.

## Quick Start

```python
# Web search across all providers
results = await web_search("python asyncio tutorial")

# Search specific providers
results = await web_search(
    "latest AI developments",
    providers=["tavily"]  # AI-enhanced results
)

# Academic paper search
papers = await paper_search("transformer architecture")

# Download a paper
download = await paper_download(
    paper_id="2106.12345",
    provider="arxiv"
)
```

## Supported Providers

### Web Search Providers
- **Brave**: General web search with privacy focus
- **Tavily**: AI-enhanced search with better context understanding

### Academic Paper Providers
- **ArXiv**: Preprints in physics, mathematics, computer science
- **PubMed**: Biomedical and life science literature
- **Semantic Scholar**: AI-powered academic search with citation data

## Configuration

### Required Environment Variables

```bash
# Web search providers
BRAVE_API_KEY=your_brave_api_key
TAVILY_API_KEY=your_tavily_api_key

# Academic providers (optional - increases rate limits)
PUBMED_API_KEY=your_pubmed_api_key  # Optional
SEMANTIC_SCHOLAR_API_KEY=your_ss_api_key  # Optional
```

### Getting API Keys
- **Brave**: https://brave.com/search/api/
- **Tavily**: https://app.tavily.com/
- **PubMed**: https://www.ncbi.nlm.nih.gov/account/
- **Semantic Scholar**: https://www.semanticscholar.org/product/api

## Architecture

See [ASR-001-unified-search-architecture.md](./ASR-001-unified-search-architecture.md) for detailed architecture documentation.

## Development

### Adding a New Provider

1. Create a new provider class inheriting from `BaseSearchProvider`
2. Implement required methods:
   - `search()`: Execute the search
   - `get_env_requirements()`: Define environment variables
3. Add to appropriate provider dictionary in `SearchManagerEngine`

Example:
```python
class NewSearchProvider(BaseSearchProvider):
    def __init__(self):
        super().__init__("new_provider", timeout=5.0)
        
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        # Implementation
        
    def get_env_requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'NEW_PROVIDER_API_KEY': {
                'required': True,
                'description': 'API key for New Provider',
                'obtain_from': 'https://newprovider.com/api'
            }
        }
```

### Testing

```bash
# Run tests
python -m pytest tests/test_search_manager.py

# Test with environment variables
BRAVE_API_KEY=test_key python test_features.py
```

## API Reference

### web_search

```python
async def web_search(
    query: str,
    providers: Union[List[str], None] = None,
    max_results: int = 10
) -> ToolResponse
```

Search the web using specified providers.

**Parameters:**
- `query`: Search query string
- `providers`: Optional list of providers to use. If None, uses all available.
- `max_results`: Maximum number of results to return (default: 10)

**Returns:** ToolResponse with search results

### paper_search

```python
async def paper_search(
    query: str,
    providers: Union[List[str], None] = None,
    max_results: int = 10
) -> ToolResponse
```

Search academic papers.

**Parameters:**
- `query`: Search query string
- `providers`: Optional list of providers to use
- `max_results`: Maximum number of results to return

**Returns:** ToolResponse with paper results

### paper_download

```python
async def paper_download(
    paper_id: str,
    provider: str,
    save_path: Union[str, None] = None
) -> ToolResponse
```

Download a paper PDF.

**Parameters:**
- `paper_id`: Paper identifier (format depends on provider)
- `provider`: Which provider to use for download
- `save_path`: Directory to save the file (default: "./downloads")

**Returns:** ToolResponse with file path

### paper_read

```python
async def paper_read(
    paper_id: str,
    provider: str
) -> ToolResponse
```

Download and extract text content from a paper.

**Parameters:**
- `paper_id`: Paper identifier
- `provider`: Which provider to use

**Returns:** ToolResponse with extracted text (Note: PDF extraction not fully implemented)

## Result Format

All search results use a unified format:

```python
{
    "query": "search query",
    "results": [
        {
            "title": "Result Title",
            "url": "https://example.com",
            "snippet": "Brief description...",
            "source": "provider_name",
            "score": 0.95,
            
            # For papers
            "authors": ["Author 1", "Author 2"],
            "published_date": "2024-01-01",
            "doi": "10.1234/example",
            "abstract": "Full abstract text...",
            "pdf_url": "https://example.com/paper.pdf",
            
            # For web results
            "domain": "example.com",
            "published_time": "2024-01-01T12:00:00Z"
        }
    ],
    "total_results": 10,
    "providers_used": ["brave", "tavily"],
    "search_time": 2.3,
    "errors": {
        "arxiv": "Connection timeout"
    }
}
```

## Troubleshooting

### No providers available
- Check that required environment variables are set
- Verify API keys are valid
- Check logs for initialization errors

### Timeout errors
- Some providers may be temporarily unavailable
- Searches continue with remaining providers
- Check the `errors` field in the response

### Rate limits
- Add optional API keys for academic providers to increase limits
- Implement caching if making repeated searches

## Future Enhancements

- [ ] Smart provider selection based on query analysis
- [ ] Result caching for repeated queries
- [ ] Advanced deduplication using ML similarity
- [ ] Full PDF text extraction implementation
- [ ] Additional providers (Google Scholar API, CORE, etc.)
- [ ] Query expansion and suggestion features