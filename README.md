# llamaindex-anakin

LlamaIndex integration for [Anakin AI](https://anakin.io) - powerful web scraping, AI-powered search, and intelligent data extraction tools and workflows for your LlamaIndex applications.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🔧 **Three Powerful LlamaIndex Tools**:
  - `AnakinScrapeTool` - Scrape websites and extract structured data
  - `AnakinSearchTool` - AI-powered search with Perplexity AI
  - `AnakinAgenticSearchTool` - Advanced multi-stage AI pipeline for comprehensive research
- 📊 **Three Deployable Workflows**:
  - Scrape Workflow - Server-side URL scraping workflow
  - Search Workflow - AI-powered search workflow
  - Agentic Search Workflow - Multi-stage research workflow
- 🚀 **Easy Deployment** with `llamactl` to LlamaCloud
- 🔐 Simple authentication with API key
- 📦 Easy integration with LlamaIndex agents and workflows
- ⚡ Asynchronous operations with automatic polling
- 🎯 Type-safe with Pydantic models
- 📖 Comprehensive documentation and examples

## Installation

```bash
pip install llamaindex-anakin
```

Or install from source:

```bash
git clone https://github.com/Anakin-Inc/llamaindex-anakin.git
cd llamaindex-anakin
pip install -e .
```

## Quick Start

### 1. Get Your API Key

Sign up at [Anakin.io](https://anakin.io) to get your API key.

### 2. Set Up Environment

Create a `.env` file:

```bash
cp .env.template .env
```

Add your API key:

```
ANAKIN_API_KEY=your-anakin-api-key-here
```

### 3. Use the Tools

```python
from llamaindex_anakin import AnakinScrapeTool, AnakinSearchTool, AnakinAgenticSearchTool

# Initialize tools with your API key
api_key = "your-anakin-api-key"

scrape_tool = AnakinScrapeTool(api_key=api_key)
search_tool = AnakinSearchTool(api_key=api_key)
agentic_tool = AnakinAgenticSearchTool(api_key=api_key)

# Use with LlamaIndex agents
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-4", temperature=0)

agent = ReActAgent.from_tools(
    tools=[
        scrape_tool.to_tool(),
        search_tool.to_tool(),
        agentic_tool.to_tool(),
    ],
    llm=llm,
    verbose=True,
)

# Ask the agent to use the tools
response = agent.chat(
    "Search for the latest AI trends and scrape the top 3 sources"
)
```

## Tools Overview

### 1. AnakinScrapeTool

Scrape websites and extract content including HTML, markdown, and structured data.

```python
from llamaindex_anakin import AnakinScrapeTool

tool = AnakinScrapeTool(api_key="your-api-key")
llama_tool = tool.to_tool()

# Use with agent or directly
result = llama_tool.call(url="https://example.com/product")
print(result)
```

**Parameters:**
- `url` (required): Website URL to scrape
- `country` (optional): Proxy country code (default: "us")
- `force_fresh` (optional): Bypass cache (default: False)
- `max_wait_time` (optional): Max seconds to wait (default: 300)
- `poll_interval` (optional): Seconds between checks (default: 3)

**Use Cases:**
- Extract product information from e-commerce sites
- Scrape article content for analysis
- Monitor website changes
- Gather structured data from web pages

### 2. AnakinSearchTool

Perform AI-powered searches with instant answers and citations.

```python
from llamaindex_anakin import AnakinSearchTool

tool = AnakinSearchTool(api_key="your-api-key")
llama_tool = tool.to_tool()

# Use with agent or directly
result = llama_tool.call(
    query="What are the latest developments in quantum computing?",
    max_results=5,
)
print(result)
```

**Parameters:**
- `query` (required): Search question or query
- `max_results` (optional): Maximum results to return (default: 5)

**Use Cases:**
- Research and fact-checking
- Competitive intelligence
- Real-time information gathering
- Content research

### 3. AnakinAgenticSearchTool

Advanced multi-stage AI pipeline that automatically searches, scrapes, and extracts structured data.

```python
from llamaindex_anakin import AnakinAgenticSearchTool

tool = AnakinAgenticSearchTool(api_key="your-api-key")
llama_tool = tool.to_tool()

# Use with agent or directly
result = llama_tool.call(
    prompt="Find pricing information for top 5 project management tools",
    use_browser=True,
)
print(result)
```

**Parameters:**
- `prompt` (required): Research prompt or question
- `use_browser` (optional): Use browser for scraping (default: True)
- `max_wait_time` (optional): Max seconds to wait (default: 600)
- `poll_interval` (optional): Seconds between checks (default: 5)

**Use Cases:**
- Comprehensive market research
- Competitive analysis with structured data
- Lead generation with enrichment
- Automated data collection for reports

## Workflows

This package includes deployable workflows that can be run as API services using `llamactl`.

### Running Locally

```bash
# Install llamactl
uv tool install llamactl

# Serve the workflows
cd llamaindex-anakin
llamactl serve
```

This starts an API server at `http://localhost:4501` with three workflow endpoints:

#### 1. Scrape Workflow

```bash
curl -X POST http://localhost:4501/deployments/llamaindex-anakin/workflows/scrape/run \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "country": "us",
    "force_fresh": false
  }'
```

#### 2. Search Workflow

```bash
curl -X POST http://localhost:4501/deployments/llamaindex-anakin/workflows/search/run \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the latest AI trends?",
    "max_results": 5
  }'
```

#### 3. Agentic Search Workflow

```bash
curl -X POST http://localhost:4501/deployments/llamaindex-anakin/workflows/agentic-search/run \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Find pricing for top 5 CRM tools",
    "use_browser": true
  }'
```

### Deploying to LlamaCloud

```bash
# Create a git repository
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-org/llamaindex-anakin
git push -u origin main

# Deploy to LlamaCloud
llamactl deployments create
```

Follow the interactive prompts to configure your deployment. Your workflows will be deployed as scalable API endpoints.

## Advanced Examples

### Example 1: Web Research Agent

```python
from llamaindex_anakin import AnakinSearchTool, AnakinScrapeTool
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI

api_key = "your-anakin-api-key"

# Initialize tools
search_tool = AnakinSearchTool(api_key=api_key).to_tool()
scrape_tool = AnakinScrapeTool(api_key=api_key).to_tool()

# Create agent
llm = OpenAI(model="gpt-4", temperature=0)
agent = ReActAgent.from_tools(
    tools=[search_tool, scrape_tool],
    llm=llm,
    verbose=True,
)

# Run research task
response = agent.chat(
    "Research the top 3 AI companies in 2026 and provide detailed information"
)
```

### Example 2: Custom Workflow

```python
import asyncio
from workflows import Workflow, step, Context
from workflows.events import StartEvent, StopEvent
from llamaindex_anakin import AnakinSearchTool, AnakinScrapeTool

class ResearchWorkflow(Workflow):
    def __init__(self, api_key: str):
        super().__init__()
        self.search_tool = AnakinSearchTool(api_key=api_key)
        self.scrape_tool = AnakinScrapeTool(api_key=api_key)
    
    @step
    async def search(self, event: StartEvent, context: Context):
        # Perform search
        results = self.search_tool._search(event.query)
        # Process and return
        return StopEvent(result=results)

# Run the workflow
workflow = ResearchWorkflow(api_key="your-api-key")
result = asyncio.run(workflow.run(query="AI trends 2026"))
```

## Configuration

### Custom Base URL

If you're using a self-hosted or custom Anakin API endpoint:

```python
from llamaindex_anakin import AnakinScrapeTool

tool = AnakinScrapeTool(
    api_key="your-api-key",
    base_url="https://your-custom-api.com",
)
```

### Tool Timeouts and Polling

Adjust timeouts for long-running operations:

```python
# For scraping
result = scrape_tool._scrape(
    url="https://example.com",
    max_wait_time=600,  # 10 minutes
    poll_interval=5,    # Check every 5 seconds
)

# For agentic search
result = agentic_tool._agentic_search(
    prompt="Research prompt",
    max_wait_time=900,   # 15 minutes
    poll_interval=10,    # Check every 10 seconds
)
```

## Examples

See the `examples/` directory for complete working examples:

- `basic_scraping.py` - Basic web scraping
- `ai_search.py` - AI-powered search
- `agentic_search.py` - Advanced agentic search
- `llamaindex_agent.py` - Using tools with LlamaIndex agents
- `custom_workflow.py` - Creating custom workflows

Run examples:

```bash
cd examples
python basic_scraping.py
python ai_search.py
python llamaindex_agent.py
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/Anakin-Inc/llamaindex-anakin.git
cd llamaindex-anakin

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Code Formatting

```bash
# Format code
hatch run format

# Lint code
hatch run lint

# Type check
hatch run typecheck

# Run all checks
hatch run all-check
```

## API Reference

### AnakinScrapeTool

```python
class AnakinScrapeTool:
    """Tool for scraping websites using the Anakin API."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.anakin.io"
    )
    
    def to_tool(self) -> FunctionTool:
        """Convert to LlamaIndex FunctionTool."""
```

### AnakinSearchTool

```python
class AnakinSearchTool:
    """Tool for AI-powered searches using the Anakin API."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.anakin.io"
    )
    
    def to_tool(self) -> FunctionTool:
        """Convert to LlamaIndex FunctionTool."""
```

### AnakinAgenticSearchTool

```python
class AnakinAgenticSearchTool:
    """Tool for advanced agentic searches using the Anakin API."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.anakin.io"
    )
    
    def to_tool(self) -> FunctionTool:
        """Convert to LlamaIndex FunctionTool."""
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

- 📖 [API Documentation](https://anakin.io/docs)
- 💬 [Community Forum](https://community.anakin.io)
- 🐛 [Report Issues](https://github.com/Anakin-Inc/llamaindex-anakin/issues)
- 📧 Email: anakin@anakininc.com

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [langchain-anakin](https://github.com/Anakin-Inc/langchain-anakin) - LangChain integration
- [n8n-nodes-anakin-scraper](https://github.com/Anakin-Inc/n8n-nodes-anakin-scraper) - n8n integration
- [Anakin API](https://anakin.io) - Official API documentation

## Changelog

### 0.1.0 (2026-01-30)

- Initial release
- Added `AnakinScrapeTool` for web scraping
- Added `AnakinSearchTool` for AI-powered search
- Added `AnakinAgenticSearchTool` for agentic research
- Added three deployable workflows (scrape, search, agentic-search)
- Full LlamaIndex integration with FunctionTool
- `llamactl` deployment support
- Comprehensive documentation and examples
