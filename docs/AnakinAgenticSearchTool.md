# AnakinAgenticSearchTool

The `AnakinAgenticSearchTool` is an advanced LlamaIndex tool that performs multi-stage AI pipeline operations: automatic searching, scraping, and structured data extraction using the Anakin API.

## Overview

This tool provides:
- Multi-stage AI pipeline (search → scrape → extract)
- Automatic URL discovery and scraping
- Structured data extraction
- Browser-based scraping support
- Comprehensive research capabilities
- Asynchronous operation with polling

## Usage

### Basic Usage

```python
from llamaindex_anakin import AnakinAgenticSearchTool

# Initialize the tool
tool = AnakinAgenticSearchTool(api_key="your-api-key")

# Convert to LlamaIndex FunctionTool
llama_tool = tool.to_tool()

# Perform agentic search
result = llama_tool.call(
    prompt="Find pricing information for the top 5 project management tools"
)
print(result)
```

### With LlamaIndex Agent

```python
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llamaindex_anakin import AnakinAgenticSearchTool

# Initialize
agentic_tool = AnakinAgenticSearchTool(api_key="your-api-key").to_tool()
llm = OpenAI(model="gpt-4")

# Create agent
agent = ReActAgent.from_tools(
    tools=[agentic_tool],
    llm=llm,
    verbose=True,
)

# Use the agent
response = agent.chat(
    "Compare features and pricing of Salesforce, HubSpot, and Zoho CRM"
)
```

### Advanced Options

```python
# Agentic search with custom parameters
result = llama_tool.call(
    prompt="Research AI companies and their valuations",
    use_browser=True,        # Use browser for JavaScript sites
    max_wait_time=900,       # Wait up to 15 minutes
    poll_interval=10,        # Check every 10 seconds
)
```

## Parameters

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | str | **required** | Your Anakin API key |
| `base_url` | str | `"https://api.anakin.io"` | Base URL for Anakin API |

### Function Parameters

When calling the tool:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | str | **required** | The research prompt or question |
| `use_browser` | bool | `True` | Whether to use browser for scraping |
| `max_wait_time` | int | `600` | Maximum seconds to wait (10 minutes) |
| `poll_interval` | int | `5` | Seconds between status checks |

## Return Format

The tool returns a formatted string containing:

```
Agentic search completed for: [your prompt]
Status: completed

Search Results: 10 items

Extracted Data: {...structured JSON data...}

Scraped 5 pages
```

## How It Works

The agentic search follows a multi-stage pipeline:

1. **Search Phase**: AI searches the web for relevant information
2. **URL Discovery**: Identifies the most relevant URLs to scrape
3. **Scraping Phase**: Scrapes discovered URLs (with browser if needed)
4. **Extraction Phase**: Extracts structured data from scraped content
5. **Synthesis**: Combines all information into a structured result

```
Prompt → Search → URLs → Scrape → Extract → Result
```

## Use Cases

### 1. Comprehensive Market Research

```python
# Research market landscape
result = llama_tool.call(
    prompt="Find and compare the top 10 CRM platforms including pricing, features, and customer reviews"
)
```

### 2. Competitive Analysis

```python
# Analyze competitors
result = llama_tool.call(
    prompt="Compare Salesforce, HubSpot, and Zoho CRM: pricing tiers, key features, and market positioning"
)
```

### 3. Lead Generation with Enrichment

```python
# Find and enrich leads
result = llama_tool.call(
    prompt="Find the top 20 AI startups in San Francisco with their funding, team size, and contact information"
)
```

### 4. Automated Data Collection

```python
# Collect structured data
result = llama_tool.call(
    prompt="Gather pricing information, feature lists, and user ratings for project management tools"
)
```

### 5. Multi-source Information Synthesis

```python
# Synthesize from multiple sources
result = llama_tool.call(
    prompt="Research the current state of quantum computing: key players, recent breakthroughs, and commercial applications"
)
```

## Browser vs Non-Browser Mode

### Non-Browser Mode (Faster)

```python
# Good for static content sites
result = llama_tool.call(
    prompt="Find contact information for tech companies",
    use_browser=False
)
```

**Advantages:**
- Faster execution
- Lower resource usage
- Good for static HTML

**Disadvantages:**
- Cannot handle JavaScript-heavy sites
- May miss dynamically loaded content

### Browser Mode (More Comprehensive)

```python
# Required for dynamic content
result = llama_tool.call(
    prompt="Scrape pricing from modern SaaS websites",
    use_browser=True
)
```

**Advantages:**
- Handles JavaScript-rendered content
- Can interact with dynamic elements
- More comprehensive data extraction

**Disadvantages:**
- Slower execution
- Higher resource usage

## Performance Considerations

### Timeouts

Agentic search is the most time-intensive operation. Adjust timeouts based on task complexity:

```python
# Simple research (default)
result = llama_tool.call(
    prompt="Find top 3 AI tools",
    max_wait_time=600  # 10 minutes
)

# Complex research with many sources
result = llama_tool.call(
    prompt="Comprehensive market analysis of 20 companies",
    max_wait_time=1800  # 30 minutes
)
```

### Poll Intervals

Balance between responsiveness and API load:

```python
# Frequent checks (more responsive)
result = llama_tool.call(
    prompt="...",
    poll_interval=3
)

# Infrequent checks (fewer API calls)
result = llama_tool.call(
    prompt="...",
    poll_interval=10
)
```

## Error Handling

The tool handles errors gracefully:

```python
try:
    result = llama_tool.call(
        prompt="Your research prompt",
        max_wait_time=300
    )
except TimeoutError as e:
    print(f"Research took too long: {e}")
except ValueError as e:
    print(f"Invalid parameters: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Progressive Research Pattern

For complex research, break into stages:

```python
from llamaindex_anakin import (
    AnakinSearchTool,
    AnakinScrapeTool,
    AnakinAgenticSearchTool,
)

# Stage 1: Quick overview
search_tool = AnakinSearchTool(api_key="your-api-key")
overview = search_tool._search(query="AI companies overview")

# Stage 2: Detailed research
agentic_tool = AnakinAgenticSearchTool(api_key="your-api-key")
detailed = agentic_tool._agentic_search(
    prompt="Find detailed information about the top 5 AI companies from the overview"
)

# Stage 3: Specific data scraping (if needed)
scrape_tool = AnakinScrapeTool(api_key="your-api-key")
specific = scrape_tool._scrape(url="https://specific-company.com/pricing")
```

## Structured Data Extraction

The tool automatically extracts structured data:

```python
result = llama_tool.call(
    prompt="Find pricing tiers for CRM platforms"
)

# Result includes:
# - searchResults: Initial search findings
# - extractedData: Structured JSON with pricing info
# - scrapedContent: Raw scraped content from each page
```

Example extracted data structure:

```json
{
  "companies": [
    {
      "name": "Salesforce",
      "pricing": {
        "starter": "$25/user/month",
        "professional": "$75/user/month",
        "enterprise": "$150/user/month"
      },
      "features": ["CRM", "Marketing", "Analytics"]
    }
  ]
}
```

## Deployment as Workflow

The agentic search functionality is also available as a deployable workflow:

```bash
llamactl serve
```

Then call via HTTP:

```bash
curl -X POST http://localhost:4501/deployments/llamaindex-anakin/workflows/agentic-search/run \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Find pricing for top 5 CRM tools",
    "use_browser": true,
    "max_wait_time": 600
  }'
```

## Best Practices

1. **Clear Prompts**: Be specific about what data you want extracted
2. **Appropriate Timeouts**: Complex research needs more time
3. **Browser Mode Selection**: Use browser only when necessary
4. **Error Handling**: Always implement timeout and error handling
5. **Progressive Research**: Break complex research into stages
6. **Rate Limiting**: Be mindful of API rate limits
7. **Data Validation**: Validate extracted structured data

## Prompt Engineering Tips

### Good Prompts

```python
# Specific and structured
"Find the pricing tiers, key features, and customer count for Salesforce, HubSpot, and Zoho CRM"

# Clear data requirements
"Research the top 10 AI companies: company name, funding amount, founding year, and main product"

# Time-bound
"Gather Q4 2025 revenue data for major cloud providers"
```

### Prompts to Avoid

```python
# Too vague
"Find information about companies"

# No structure
"Tell me about CRM tools"

# Too broad
"Research everything about AI"
```

## Monitoring Long-Running Operations

For operations that take significant time:

```python
import time

print("Starting agentic search...")
start_time = time.time()

try:
    result = llama_tool.call(
        prompt="Comprehensive market research on 20 AI companies",
        max_wait_time=1800,  # 30 minutes
        poll_interval=10
    )
    
    elapsed = time.time() - start_time
    print(f"Completed in {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
    
except TimeoutError:
    elapsed = time.time() - start_time
    print(f"Timed out after {elapsed:.2f} seconds")
    print("Consider increasing max_wait_time or simplifying the prompt")
```

## Examples

See `examples/agentic_search.py` for complete working examples.

## Related

- [AnakinScrapeTool](AnakinScrapeTool.md) - Web scraping
- [AnakinSearchTool](AnakinSearchTool.md) - AI-powered search
- [Agentic Search Workflow](workflows/AgenticSearchWorkflow.md) - Deployable workflow version

## Troubleshooting

### Operation Times Out

- Increase `max_wait_time`
- Simplify the research prompt
- Break into smaller stages

### Incomplete Data

- Enable browser mode: `use_browser=True`
- Make prompt more specific
- Increase wait time

### Rate Limiting

- Add delays between calls
- Use caching when possible
- Consider progressive research pattern
