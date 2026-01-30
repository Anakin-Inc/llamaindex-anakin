"""Example of using Anakin tools with a LlamaIndex agent."""

import os
from dotenv import load_dotenv
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llamaindex_anakin import AnakinScrapeTool, AnakinSearchTool, AnakinAgenticSearchTool

# Load environment variables
load_dotenv()

# Get API keys from environment
anakin_api_key = os.getenv("ANAKIN_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

if not anakin_api_key:
    raise ValueError("Please set ANAKIN_API_KEY environment variable")
if not openai_api_key:
    raise ValueError("Please set OPENAI_API_KEY environment variable")

# Initialize Anakin tools
scrape_tool = AnakinScrapeTool(api_key=anakin_api_key).to_tool()
search_tool = AnakinSearchTool(api_key=anakin_api_key).to_tool()
agentic_tool = AnakinAgenticSearchTool(api_key=anakin_api_key).to_tool()

# Initialize LLM
llm = OpenAI(model="gpt-4", api_key=openai_api_key, temperature=0)

# Create ReAct agent with all Anakin tools
agent = ReActAgent.from_tools(
    tools=[scrape_tool, search_tool, agentic_tool],
    llm=llm,
    verbose=True,
)

# Example 1: Research task
print("Example 1: Research the top 3 AI companies in 2026...")
response = agent.chat(
    "Research the top 3 AI companies in 2026 and provide detailed information about each, "
    "including their main products and market position."
)
print(response)
print("\n" + "=" * 80 + "\n")

# Example 2: Data collection task
print("Example 2: Collect pricing data...")
response = agent.chat(
    "Find and compare the pricing tiers of GitHub, GitLab, and Bitbucket. "
    "Provide a structured comparison."
)
print(response)
print("\n" + "=" * 80 + "\n")

# Example 3: Scraping and analysis
print("Example 3: Scrape and analyze...")
response = agent.chat(
    "Scrape the Hacker News homepage and search for more information about "
    "the top 3 trending topics."
)
print(response)
print("\n" + "=" * 80 + "\n")

print("✓ LlamaIndex agent examples completed!")
