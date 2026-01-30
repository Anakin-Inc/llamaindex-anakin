"""Anakin URL scraping tool for LlamaIndex."""

from typing import Optional
from llama_index.core.tools import FunctionTool

from llamaindex_anakin.client import AnakinAPIClient


class AnakinScrapeTool:
    """Tool for scraping websites using the Anakin API.

    This tool extracts content and structured data from any website.
    It returns HTML, markdown, and automatically extracted JSON data.

    Example:
        ```python
        from llamaindex_anakin import AnakinScrapeTool

        tool = AnakinScrapeTool(api_key="your-api-key")
        result = tool.call(url="https://example.com")
        ```
    """

    def __init__(
        self, api_key: str, base_url: str = "https://api.anakin.io"
    ):
        """Initialize the Anakin scrape tool.

        Args:
            api_key: Anakin API key
            base_url: Base URL for Anakin API (default: https://api.anakin.io)
        """
        self.client = AnakinAPIClient(api_key=api_key, base_url=base_url)

    def _scrape(
        self,
        url: str,
        country: str = "us",
        force_fresh: bool = False,
        max_wait_time: int = 300,
        poll_interval: int = 3,
    ) -> str:
        """Execute the URL scraping operation.

        Args:
            url: The URL to scrape
            country: Country code for proxy routing (default: us)
            force_fresh: Whether to bypass cache (default: False)
            max_wait_time: Maximum seconds to wait (default: 300)
            poll_interval: Seconds between checks (default: 3)

        Returns:
            A formatted string containing the scraped data
        """
        try:
            result = self.client.scrape_url(
                url=url,
                country=country,
                force_fresh=force_fresh,
                max_wait_time=max_wait_time,
                poll_interval=poll_interval,
            )

            # Format the result as a readable string
            output_parts = [
                f"Successfully scraped: {url}",
                f"Status: {result.get('status', 'completed')}",
            ]

            # Add markdown content if available
            if "markdown" in result:
                markdown_preview = result["markdown"][:500]
                output_parts.append(f"\nContent Preview:\n{markdown_preview}...")

            # Add structured data if available
            if "generatedJson" in result and result["generatedJson"]:
                output_parts.append(
                    f"\nStructured Data: {str(result['generatedJson'])[:300]}..."
                )

            return "\n".join(output_parts)

        except Exception as e:
            return f"Error scraping URL: {str(e)}"

    def to_tool(self) -> FunctionTool:
        """Convert to LlamaIndex FunctionTool.

        Returns:
            FunctionTool instance that can be used with LlamaIndex agents
        """
        return FunctionTool.from_defaults(
            fn=self._scrape,
            name="anakin_scrape_url",
            description=(
                "Scrape a website and extract its content including HTML, markdown, and structured data. "
                "Useful for extracting information from web pages, product pages, articles, or any website. "
                "Returns comprehensive data including text content and automatically extracted structured data. "
                "Input should be a valid HTTP/HTTPS URL."
            ),
        )
