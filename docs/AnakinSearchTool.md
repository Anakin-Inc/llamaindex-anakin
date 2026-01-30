# AnakinSearchTool

The `AnakinSearchTool` is a LlamaIndex tool for performing AI-powered searches with instant answers and citations using the Anakin API.

## Overview

This tool provides:
- AI-powered search with instant answers
- Citations and source references
- Similar functionality to Perplexity AI
- Synchronous operation (fast responses)
- Configurable result limits

## Usage

### Basic Usage

```python
from llamaindex_anakin import AnakinSearchTool

# Initialize the tool
tool = AnakinSearchTool(api_key="your-api-key")

# Convert to LlamaIndex FunctionTool
llama_tool = tool.to_tool()

# Perform a search
result = llama_tool.call(query="What are the latest AI trends in 2026?")
print(result)
```

### With LlamaIndex Agent

```python
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llamaindex_anakin import AnakinSearchTool

# Initialize
search_tool = AnakinSearchTool(api_key="your-api-key").to_tool()
llm = OpenAI(model="gpt-4")

# Create agent
agent = ReActAgent.from_tools(
    tools=[search_tool],
    llm=llm,
    verbose=True,
)

# Use the agent
response = agent.chat("What are the latest developments in quantum computing?")
```

### Advanced Options

```python
# Search with more results
result = llama_tool.call(
    query="Best AI tools for developers",
    max_results=10
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
| `query` | str | **required** | The search query or question |
| `max_results` | int | `5` | Maximum number of results to return |

## Return Format

The tool returns a formatted string containing:

```
Search query: What are the latest AI trends?
Status: success

Answer:
[AI-generated answer with information]...

Citations: 5 sources

Results: 5 items
  1. Title of First Result
  2. Title of Second Result
  3. Title of Third Result
```

## Use Cases

### 1. Research and Fact-Checking

```python
# Get quick facts with citations
result = llama_tool.call(
    query="When was the Transformer architecture introduced?"
)
```

### 2. Competitive Intelligence

```python
# Research competitors
result = llama_tool.call(
    query="What are the main features of Salesforce CRM?"
)
```

### 3. Real-time Information

```python
# Get current information
result = llama_tool.call(
    query="What are the latest updates to GPT models?"
)
```

### 4. Content Research

```python
# Research for content creation
result = llama_tool.call(
    query="Best practices for API design in 2026",
    max_results=10
)
```

## Comparison with Traditional Search

| Feature | Traditional Search | AnakinSearchTool |
|---------|-------------------|------------------|
| Results | List of links | AI-generated answer + sources |
| Processing | Manual review required | Instant synthesis |
| Citations | None | Automatic citations |
| Format | Web pages | Structured response |
| Speed | Fast | Very fast (synchronous) |

## Use with Multiple Queries

```python
queries = [
    "What is LlamaIndex?",
    "How does RAG work?",
    "Best vector databases for AI"
]

for query in queries:
    result = llama_tool.call(query=query)
    print(f"\n{query}")
    print("=" * 80)
    print(result)
    print()
```

## Error Handling

The tool handles errors gracefully:

```python
try:
    result = llama_tool.call(query="")
except Exception as e:
    print(f"Error: {e}")
```

Common errors:
- `ValueError`: Empty query or invalid parameters
- `requests.exceptions.RequestException`: Network errors
- `TimeoutError`: Request timeout

## Performance Considerations

### Response Time

The search tool is synchronous and typically responds in 1-3 seconds:

```python
import time

start = time.time()
result = llama_tool.call(query="AI trends 2026")
elapsed = time.time() - start
print(f"Search completed in {elapsed:.2f} seconds")
```

### Result Quality vs. Quantity

Balance between result count and response time:

```python
# Fast, focused results
result = llama_tool.call(query="...", max_results=3)

# Comprehensive results
result = llama_tool.call(query="...", max_results=10)
```

## Combining with Other Tools

### With Scrape Tool

```python
from llamaindex_anakin import AnakinSearchTool, AnakinScrapeTool

search_tool = AnakinSearchTool(api_key="your-api-key")
scrape_tool = AnakinScrapeTool(api_key="your-api-key")

# First, search for information
search_result = search_tool._search(query="Best AI tools 2026")

# Then scrape specific URLs from results
# (You'd extract URLs from search_result)
scrape_result = scrape_tool._scrape(url="https://example.com")
```

### With Agentic Search

```python
from llamaindex_anakin import AnakinSearchTool, AnakinAgenticSearchTool

# Quick search for overview
search_tool = AnakinSearchTool(api_key="your-api-key")
overview = search_tool._search(query="AI companies")

# Deep research with agentic search
agentic_tool = AnakinAgenticSearchTool(api_key="your-api-key")
detailed = agentic_tool._agentic_search(
    prompt="Find detailed pricing and features of top AI companies"
)
```

## Deployment as Workflow

The search functionality is also available as a deployable workflow:

```bash
llamactl serve
```

Then call via HTTP:

```bash
curl -X POST http://localhost:4501/deployments/llamaindex-anakin/workflows/search/run \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the latest AI trends?",
    "max_results": 5
  }'
```

## Best Practices

1. **Clear Queries**: Use specific, well-formed questions
2. **Appropriate Result Limits**: Start with default (5) and adjust as needed
3. **Error Handling**: Always wrap calls in try-except blocks
4. **Rate Limiting**: Be mindful of API rate limits
5. **Caching**: Cache results for frequently asked questions

## Query Tips

### Good Queries

```python
# Specific and clear
"What are the main features of React 19?"

# Time-bound
"Latest developments in quantum computing in 2026"

# Comparative
"Compare TypeScript vs JavaScript for large projects"
```

### Queries to Avoid

```python
# Too vague
"AI"

# Multiple questions
"What is AI and how does it work and what are the applications?"

# Commands instead of questions
"Tell me about AI"
```

## Examples

See `examples/ai_search.py` for complete working examples.

## Related

- [AnakinScrapeTool](AnakinScrapeTool.md) - Web scraping
- [AnakinAgenticSearchTool](AnakinAgenticSearchTool.md) - Advanced research
- [Search Workflow](workflows/SearchWorkflow.md) - Deployable workflow version
