"""Example of using the Anakin AI Search Tool with LlamaIndex."""

import os
from dotenv import load_dotenv
from llamaindex_anakin import AnakinSearchTool

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("ANAKIN_API_KEY")
if not api_key:
    raise ValueError("Please set ANAKIN_API_KEY environment variable")

# Initialize the search tool
search_tool = AnakinSearchTool(api_key=api_key)

# Convert to LlamaIndex FunctionTool
tool = search_tool.to_tool()

# Example 1: Simple search query
print("Example 1: Simple AI search...")
result = tool.call(query="What are the latest developments in quantum computing?")
print(result)
print("\n" + "=" * 80 + "\n")

# Example 2: Search with more results
print("Example 2: Search with more results...")
result = tool.call(query="Best AI tools for developers in 2026", max_results=10)
print(result)
print("\n" + "=" * 80 + "\n")

# Example 3: Fact-checking query
print("Example 3: Fact-checking query...")
result = tool.call(query="What is the current state of GPT-5?")
print(result)
print("\n" + "=" * 80 + "\n")

print("✓ AI search examples completed!")
