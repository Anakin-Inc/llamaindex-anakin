# LlamaIndex Anakin Quick Start

Get started with llamaindex-anakin in 5 minutes!

## Step 1: Installation

```bash
pip install llamaindex-anakin
```

## Step 2: Get API Key

1. Sign up at [anakin.io](https://anakin.io)
2. Navigate to API settings
3. Generate a new API key

## Step 3: Set Up Environment

Create a `.env` file:

```bash
ANAKIN_API_KEY=your-anakin-api-key-here
```

## Step 4: Try Your First Tool

### Simple Web Scraping

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

### AI-Powered Search

```python
from llamaindex_anakin import AnakinSearchTool

# Initialize the tool
tool = AnakinSearchTool(api_key="your-api-key")

# Convert to LlamaIndex FunctionTool
llama_tool = tool.to_tool()

# Perform a search
result = llama_tool.call(query="What are the latest AI trends?")
print(result)
```

## Step 5: Use with LlamaIndex Agent

```python
from llamaindex_anakin import AnakinSearchTool, AnakinScrapeTool
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI

# Initialize tools
search_tool = AnakinSearchTool(api_key="your-api-key").to_tool()
scrape_tool = AnakinScrapeTool(api_key="your-api-key").to_tool()

# Create LLM
llm = OpenAI(model="gpt-4", temperature=0)

# Create agent
agent = ReActAgent.from_tools(
    tools=[search_tool, scrape_tool],
    llm=llm,
    verbose=True,
)

# Chat with the agent
response = agent.chat("Find and summarize the latest news on quantum computing")
print(response)
```

## Step 6: Deploy as API Service (Optional)

### Run Locally

```bash
# Install llamactl
uv tool install llamactl

# Serve workflows
llamactl serve
```

Your API is now running at `http://localhost:4501`!

### Test the API

```bash
curl -X POST http://localhost:4501/deployments/llamaindex-anakin/workflows/search/run \
  -H "Content-Type: application/json" \
  -d '{"query": "AI trends 2026", "max_results": 5}'
```

### Deploy to Cloud

```bash
# Create a git repo
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-org/my-anakin-workflows
git push -u origin main

# Deploy to LlamaCloud
llamactl deployments create
```

## Next Steps

- 📖 Read the full [README](README.md)
- 💻 Check out the [examples](examples/)
- 🔧 Explore the [API Reference](README.md#api-reference)
- 🚀 Learn about [Workflows](README.md#workflows)
- 📚 Read the [LlamaIndex documentation](https://docs.llamaindex.ai/)

## Common Issues

### API Key Not Found

Make sure you've set the `ANAKIN_API_KEY` environment variable:

```python
import os
os.environ["ANAKIN_API_KEY"] = "your-api-key"
```

Or load from `.env`:

```python
from dotenv import load_dotenv
load_dotenv()
```

### Import Errors

Make sure you've installed the package:

```bash
pip install llamaindex-anakin
```

### Timeout Errors

For long-running operations, increase the timeout:

```python
result = tool._scrape(
    url="https://example.com",
    max_wait_time=600  # 10 minutes
)
```

## Support

Need help? Contact us:

- 📧 Email: anakin@anakininc.com
- 💬 [Community Forum](https://community.anakin.io)
- 🐛 [GitHub Issues](https://github.com/Anakin-Inc/llamaindex-anakin/issues)

---

Happy building with LlamaIndex and Anakin! 🦙✨
