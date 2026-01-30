"""Anakin URL scraping workflow for LlamaIndex."""

from workflows import Workflow, step, Context
from workflows.events import StartEvent, StopEvent, Event
from pydantic import Field

from llamaindex_anakin.client import AnakinAPIClient


class ScrapeStartEvent(StartEvent):
    """Start event for scraping workflow."""

    api_key: str = Field(description="Anakin API key")
    url: str = Field(description="The URL to scrape")
    country: str = Field(default="us", description="Country code for proxy routing")
    force_fresh: bool = Field(default=False, description="Whether to bypass cache")
    max_wait_time: int = Field(default=300, description="Maximum seconds to wait")
    poll_interval: int = Field(default=3, description="Seconds between checks")


class ScrapeProgressEvent(Event):
    """Progress event for scraping workflow."""

    message: str


class AnakinScrapeWorkflow(Workflow):
    """Workflow for scraping websites using the Anakin API.
    
    Users must provide their own Anakin API key in the request.
    """

    @step
    async def scrape(self, event: ScrapeStartEvent, context: Context) -> StopEvent:
        """Execute the URL scraping operation.

        Args:
            event: The start event containing scraping parameters
            context: The workflow context

        Returns:
            StopEvent with the scraping result
        """
        context.write_event_to_stream(
            ScrapeProgressEvent(message=f"Starting to scrape: {event.url}")
        )

        try:
            # Create client with user's API key
            client = AnakinAPIClient(api_key=event.api_key)
            
            result = client.scrape_url(
                url=event.url,
                country=event.country,
                force_fresh=event.force_fresh,
                max_wait_time=event.max_wait_time,
                poll_interval=event.poll_interval,
            )

            context.write_event_to_stream(
                ScrapeProgressEvent(message="Scraping completed successfully")
            )

            return StopEvent(result=result)

        except Exception as e:
            context.write_event_to_stream(
                ScrapeProgressEvent(message=f"Error: {str(e)}")
            )
            return StopEvent(
                result={"success": False, "error": str(e), "operation": "scrapeUrl"}
            )


# Create the workflow instance
scrape_workflow = AnakinScrapeWorkflow(timeout=600)
