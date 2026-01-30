"""Anakin AI search tool for LlamaIndex."""

from llama_index.core.tools import FunctionTool

from llamaindex_anakin.client import AnakinAPIClient


class AnakinSearchTool:
    """Tool for AI-powered searches using the Anakin API.

    This tool performs AI-powered searches with instant answers and citations,
    similar to Perplexity AI.

    Example:
        ```python
        from llamaindex_anakin import AnakinSearchTool

        tool = AnakinSearchTool(api_key="your-api-key")
        result = tool.call(query="What are the latest AI trends?")
        ```
    """

    def __init__(
        self, api_key: str, base_url: str = "https://api.anakin.io"
    ):
        """Initialize the Anakin search tool.

        Args:
            api_key: Anakin API key
            base_url: Base URL for Anakin API (default: https://api.anakin.io)
        """
        self.client = AnakinAPIClient(api_key=api_key, base_url=base_url)

    def _search(self, query: str, max_results: int = 5) -> str:
        """Execute the AI-powered search operation.

        Args:
            query: The search query or question
            max_results: Maximum number of results to return (default: 5)

        Returns:
            A formatted string containing the search results
        """
        try:
            result = self.client.search(prompt=query, limit=max_results)

            # Format the result as a readable string
            output_parts = [
                f"Search query: {query}",
                f"Status: {'success' if result.get('success') else 'failed'}",
            ]

            # Add answer if available
            if "answer" in result:
                output_parts.append(f"\nAnswer:\n{result['answer']}")

            # Add citations if available
            if "citations" in result and result["citations"]:
                output_parts.append(
                    f"\nCitations: {len(result['citations'])} sources"
                )

            # Add results if available
            if "results" in result and result["results"]:
                output_parts.append(f"\nResults: {len(result['results'])} items")
                for i, res in enumerate(result["results"][:3], 1):
                    title = res.get("title", "No title")
                    output_parts.append(f"  {i}. {title}")

            return "\n".join(output_parts)

        except Exception as e:
            return f"Error performing search: {str(e)}"

    def to_tool(self) -> FunctionTool:
        """Convert to LlamaIndex FunctionTool.

        Returns:
            FunctionTool instance that can be used with LlamaIndex agents
        """
        return FunctionTool.from_defaults(
            fn=self._search,
            name="anakin_ai_search",
            description=(
                "Perform an AI-powered search query using Anakin API. "
                "Similar to Perplexity AI, this provides instant answers with citations. "
                "Useful for research, fact-checking, competitive intelligence, and real-time information gathering. "
                "Returns an answer along with citations and sources."
            ),
        )
