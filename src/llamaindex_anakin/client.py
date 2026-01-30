"""Anakin API client for making requests to the Anakin API."""

import time
from typing import Any, Dict, Optional
import requests


class AnakinAPIClient:
    """Client for interacting with the Anakin API."""

    def __init__(self, api_key: str, base_url: str = "https://api.anakin.io"):
        """Initialize the Anakin API client.

        Args:
            api_key: Your Anakin API authentication token
            base_url: The base URL of the Anakin API (default: https://api.anakin.io)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request to the Anakin API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data (optional)

        Returns:
            JSON response from the API

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.request(
            method=method, url=url, headers=self.headers, json=data, timeout=30
        )
        response.raise_for_status()
        return response.json()

    def scrape_url(
        self,
        url: str,
        country: str = "us",
        force_fresh: bool = False,
        max_wait_time: int = 300,
        poll_interval: int = 3,
    ) -> Dict[str, Any]:
        """Scrape a URL and return the extracted content.

        This operation is asynchronous and will poll for completion.

        Args:
            url: The URL to scrape
            country: Country code for proxy routing (default: us)
            force_fresh: Whether to bypass cache (default: False)
            max_wait_time: Maximum seconds to wait for completion (default: 300)
            poll_interval: Seconds between status checks (default: 3)

        Returns:
            Dictionary containing scraped data including HTML, markdown, and extracted JSON

        Raises:
            TimeoutError: If the job doesn't complete within max_wait_time
            ValueError: If the job fails
        """
        # Submit the scraping job
        submit_response = self._make_request(
            "POST",
            "/v1/request",
            {
                "job_type": "url_scraper",
                "url": url,
                "country": country,
                "force_fresh": force_fresh,
            },
        )

        job_id = submit_response.get("jobId")
        if not job_id:
            raise ValueError("No job ID received from API")

        # Poll for completion
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            status_response = self._make_request("GET", f"/v1/request/{job_id}")
            status = status_response.get("status")

            if status in ["completed", "success"]:
                return {
                    "success": True,
                    "operation": "scrapeUrl",
                    "request_id": job_id,
                    "url": url,
                    **status_response,
                }

            if status in ["failed", "error"]:
                error_msg = (
                    status_response.get("error")
                    or status_response.get("error_message")
                    or "Unknown error occurred"
                )
                raise ValueError(f"Scraping job failed: {error_msg}")

            time.sleep(poll_interval)

        raise TimeoutError(
            f"Job did not complete within {max_wait_time} seconds. Last status: {status_response.get('status')}"
        )

    def search(self, prompt: str, limit: int = 5) -> Dict[str, Any]:
        """Perform an AI-powered search query.

        This operation is synchronous and returns immediately.

        Args:
            prompt: The search query or question to ask
            limit: Maximum number of results to return (default: 5)

        Returns:
            Dictionary containing search results with answer and citations

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._make_request(
            "POST", "/v1/search", {"prompt": prompt, "limit": limit}
        )

        return {
            "success": True,
            "operation": "search",
            "query": prompt,
            **response,
        }

    def agentic_search(
        self,
        prompt: str,
        use_browser: bool = True,
        max_wait_time: int = 600,
        poll_interval: int = 5,
    ) -> Dict[str, Any]:
        """Perform an advanced agentic search with automatic scraping and data extraction.

        This operation is asynchronous and will poll for completion.

        Args:
            prompt: The search prompt for agentic analysis
            use_browser: Whether to use browser for scraping (default: True)
            max_wait_time: Maximum seconds to wait for completion (default: 600)
            poll_interval: Seconds between status checks (default: 5)

        Returns:
            Dictionary containing search results, scraped data, and structured extraction

        Raises:
            TimeoutError: If the job doesn't complete within max_wait_time
            ValueError: If the job fails
        """
        # Submit the agentic search job
        submit_response = self._make_request(
            "POST",
            "/v1/agentic-search",
            {"prompt": prompt, "useBrowser": use_browser},
        )

        job_id = submit_response.get("job_id") or submit_response.get("jobId")
        if not job_id:
            raise ValueError("No job ID received from API")

        # Poll for completion
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            status_response = self._make_request(
                "GET", f"/v1/agentic-search/{job_id}"
            )
            status = status_response.get("status")

            if status == "completed":
                return {
                    "success": True,
                    "operation": "agenticSearch",
                    "job_id": job_id,
                    "prompt": prompt,
                    **status_response,
                }

            if status in ["failed", "error"]:
                error_msg = (
                    status_response.get("message")
                    or status_response.get("error")
                    or "Unknown error occurred"
                )
                raise ValueError(f"Agentic search failed: {error_msg}")

            time.sleep(poll_interval)

        raise TimeoutError(
            f"Agentic search did not complete within {max_wait_time} seconds. Last status: {status_response.get('status')}"
        )
