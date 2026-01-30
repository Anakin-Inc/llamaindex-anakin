"""Anakin agentic search tool for LlamaIndex."""

from llama_index.core.tools import FunctionTool

from llamaindex_anakin.client import AnakinAPIClient


class AnakinAgenticSearchTool:
    """Tool for advanced agentic searches using the Anakin API.

    This tool performs multi-stage AI pipeline that automatically searches,
    scrapes, and extracts structured data.

    Example:
        ```python
        from llamaindex_anakin import AnakinAgenticSearchTool

        tool = AnakinAgenticSearchTool(api_key="your-api-key")
        result = tool.call(prompt="Find pricing for top 5 CRM tools")
        ```
    """

    def __init__(
        self, api_key: str, base_url: str = "https://api.anakin.io"
    ):
        """Initialize the Anakin agentic search tool.

        Args:
            api_key: Anakin API key
            base_url: Base URL for Anakin API (default: https://api.anakin.io)
        """
        self.client = AnakinAPIClient(api_key=api_key, base_url=base_url)

    def _agentic_search(
        self,
        prompt: str,
        use_browser: bool = True,
        max_wait_time: int = 600,
        poll_interval: int = 5,
    ) -> str:
        """Execute the agentic search operation.

        Args:
            prompt: The research prompt or question
            use_browser: Whether to use browser for scraping (default: True)
            max_wait_time: Maximum seconds to wait (default: 600)
            poll_interval: Seconds between checks (default: 5)

        Returns:
            A formatted string containing the search results
        """
        try:
            result = self.client.agentic_search(
                prompt=prompt,
                use_browser=use_browser,
                max_wait_time=max_wait_time,
                poll_interval=poll_interval,
            )

            # Format the result as a readable string
            output_parts = [
                f"Agentic search completed for: {prompt}",
                f"Status: {result.get('status', 'completed')}",
            ]

            # Add search results if available
            if "searchResults" in result and result["searchResults"]:
                output_parts.append(
                    f"\nSearch Results: {len(result['searchResults'])} items"
                )

            # Add extracted data if available
            if "extractedData" in result and result["extractedData"]:
                output_parts.append(
                    f"\nExtracted Data: {str(result['extractedData'])[:500]}..."
                )

            # Add scraped content if available
            if "scrapedContent" in result and result["scrapedContent"]:
                output_parts.append(
                    f"\nScraped {len(result['scrapedContent'])} pages"
                )

            return "\n".join(output_parts)

        except Exception as e:
            return f"Error performing agentic search: {str(e)}"

    def to_tool(self) -> FunctionTool:
        """Convert to LlamaIndex FunctionTool.

        Returns:
            FunctionTool instance that can be used with LlamaIndex agents
        """
        return FunctionTool.from_defaults(
            fn=self._agentic_search,
            name="anakin_agentic_search",
            description=(
                "Perform an advanced agentic search with automatic scraping and data extraction. "
                "This multi-stage AI pipeline automatically searches the web, scrapes relevant pages, "
                "and extracts structured data. Useful for comprehensive market research, competitive analysis, "
                "lead generation with enrichment, and automated data collection for reports. "
                "Input should be a research prompt or question."
            ),
        )
