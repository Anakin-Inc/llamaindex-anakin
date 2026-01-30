"""Basic example of using the Anakin Scrape Tool with LlamaIndex."""

import os
from dotenv import load_dotenv
from llamaindex_anakin import AnakinScrapeTool

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("ANAKIN_API_KEY")
if not api_key:
    raise ValueError("Please set ANAKIN_API_KEY environment variable")

# Initialize the scrape tool
scrape_tool = AnakinScrapeTool(api_key=api_key)

# Convert to LlamaIndex FunctionTool
tool = scrape_tool.to_tool()

# Example 1: Scrape a website
print("Example 1: Scraping a website...")
result = tool.call(url="https://example.com")
print(result)
print("\n" + "=" * 80 + "\n")

# Example 2: Scrape with custom parameters
print("Example 2: Scraping with custom parameters...")
result = tool.call(
    url="https://news.ycombinator.com", country="us", force_fresh=True
)
print(result)
print("\n" + "=" * 80 + "\n")

print("✓ Scraping examples completed!")
