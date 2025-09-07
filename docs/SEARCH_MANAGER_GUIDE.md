# Search Manager Guide

The Search Manager provides unified access to multiple web and academic search providers through a simple interface. Instead of calling individual search tools, you can search across multiple providers in parallel with a single command.

## Features

- **Unified Interface**: Two simple methods for all your search needs
- **Parallel Execution**: All providers search simultaneously for faster results
- **Smart Consolidation**: Automatic deduplication and ranking of results
- **Graceful Degradation**: Continues working even if some providers fail
- **Flexible Provider Selection**: Use all providers or choose specific ones

## Available Search Tools

### 1. `web_search`
Search the web using multiple providers (Brave, Tavily).

**Parameters:**
- `query` (required): Your search query
- `providers` (optional): List of specific providers to use
  - Available: `["brave", "tavily"]`
  - If not specified, uses all configured providers
- `max_results` (optional): Maximum results to return (default: 10)

**Example:**
```json
{
  "query": "latest developments in quantum computing",
  "max_results": 20
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "query": "latest developments in quantum computing",
    "results": [
      {
        "title": "Google's Quantum Breakthrough...",
        "url": "https://example.com/article",
        "snippet": "Recent advances in quantum error correction...",
        "source": "tavily",
        "score": 0.98,
        "domain": "example.com",
        "published_time": "2025-01-15T10:30:00Z"
      }
    ],
    "total_results": 20,
    "providers_used": ["brave", "tavily"],
    "search_time": 2.3,
    "errors": {}
  }
}
```

### 2. `paper_search`
Search academic papers across multiple databases.

**Parameters:**
- `query` (required): Your search query
- `providers` (optional): List of specific providers to use
  - Available: `["arxiv", "pubmed", "semantic"]`
  - If not specified, uses all available providers
- `max_results` (optional): Maximum results to return (default: 10)

**Example:**
```json
{
  "query": "transformer architecture attention mechanism",
  "providers": ["arxiv", "semantic"],
  "max_results": 15
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "query": "transformer architecture attention mechanism",
    "results": [
      {
        "title": "Attention Is All You Need",
        "url": "https://arxiv.org/abs/1706.03762",
        "snippet": "The dominant sequence transduction models...",
        "source": "arxiv",
        "score": 0.95,
        "authors": ["Vaswani, A.", "Shazeer, N.", "Parmar, N."],
        "published_date": "2017-06-12",
        "doi": "10.48550/arXiv.1706.03762",
        "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",
        "metadata": {
          "arxiv_id": "1706.03762",
          "categories": ["cs.CL", "cs.LG"]
        }
      }
    ],
    "total_results": 15,
    "providers_used": ["arxiv", "semantic"],
    "search_time": 3.1,
    "errors": {}
  }
}
```

### 3. `paper_download`
Download a paper PDF from a specific provider.

**Parameters:**
- `paper_id` (required): Paper identifier
  - ArXiv: Use the arxiv ID (e.g., "1706.03762")
  - PubMed: Use the PMID
  - Semantic Scholar: Use the paper ID
- `provider` (required): Which provider to download from
- `save_path` (optional): Directory to save the file (default: "./downloads")

**Example:**
```json
{
  "paper_id": "1706.03762",
  "provider": "arxiv"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "file_path": "./downloads/1706.03762.pdf",
    "provider": "arxiv",
    "paper_id": "1706.03762",
    "message": "Successfully downloaded to ./downloads/1706.03762.pdf"
  }
}
```

### 4. `paper_read`
Download and extract text content from a paper.

**Parameters:**
- `paper_id` (required): Paper identifier
- `provider` (required): Which provider to use

**Note:** PDF text extraction is not fully implemented yet.

## Provider Details

### Web Search Providers

#### Brave Search
- **Strengths**: Privacy-focused, fast, good general results
- **API Key Required**: Yes
- **Get API Key**: https://brave.com/search/api/

#### Tavily
- **Strengths**: AI-enhanced results, better context understanding, advanced search depth
- **API Key Required**: Yes
- **Get API Key**: https://app.tavily.com/

### Academic Search Providers

#### ArXiv
- **Coverage**: Physics, mathematics, computer science, statistics, and more
- **Strengths**: Free access, preprints, PDF downloads always available
- **API Key Required**: No

#### PubMed
- **Coverage**: Biomedical and life sciences
- **Strengths**: Peer-reviewed articles, medical research
- **API Key Required**: Optional (increases rate limit)
- **Get API Key**: https://www.ncbi.nlm.nih.gov/account/

#### Semantic Scholar
- **Coverage**: All academic disciplines
- **Strengths**: AI-powered, citation data, influence metrics
- **API Key Required**: Optional (increases rate limit)
- **Get API Key**: https://www.semanticscholar.org/product/api

## Configuration

Set these environment variables before starting the server:

```bash
# Required for web search
export BRAVE_API_KEY="your_brave_api_key"
export TAVILY_API_KEY="your_tavily_api_key"

# Optional for academic search (increases rate limits)
export PUBMED_API_KEY="your_pubmed_api_key"
export SEMANTIC_SCHOLAR_API_KEY="your_api_key"
```

## Usage Tips

### 1. Let the System Choose Providers
For most cases, don't specify providers - let the system use all available ones:
```json
{
  "query": "machine learning best practices"
}
```

### 2. Use Specific Providers for Targeted Results
When you know which source is best:
```json
{
  "query": "COVID-19 vaccine efficacy",
  "providers": ["pubmed"]
}
```

### 3. Combine Web and Academic Searches
For comprehensive research, run both:
```python
# Get general web information
web_results = web_search("quantum computing applications")

# Get academic papers
papers = paper_search("quantum computing applications")
```

### 4. Handle Provider Failures
Always check the `errors` field to see if any providers failed:
```python
if result["data"]["errors"]:
    print("Some providers failed:", result["data"]["errors"])
```

## Understanding Results

### Scoring
- Results are scored from 0 to 1 based on:
  - Provider ranking (position in original results)
  - Provider weight (Tavily gets 1.2x boost for AI enhancement)
  - Consolidation algorithm

### Deduplication
- Web results: Deduplicated by URL
- Papers: Deduplicated by DOI or title similarity

### Error Handling
- Individual provider failures don't stop the search
- Failed providers are listed in the `errors` field
- The search continues with available providers

## Examples

### Research a Topic Comprehensively
```python
# Search web for current information
web = web_search("large language models applications 2025")

# Find academic papers
papers = paper_search("large language models applications")

# Download interesting papers
for paper in papers["data"]["results"][:3]:
    if paper.get("pdf_url") and paper["source"] == "arxiv":
        download = paper_download(
            paper_id=paper["metadata"]["arxiv_id"],
            provider="arxiv"
        )
```

### Quick News Search with AI Enhancement
```python
# Use only Tavily for AI-enhanced news understanding
news = web_search(
    "AI regulation news January 2025",
    providers=["tavily"]
)
```

### Medical Research
```python
# Search PubMed specifically for medical papers
studies = paper_search(
    "mRNA vaccine long-term effects",
    providers=["pubmed"],
    max_results=20
)
```

## Troubleshooting

### "No providers available" Error
- Check that you've set the required environment variables
- Verify your API keys are valid
- Look at server logs for initialization errors

### Slow Searches
- Normal search time is 2-5 seconds
- Tavily might be slower due to AI processing
- Academic searches may take longer with many results

### Missing Results
- Some providers may be temporarily down
- Check the `errors` field in the response
- Try searching with specific providers that are working

### Rate Limits
- Add optional API keys to increase limits
- Implement caching for repeated searches
- Space out requests if hitting limits