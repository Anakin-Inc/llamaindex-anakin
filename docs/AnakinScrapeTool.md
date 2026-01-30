# AnakinScrapeTool

The `AnakinScrapeTool` is a LlamaIndex tool for scraping websites and extracting structured data using the Anakin API.

## Overview

This tool provides:
- Full webpage content extraction (HTML and Markdown)
- Automatic structured data extraction
- Proxy support for different countries
- Caching with force-fresh option
- Asynchronous operation with polling

## Usage

### Basic Usage

```python
from llamaindex_anakin import AnakinScrapeTool

# Initialize the tool
tool = AnakinScrapeTool(api_key="your-api-key")

# Convert to LlamaIndex FunctionTool
llama_tool = tool.to_tool()

# Scrape a website
result = llama_tool.call(url="https://example.com")
print(result)
```

### With LlamaIndex Agent

```python
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llamaindex_anakin import AnakinScrapeTool

# Initialize
scrape_tool = AnakinScrapeTool(api_key="your-api-key").to_tool()
llm = OpenAI(model="gpt-4")

# Create agent
agent = ReActAgent.from_tools(
    tools=[scrape_tool],
    llm=llm,
    verbose=True,
)

# Use the agent
response = agent.chat("Scrape https://news.ycombinator.com and summarize the top stories")
```

### Advanced Options

```python
# Scrape with custom parameters
result = llama_tool.call(
    url="https://example.com",
    country="uk",              # Use UK proxy
    force_fresh=True,          # Bypass cache
    max_wait_time=600,         # Wait up to 10 minutes
    poll_interval=5,           # Check every 5 seconds
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
| `url` | str | **required** | The URL to scrape |
| `country` | str | `"us"` | Country code for proxy (us, uk, de, etc.) |
| `force_fresh` | bool | `False` | Bypass cache and force fresh scrape |
| `max_wait_time` | int | `300` | Maximum seconds to wait for completion |
| `poll_interval` | int | `3` | Seconds between status checks |

## Return Format

The tool returns a formatted string containing:

```
Successfully scraped: https://example.com
Status: completed

Content Preview:
[First 500 characters of markdown content]...

Structured Data: {...extracted JSON data...}
```

## Use Cases

### 1. E-commerce Product Extraction

```python
# Extract product details from e-commerce sites
result = llama_tool.call(url="https://amazon.com/product/...")
```

### 2. News Article Scraping

```python
# Scrape news articles for analysis
result = llama_tool.call(url="https://news.example.com/article")
```

### 3. Website Monitoring

```python
# Monitor website changes with force_fresh
result = llama_tool.call(
    url="https://competitor.com",
    force_fresh=True
)
```

### 4. Multi-region Content Access

```python
# Access region-specific content
result = llama_tool.call(
    url="https://example.com",
    country="jp"  # Use Japanese proxy
)
```

## Error Handling

The tool handles errors gracefully:

```python
try:
    result = llama_tool.call(url="https://invalid-url")
except Exception as e:
    print(f"Error: {e}")
```

Common errors:
- `ValueError`: Invalid URL or API response
- `TimeoutError`: Operation exceeded max_wait_time
- `requests.exceptions.RequestException`: Network errors

## Performance Considerations

### Caching

By default, results are cached to improve performance:

```python
# First call - fetches from web
result1 = llama_tool.call(url="https://example.com")

# Second call - uses cache (faster)
result2 = llama_tool.call(url="https://example.com")

# Force fresh scrape
result3 = llama_tool.call(url="https://example.com", force_fresh=True)
```

### Timeouts

Adjust timeouts based on website complexity:

```python
# Quick sites
result = llama_tool.call(url="https://simple.com", max_wait_time=60)

# Complex sites with JavaScript
result = llama_tool.call(url="https://complex.com", max_wait_time=600)
```

### Polling Intervals

Balance between responsiveness and API load:

```python
# Quick checks (more API calls)
result = llama_tool.call(url="https://example.com", poll_interval=1)

# Slower checks (fewer API calls)
result = llama_tool.call(url="https://example.com", poll_interval=10)
```

## Deployment as Workflow

The scraping functionality is also available as a deployable workflow:

```bash
llamactl serve
```

Then call via HTTP:

```bash
curl -X POST http://localhost:4501/deployments/llamaindex-anakin/workflows/scrape/run \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "country": "us",
    "force_fresh": false
  }'
```

## Best Practices

1. **Use Caching**: Don't set `force_fresh=True` unless necessary
2. **Set Appropriate Timeouts**: Estimate based on website complexity
3. **Handle Errors**: Always wrap calls in try-except blocks
4. **Rate Limiting**: Be mindful of API rate limits
5. **Country Selection**: Choose proxies based on target website location

## Examples

See `examples/basic_scraping.py` for complete working examples.

## Related

- [AnakinSearchTool](AnakinSearchTool.md) - AI-powered search
- [AnakinAgenticSearchTool](AnakinAgenticSearchTool.md) - Advanced research
- [Scrape Workflow](workflows/ScrapeWorkflow.md) - Deployable workflow version
