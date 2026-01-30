"""Anakin AI search workflow for LlamaIndex."""

from workflows import Workflow, step, Context
from workflows.events import StartEvent, StopEvent, Event
from pydantic import Field

from llamaindex_anakin.client import AnakinAPIClient


class SearchStartEvent(StartEvent):
    """Start event for search workflow."""

    api_key: str = Field(description="Anakin API key")
    query: str = Field(description="The search query or question")
    max_results: int = Field(default=5, description="Maximum number of results")


class SearchProgressEvent(Event):
    """Progress event for search workflow."""

    message: str


class AnakinSearchWorkflow(Workflow):
    """Workflow for AI-powered searches using the Anakin API.
    
    Users must provide their own Anakin API key in the request.
    """

    @step
    async def search(self, event: SearchStartEvent, context: Context) -> StopEvent:
        """Execute the AI-powered search operation.

        Args:
            event: The start event containing search parameters
            context: The workflow context

        Returns:
            StopEvent with the search result
        """
        context.write_event_to_stream(
            SearchProgressEvent(message=f"Searching for: {event.query}")
        )

        try:
            # Create client with user's API key
            client = AnakinAPIClient(api_key=event.api_key)
            
            result = client.search(prompt=event.query, limit=event.max_results)

            context.write_event_to_stream(
                SearchProgressEvent(message="Search completed successfully")
            )

            return StopEvent(result=result)

        except Exception as e:
            context.write_event_to_stream(SearchProgressEvent(message=f"Error: {str(e)}"))
            return StopEvent(
                result={"success": False, "error": str(e), "operation": "search"}
            )


# Create the workflow instance
search_workflow = AnakinSearchWorkflow(timeout=60)
