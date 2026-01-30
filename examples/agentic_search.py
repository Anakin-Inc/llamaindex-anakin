"""Example of using the Anakin Agentic Search Tool with LlamaIndex."""

import os
from dotenv import load_dotenv
from llamaindex_anakin import AnakinAgenticSearchTool

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("ANAKIN_API_KEY")
if not api_key:
    raise ValueError("Please set ANAKIN_API_KEY environment variable")

# Initialize the agentic search tool
agentic_tool = AnakinAgenticSearchTool(api_key=api_key)

# Convert to LlamaIndex FunctionTool
tool = agentic_tool.to_tool()

# Example 1: Market research
print("Example 1: Comprehensive market research...")
result = tool.call(
    prompt="Find pricing information for the top 5 project management tools"
)
print(result)
print("\n" + "=" * 80 + "\n")

# Example 2: Competitive analysis
print("Example 2: Competitive analysis with structured data...")
result = tool.call(
    prompt="Compare features and pricing of Salesforce, HubSpot, and Zoho CRM",
    use_browser=True,
)
print(result)
print("\n" + "=" * 80 + "\n")

print("✓ Agentic search examples completed!")
