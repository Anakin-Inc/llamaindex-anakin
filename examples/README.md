# LlamaIndex Anakin Examples

This directory contains examples demonstrating how to use the Anakin integration with LlamaIndex.

## Prerequisites

1. Set up your environment variables:
   ```bash
   cp ../.env.template ../.env
   ```

2. Add your API keys to `.env`:
   ```
   ANAKIN_API_KEY=your-anakin-api-key
   OPENAI_API_KEY=your-openai-api-key  # Only needed for agent examples
   ```

3. Install the package:
   ```bash
   cd ..
   pip install -e .
   ```

## Examples

### 1. Basic Scraping (`basic_scraping.py`)
Demonstrates basic web scraping using the Anakin Scrape Tool.

```bash
python examples/basic_scraping.py
```

### 2. AI Search (`ai_search.py`)
Shows how to perform AI-powered searches using the Anakin Search Tool.

```bash
python examples/ai_search.py
```

### 3. Agentic Search (`agentic_search.py`)
Demonstrates advanced agentic search with automatic scraping and data extraction.

```bash
python examples/agentic_search.py
```

### 4. LlamaIndex Agent (`llamaindex_agent.py`)
Shows how to use Anakin tools with a LlamaIndex ReAct agent.

**Requires OpenAI API key.**

```bash
python examples/llamaindex_agent.py
```

### 5. Custom Workflow (`custom_workflow.py`)
Demonstrates creating a custom workflow that combines multiple Anakin tools.

```bash
python examples/custom_workflow.py
```

## Running Workflows as a Server

You can also run the workflows as an API server using `llamactl`:

```bash
cd ..
llamactl serve
```

This will start an API server where you can invoke the workflows via HTTP:

- Scrape workflow: `POST /deployments/llamaindex-anakin/workflows/scrape/run`
- Search workflow: `POST /deployments/llamaindex-anakin/workflows/search/run`
- Agentic search workflow: `POST /deployments/llamaindex-anakin/workflows/agentic-search/run`

Example request:
```bash
curl -X POST http://localhost:4501/deployments/llamaindex-anakin/workflows/search/run \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the latest AI trends?", "max_results": 5}'
```

## Notes

- All examples require an Anakin API key from [anakin.io](https://anakin.io)
- Agent examples require an OpenAI API key
- Some operations may take time to complete due to scraping and processing
- Check the individual example files for more detailed comments
