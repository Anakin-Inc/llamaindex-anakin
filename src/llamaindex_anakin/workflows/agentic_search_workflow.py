"""Anakin agentic search workflow for LlamaIndex."""

from workflows import Workflow, step, Context
from workflows.events import StartEvent, StopEvent, Event
from pydantic import Field

from llamaindex_anakin.client import AnakinAPIClient


class AgenticSearchStartEvent(StartEvent):
    """Start event for agentic search workflow."""

    api_key: str = Field(description="Anakin API key")
    prompt: str = Field(description="The research prompt or question")
    use_browser: bool = Field(
        default=True, description="Whether to use browser for scraping"
    )
    max_wait_time: int = Field(
        default=600, description="Maximum seconds to wait for completion"
    )
    poll_interval: int = Field(
        default=5, description="Seconds between status checks"
    )


class AgenticSearchProgressEvent(Event):
    """Progress event for agentic search workflow."""

    message: str


class AnakinAgenticSearchWorkflow(Workflow):
    """Workflow for advanced agentic searches using the Anakin API.
    
    Users must provide their own Anakin API key in the request.
    """

    @step
    async def agentic_search(
        self, event: AgenticSearchStartEvent, context: Context
    ) -> StopEvent:
        """Execute the agentic search operation.

        Args:
            event: The start event containing search parameters
            context: The workflow context

        Returns:
            StopEvent with the search result
        """
        context.write_event_to_stream(
            AgenticSearchProgressEvent(
                message=f"Starting agentic search for: {event.prompt}"
            )
        )

        try:
            # Create client with user's API key
            client = AnakinAPIClient(api_key=event.api_key)
            
            result = client.agentic_search(
                prompt=event.prompt,
                use_browser=event.use_browser,
                max_wait_time=event.max_wait_time,
                poll_interval=event.poll_interval,
            )

            context.write_event_to_stream(
                AgenticSearchProgressEvent(message="Agentic search completed successfully")
            )

            return StopEvent(result=result)

        except Exception as e:
            context.write_event_to_stream(
                AgenticSearchProgressEvent(message=f"Error: {str(e)}")
            )
            return StopEvent(
                result={
                    "success": False,
                    "error": str(e),
                    "operation": "agenticSearch",
                }
            )


# Create the workflow instance
agentic_search_workflow = AnakinAgenticSearchWorkflow(timeout=900)
