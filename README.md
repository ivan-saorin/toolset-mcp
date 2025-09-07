# Atlas Toolset MCP - Enhanced Utility Toolset Server

A modular FastMCP server providing enhanced utility tools including advanced calculator, text analyzer, task manager, time utilities with Italian format support, path converter for Windows/Linux compatibility, and unified search capabilities for web and academic papers.

## Architecture

The server follows a clean modular architecture:

```
src/remote_mcp/
├── server.py              # Main FastMCP server
├── shared/                # Shared components
│   ├── base.py           # Base classes for features
│   └── types.py          # Common type definitions
└── features/             # Feature implementations
    ├── calculator/       # Advanced calculator
    ├── text_analyzer/    # Text analysis tools
    ├── task_manager/     # Task management system
    ├── time/             # Time utilities with Italian format
    ├── path_converter/   # Windows/Linux path conversion
    └── search_manager/   # Unified web and paper search
```

## Features

### 🧮 Calculator (Enhanced)

Advanced mathematical operations beyond basic arithmetic:

- **Basic Operations**: add, subtract, multiply, divide, power, modulo
- **Scientific**: sqrt, factorial, logarithms, trigonometry
- **Statistical**: mean, median, mode, standard deviation, variance
- **Financial**: compound interest, loan payments, ROI, present value
- **Expression Evaluation**: Safe evaluation of mathematical expressions
- **History Tracking**: Keeps track of calculations

**Tools:**
- `calculate` - Basic and scientific operations
- `calculate_advanced` - Evaluate expressions with variables
- `calculate_statistics` - Statistical analysis on datasets
- `calculate_financial` - Financial calculations

### 📝 Text Analyzer (Enhanced)

Comprehensive text analysis with multiple modes:

- **Basic Analysis**: Character/word/sentence counts
- **Detailed Analysis**: Lexical diversity, frequency analysis
- **Readability**: Flesch Reading Ease score and grade level
- **Sentiment Analysis**: Positive/negative/neutral classification
- **Keyword Extraction**: Top keywords, bigrams, proper nouns
- **Text Comparison**: Similarity metrics between texts
- **Information Extraction**: URLs, emails, numbers, dates, hashtags
- **Text Transformation**: Case conversion, formatting, cleaning

**Tools:**
- `text_analyze` - Multi-mode text analysis
- `text_compare` - Compare two texts
- `text_extract` - Extract specific information
- `text_transform` - Transform text formatting

### ✅ Task Manager (Enhanced)

Advanced task management with dependencies and tracking:

- **Priority Levels**: low, medium, high, urgent, critical
- **Status Tracking**: pending, in_progress, blocked, review, completed, cancelled, archived
- **Categories & Tags**: Organize tasks with categories and multiple tags
- **Dependencies**: Tasks can depend on other tasks
- **Time Tracking**: Estimated vs actual hours
- **Due Dates**: Track deadlines and overdue tasks
- **Statistics**: Comprehensive productivity metrics

**Tools:**
- `task_create` - Create tasks with advanced options
- `task_list` - List and filter tasks
- `task_update` - Update task properties
- `task_delete` - Delete tasks
- `task_complete` - Mark tasks as complete with tracking
- `task_stats` - Get productivity statistics

### 🕐 Time Utilities (Italian Format)

Time and date utilities with Italian format and advanced shortcuts:

#### Date Formats
- **Italian**: `DD/MM/YYYY HH:mm:ss` (e.g., `05/09/2025 20:06:00`)
- **ISO**: Standard ISO format
- **US**: `MM/DD/YYYY HH:mm:ss`
- **Full Italian**: With day and month names (e.g., `venerdì 5 settembre 2025, 20:06:00`)

#### Date Shortcuts
Simple shortcuts that can be combined:
- `now` - Current datetime
- `yesterday` - 24 hours ago
- `tomorrow` - 24 hours ahead
- `last_month` - Same day last month
- `next_month` - Same day next month
- `EoD` - End of Day (23:59:59)
- `EoM` - End of Month
- `SoD` - Start of Day (00:00:00)
- `SoM` - Start of Month

#### Compound Shortcuts
Combine shortcuts for complex dates:
- `tomorrow EoD` → Tomorrow at 23:59:59
- `next month EoM` → Last day of next month at current time
- `yesterday SoD` → Yesterday at 00:00:00

#### Date Calculations
- Calculate differences between dates with detailed statistics
- Add/subtract time with any unit (seconds to years)
- Working days and weekend calculations
- Quarter and week-of-year information

**Tools:**
- `time_now` - Get current date/time in any format
- `time_parse` - Parse shortcuts like "tomorrow EoD"
- `time_calculate` - Calculate date differences with statistics
- `time_add` - Add/subtract time from dates
- `time_format` - Convert between date formats

### 🔄 Path Converter (NEW)

Convert between Windows and Linux path formats with configurable drive mapping:

- **Auto-detection**: Automatically detects path format and converts to the opposite
- **Batch conversion**: Convert multiple paths in one operation
- **Path validation**: Validate paths and see both Windows and Linux formats
- **VS Code integration**: Perfect for copying paths from VS Code on Windows
- **Configurable drive**: Use `MCP_WINDOWS_DRIVE` environment variable (default: M)

**Path Mapping:**
- Windows: `M:\projects\myproject` (or configured drive)
- Linux: `/mcp/projects/myproject`

**Tools:**
- `convert_path` - Convert a single path
- `convert_multiple_paths` - Convert multiple paths at once
- `validate_path` - Validate and show both formats

### 🔍 Search Manager (NEW)

Unified search interface for web and academic papers with parallel execution:

- **Web Search**: Search across multiple providers (Brave, Tavily) in parallel
- **Paper Search**: Search academic databases (ArXiv, PubMed, Semantic Scholar)
- **Parallel Execution**: All providers run concurrently for optimal performance
- **Result Consolidation**: Automatic deduplication and ranking
- **PDF Download**: Download papers directly from supported providers
- **Graceful Degradation**: Continues with available providers if some fail

**Supported Providers:**
- **Web**: Brave (privacy-focused), Tavily (AI-enhanced), SearXNG (meta-search)
- **Academic**: ArXiv (preprints), PubMed (biomedical), Semantic Scholar (AI-powered)

**Tools:**
- `web_search` - Search the web across multiple providers
- `paper_search` - Search academic papers
- `paper_download` - Download paper PDFs
- `paper_read` - Extract text from papers (limited)

## Usage Examples

### Calculator Examples
```python
# Basic calculation
await calculate(10, 5, "multiply")  # 10 × 5 = 50

# Advanced expression
await calculate_advanced("2 * pi * r", {"r": 5})  # 31.416...

# Statistics
await calculate_statistics([1, 2, 3, 4, 5], ["mean", "stdev"])

# Financial
await calculate_financial("compound_interest", {
    "principal": 1000,
    "rate": 5,  # 5%
    "time": 10,  # years
    "compounds_per_year": 12
})
```

### Text Analyzer Examples
```python
# Analyze readability
await text_analyze("Your text here", mode="readability")

# Compare two texts
await text_compare("Text 1", "Text 2")

# Extract emails
await text_extract("Contact: john@example.com", "emails")

# Transform to snake_case
await text_transform("Hello World Example", "snake_case")
```

### Task Manager Examples
```python
# Create a high-priority task with deadline
await task_create(
    title="Deploy new feature",
    priority="high",
    category="development",
    tags=["backend", "urgent"],
    due_date="2025-09-10",
    estimated_hours=8
)

# List overdue tasks
await task_list(overdue=True)

# Complete a task with tracking
await task_complete("task_0001", 
    completion_notes="Deployed successfully",
    actual_hours=6.5
)

# Get productivity stats
await task_stats()
```

### Time Examples
```python
# Get current time in Italian format
await time_now(format="italian")
# Output: {"datetime": "05/09/2025 20:06:00", ...}

# Parse shortcut
await time_parse("tomorrow EoD")
# Output: {"datetime": "06/09/2025 23:59:59", ...}

# Calculate date difference
await time_calculate("now", "next month EoM", unit="days")

# Add time
await time_add("now", 45, unit="days", format="italian")

# Format conversion
await time_format("2025-09-05", input_format="iso", output_format="full_italian")
# Output: "venerdì 5 settembre 2025, 00:00:00"
```

### Path Converter Examples
```python
# Convert Windows path to Linux
await convert_path("M:\\projects\\toolset-mcp\\README.md")
# Output: {
#   "original": "M:\\projects\\toolset-mcp\\README.md",
#   "converted": "/mcp/projects/toolset-mcp/README.md",
#   "detected_type": "windows",
#   "conversion": "windows_to_linux"
# }

# Convert Linux path to Windows
await convert_path("/mcp/projects/atlas-meta/akasha")
# Output: {
#   "original": "/mcp/projects/atlas-meta/akasha",
#   "converted": "M:\\projects\\atlas-meta\\akasha",
#   "detected_type": "linux",
#   "conversion": "linux_to_windows"
# }

# Convert multiple paths
await convert_multiple_paths([
    "M:\\projects\\project1",
    "/mcp/data/file.txt",
    "M:\\workspace\\test"
])

# Validate and show both formats
await validate_fs_path("M:\\projects\\toolset-mcp\\src")
# Output: {
#   "windows_format": "M:\\projects\\toolset-mcp\\src",
#   "linux_format": "/mcp/projects/toolset-mcp/src",
#   "ready_to_copy": {
#     "windows": "M:\\projects\\toolset-mcp\\src",
#     "linux": "/mcp/projects/toolset-mcp/src"
#   }
# }
```

### Search Manager Examples
```python
# Search the web across all available providers
await web_search("python asyncio best practices")
# Returns results from Brave and Tavily in parallel

# Search specific providers
await web_search(
    "latest AI developments 2025",
    providers=["tavily"],  # AI-enhanced search
    max_results=20
)

# Search academic papers
await paper_search("transformer neural networks attention")
# Searches ArXiv, PubMed, and Semantic Scholar

# Search specific academic databases
await paper_search(
    "COVID-19 vaccine efficacy",
    providers=["pubmed", "semantic"],
    max_results=15
)

# Download a paper
await paper_download(
    paper_id="2106.12345",  # ArXiv ID
    provider="arxiv",
    save_path="./research/papers"
)

# Read paper content (limited PDF extraction)
await paper_read(
    paper_id="2106.12345",
    provider="arxiv"
)
```

## Running the Server

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python -m src.remote_mcp.server
```

### Endpoints
- **MCP Interface**: `http://localhost:8000/mcp`
- **Health Check**: `http://localhost:8000/health`

### Docker Deployment
```bash
# Build and run with Docker
docker build -t atlas-toolset-mcp .
docker run -p 8000:8000 atlas-toolset-mcp
```

## Integration with Claude Desktop

Configure in Claude Desktop settings:

```json
{
  "mcpServers": {
    "toolset": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

For remote deployment:
```json
{
  "mcpServers": {
    "toolset": {
      "url": "https://your-domain.com/mcp"
    }
  }
}
```

## System Information

Use `system_info()` to get server status and capabilities:
- Server version
- Feature versions and capabilities
- Available operations and modes
- Supported formats and shortcuts

## Advanced Features

### Calculator Memory
The calculator maintains a history of calculations that can be retrieved for reference.

### Task Dependencies
Tasks can depend on other tasks, automatically managing blocking states when dependencies aren't complete.

### Text Sentiment Analysis
Analyzes emotional tone of text using positive/negative word detection.

### Date Statistics
When calculating date differences, get comprehensive statistics including:
- Working days vs weekends
- Breakdown by years/months/days/hours
- Quarter and week-of-year information

## Performance

All features are optimized for:
- Fast response times
- Memory efficiency
- Concurrent operation support
- Error recovery and validation

## Error Handling

All tools return structured responses with:
- `success`: Boolean indicating success/failure
- `data`: Result data when successful
- `error`: Error message when failed
- `metadata`: Additional context information

## License

MIT License

## Based On

- FastMCP framework for Model Context Protocol
- Enhanced implementations of common utility tools
