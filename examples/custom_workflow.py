"""Example of creating a custom workflow with Anakin tools."""

import os
import asyncio
from dotenv import load_dotenv
from workflows import Workflow, step, Context
from workflows.events import StartEvent, StopEvent, Event
from pydantic import Field

from llamaindex_anakin import AnakinScrapeTool, AnakinSearchTool

# Load environment variables
load_dotenv()


class ResearchStartEvent(StartEvent):
    """Start event for research workflow."""

    topic: str = Field(description="The topic to research")


class SearchCompleteEvent(Event):
    """Event emitted when search is complete."""

    search_results: str


class CustomResearchWorkflow(Workflow):
    """Custom workflow that combines search and scraping."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        api_key = os.getenv("ANAKIN_API_KEY")
        if not api_key:
            raise ValueError("Please set ANAKIN_API_KEY environment variable")

        self.search_tool = AnakinSearchTool(api_key=api_key)
        self.scrape_tool = AnakinScrapeTool(api_key=api_key)

    @step
    async def search_topic(
        self, event: ResearchStartEvent, context: Context
    ) -> SearchCompleteEvent:
        """First step: Search for the topic."""
        print(f"Step 1: Searching for '{event.topic}'...")

        result = self.search_tool._search(query=event.topic, max_results=5)

        return SearchCompleteEvent(search_results=result)

    @step
    async def analyze_results(
        self, event: SearchCompleteEvent, context: Context
    ) -> StopEvent:
        """Second step: Analyze the search results."""
        print("Step 2: Analyzing search results...")

        # In a real workflow, you might extract URLs from search results
        # and scrape them for deeper analysis
        analysis = {
            "search_results": event.search_results,
            "status": "completed",
            "message": "Research workflow completed successfully",
        }

        return StopEvent(result=analysis)


async def main():
    """Run the custom workflow."""
    workflow = CustomResearchWorkflow(timeout=300)

    print("Running custom research workflow...")
    print("=" * 80)

    result = await workflow.run(topic="Latest AI trends in 2026")

    print("\nWorkflow Result:")
    print(result)
    print("=" * 80)
    print("✓ Custom workflow example completed!")


if __name__ == "__main__":
    asyncio.run(main())
