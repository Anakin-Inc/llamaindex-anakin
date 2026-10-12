"""Anakin web reader: load pages, crawls, search results and site maps as Documents."""

import logging
from typing import Any, Literal

from anakin import Anakin
from llama_index.core.bridge.pydantic import Field, PrivateAttr
from llama_index.core.readers.base import BasePydanticReader
from llama_index.core.schema import Document

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.anakin.io/v1"
# Anakin's batch scrape takes at most 10 URLs per job.
BATCH_SIZE = 10
# Bookkeeping metadata, kept out of embeddings and LLM prompts.
INTERNAL_METADATA = ["source", "mode", "job_id", "cached", "crawl_url", "site_url"]

Mode = Literal["scrape", "crawl", "search", "map"]


class AnakinWebReader(BasePydanticReader):
    """
    Load web content through Anakin (https://anakin.io) as LlamaIndex Documents.

    Modes:
        scrape: one Document per page, with the page as clean markdown.
            `load_data(url=...)` scrapes one page; `load_data(urls=[...])`
            scrapes many, 10 at a time in parallel.
        crawl: one Document per crawled page of a site.
        search: one Document per web search result (title and snippet).
        map: one Document per URL found on a site.

    `params` are passed to the Anakin SDK call behind the mode: `Anakin.scrape`
    for one URL, `Anakin.scrape_batch` for several, then `crawl`, `search` and
    `map`. For example `{"use_browser": True}` for JavaScript-heavy pages, or
    `{"max_pages": 50, "include_patterns": ["/docs/*"]}` for a crawl.

    Scraped and crawled pages use their URL as the Document ID, so re-loading
    a page updates it in an ingestion pipeline instead of duplicating it.
    """

    is_remote: bool = True
    api_key: str | None = Field(default=None, exclude=True)
    base_url: str = DEFAULT_BASE_URL
    mode: Mode = "scrape"
    params: dict[str, Any] = Field(default_factory=dict)

    _client: Anakin = PrivateAttr()

    def __init__(
        self,
        api_key: str | None = None,
        mode: Mode = "scrape",
        params: dict[str, Any] | None = None,
        base_url: str = DEFAULT_BASE_URL,
        client: Anakin | None = None,
    ) -> None:
        """
        Args:
            api_key: Anakin API key. Defaults to the ANAKIN_API_KEY environment variable.
            mode: "scrape", "crawl", "search" or "map".
            params: Extra arguments for the Anakin call behind the mode.
            base_url: Anakin API base URL.
            client: An existing `anakin.Anakin` client to use instead.
        """
        super().__init__(api_key=api_key, mode=mode, params=params or {}, base_url=base_url)
        self._client = client or Anakin(api_key=api_key, base_url=base_url)

    @classmethod
    def class_name(cls) -> str:
        return "AnakinWebReader"

    def load_data(
        self,
        url: str | None = None,
        urls: list[str] | None = None,
        query: str | None = None,
    ) -> list[Document]:
        """
        Load Documents for the reader's mode.

        Args:
            url: The page (scrape) or site (crawl, map) to load.
            urls: Several pages to scrape. Pages that fail are logged and skipped.
            query: The search query (search mode).
        """
        if self.mode == "scrape":
            if url and urls:
                raise ValueError("Pass url or urls, not both.")
            if url:
                return [self._scrape(url)]
            if urls:
                return self._scrape_many(urls)
            raise ValueError("scrape mode needs url or urls.")
        if self.mode == "crawl":
            return self._crawl(_require(url, "crawl mode needs url."))
        if self.mode == "search":
            return self._search(_require(query, "search mode needs query."))
        if self.mode == "map":
            return self._map(_require(url, "map mode needs url."))
        raise ValueError(f'Unknown mode "{self.mode}": use scrape, crawl, search or map.')

    def _scrape(self, url: str) -> Document:
        page = self._client.scrape(url, **self.params)
        return _page(
            page.markdown or "",
            page.url or url,
            mode="scrape",
            job_id=page.id,
            cached=page.cached,
        )

    def _scrape_many(self, urls: list[str]) -> list[Document]:
        docs = []
        for start in range(0, len(urls), BATCH_SIZE):
            batch = self._client.scrape_batch(urls[start : start + BATCH_SIZE], **self.params)
            for item in sorted(batch.results, key=lambda item: item.index):
                if item.status == "completed" and item.markdown:
                    docs.append(
                        _page(
                            item.markdown,
                            item.url,
                            mode="scrape",
                            job_id=item.id or batch.id,
                            cached=item.cached,
                        )
                    )
                else:
                    _log_skipped(item.url, item.status, item.error, job_id=batch.id)
        return docs

    def _crawl(self, url: str) -> list[Document]:
        result = self._client.crawl(url, **self.params)
        docs = []
        for page in result.pages:
            if page.status == "completed" and page.markdown:
                docs.append(
                    _page(page.markdown, page.url, mode="crawl", job_id=result.id, crawl_url=url)
                )
            else:
                _log_skipped(page.url, page.status, page.error, job_id=result.id)
        return docs

    def _search(self, query: str) -> list[Document]:
        result = self._client.search(query, **self.params)
        return [
            Document(
                text="\n\n".join(part for part in (item.title, item.snippet) if part),
                metadata={
                    "source": "anakin",
                    "mode": "search",
                    "url": item.url,
                    "title": item.title,
                    "date": item.date,
                    "query": query,
                    "job_id": result.id,
                },
                excluded_embed_metadata_keys=INTERNAL_METADATA,
                excluded_llm_metadata_keys=INTERNAL_METADATA,
            )
            for item in result.results
        ]

    def _map(self, url: str) -> list[Document]:
        result = self._client.map(url, **self.params)
        return [
            Document(
                text=link,
                metadata={
                    "source": "anakin",
                    "mode": "map",
                    "url": link,
                    "site_url": url,
                    "job_id": result.id,
                },
                excluded_embed_metadata_keys=INTERNAL_METADATA,
                excluded_llm_metadata_keys=INTERNAL_METADATA,
            )
            for link in result.links
        ]


def _page(text: str, url: str, *, mode: str, **metadata: Any) -> Document:
    """A Document for one page's content, keyed by its URL."""
    return Document(
        id_=url,
        text=text,
        metadata={"source": "anakin", "mode": mode, "url": url, **metadata},
        excluded_embed_metadata_keys=INTERNAL_METADATA,
        excluded_llm_metadata_keys=INTERNAL_METADATA,
    )


def _log_skipped(url: str, status: str, error: str | None, *, job_id: str) -> None:
    logger.warning(
        "Anakin skipped %s (status=%s, job_id=%s): %s",
        url,
        status,
        job_id,
        error or "no content",
    )


def _require(value: str | None, message: str) -> str:
    if not value:
        raise ValueError(message)
    return value
